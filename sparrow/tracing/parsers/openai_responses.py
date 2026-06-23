from __future__ import annotations

import json
from typing import Optional

from sparrow.tracing.parsers.base import TokenUsage

_EMPTY_USAGE: TokenUsage = {
    "prompt_tokens": None,
    "completion_tokens": None,
    "total_tokens": None,
}


class OpenAIResponsesParser:
    def extract_model_name(self, request_body: Optional[str]) -> Optional[str]:
        if not request_body:
            return None
        try:
            data = json.loads(request_body)
            return data.get("model")
        except (json.JSONDecodeError, AttributeError):
            return None

    def extract_token_usage(self, response_body: Optional[str]) -> TokenUsage:
        if not response_body:
            return _EMPTY_USAGE
        try:
            data = json.loads(response_body)
            usage = data.get("usage", {})
            if not usage:
                return _EMPTY_USAGE
            return _map_usage(usage)
        except (json.JSONDecodeError, AttributeError):
            return _EMPTY_USAGE

    def extract_token_usage_from_sse(self, accumulated_chunks: str) -> TokenUsage:
        if not accumulated_chunks:
            return _EMPTY_USAGE

        for line in accumulated_chunks.split("\n"):
            line = line.strip()
            if not line.startswith("data: "):
                continue
            data_str = line[6:].strip()
            if data_str == "[DONE]":
                continue
            try:
                data = json.loads(data_str)
            except json.JSONDecodeError:
                continue

            if data.get("type") == "response.completed":
                resp = data.get("response", {})
                usage = resp.get("usage", {})
                if usage:
                    return _map_usage(usage)

        return _EMPTY_USAGE


def _map_usage(usage: dict) -> TokenUsage:
    prompt = usage.get("input_tokens")
    completion = usage.get("output_tokens")
    total = usage.get("total_tokens")
    if total is None and prompt is not None and completion is not None:
        total = prompt + completion
    return {
        "prompt_tokens": prompt,
        "completion_tokens": completion,
        "total_tokens": total,
    }
