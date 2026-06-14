from __future__ import annotations

import json
import time
from typing import Any, Optional

from sparrow.config import AppConfig, ModelPricing
from sparrow.database import Database
from sparrow.models import Trace, truncate_body
from sparrow.tracing.cost import calculate_cost


def extract_model_name(request_body: Optional[str]) -> Optional[str]:
    if not request_body:
        return None
    try:
        data = json.loads(request_body)
        return data.get("model")
    except (json.JSONDecodeError, AttributeError):
        return None


def extract_token_usage(response_body: Optional[str]) -> dict[str, Optional[int]]:
    if not response_body:
        return {"prompt_tokens": None, "completion_tokens": None, "total_tokens": None}
    try:
        data = json.loads(response_body)
        usage = data.get("usage", {})
        return {
            "prompt_tokens": usage.get("prompt_tokens"),
            "completion_tokens": usage.get("completion_tokens"),
            "total_tokens": usage.get("total_tokens"),
        }
    except (json.JSONDecodeError, AttributeError):
        return {"prompt_tokens": None, "completion_tokens": None, "total_tokens": None}


def extract_token_usage_from_sse(
    accumulated_chunks: str,
) -> dict[str, Optional[int]]:
    if not accumulated_chunks:
        return {"prompt_tokens": None, "completion_tokens": None, "total_tokens": None}

    for line in reversed(accumulated_chunks.split("\n")):
        line = line.strip()
        if not line.startswith("data: "):
            continue
        data_str = line[6:].strip()
        if data_str == "[DONE]":
            continue
        try:
            data = json.loads(data_str)
            usage = data.get("usage")
            if usage:
                return {
                    "prompt_tokens": usage.get("prompt_tokens"),
                    "completion_tokens": usage.get("completion_tokens"),
                    "total_tokens": usage.get("total_tokens"),
                }
        except json.JSONDecodeError:
            continue

    return {"prompt_tokens": None, "completion_tokens": None, "total_tokens": None}


async def save_trace(
    db: Database,
    config: AppConfig,
    request_method: str,
    request_path: str,
    request_headers: Optional[str],
    request_body: Optional[str],
    response_status: Optional[int],
    response_headers: Optional[str],
    response_body: Optional[str],
    duration_ms: Optional[float],
    ttfb_ms: Optional[float],
    is_streaming: bool,
    status: str,
    target_url: Optional[str] = None,
) -> None:
    max_bytes = config.storage.max_body_bytes

    model_name = extract_model_name(request_body)

    if is_streaming:
        tokens = extract_token_usage_from_sse(response_body or "")
    else:
        tokens = extract_token_usage(response_body)

    cost = calculate_cost(
        tokens["prompt_tokens"],
        tokens["completion_tokens"],
        model_name,
        config.pricing,
    )

    trace = Trace(
        request_method=request_method,
        request_path=request_path,
        request_headers=truncate_body(request_headers, max_bytes),
        request_body=truncate_body(request_body, max_bytes),
        response_status=response_status,
        response_headers=truncate_body(response_headers, max_bytes),
        response_body=truncate_body(response_body, max_bytes),
        duration_ms=duration_ms,
        ttfb_ms=ttfb_ms,
        model_name=model_name,
        prompt_tokens=tokens["prompt_tokens"],
        completion_tokens=tokens["completion_tokens"],
        total_tokens=tokens["total_tokens"],
        cost=cost,
        status=status,
        is_streaming=is_streaming,
        target_url=target_url,
    )

    async with db.session() as session:
        session.add(trace)
        await session.commit()
        await session.refresh(trace)

    try:
        from sparrow.api.routes import notify_new_trace

        trace_data = {
            "id": trace.id,
            "timestamp": trace.timestamp.isoformat() if trace.timestamp else None,
            "request_method": trace.request_method,
            "request_path": trace.request_path,
            "response_status": trace.response_status,
            "model_name": trace.model_name,
            "duration_ms": trace.duration_ms,
            "ttfb_ms": trace.ttfb_ms,
            "prompt_tokens": trace.prompt_tokens,
            "completion_tokens": trace.completion_tokens,
            "total_tokens": trace.total_tokens,
            "cost": trace.cost,
            "status": trace.status,
            "is_streaming": trace.is_streaming,
        }
        await notify_new_trace(trace_data)
    except Exception:
        pass
