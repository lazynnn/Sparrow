from __future__ import annotations

import json
from typing import Optional

from sparrow.tracing.parsers.base import TokenUsage

_EMPTY_USAGE: TokenUsage = {
    "prompt_tokens": None,
    "completion_tokens": None,
    "total_tokens": None,
}


class AnthropicMessagesParser:
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

        input_tokens: Optional[int] = None
        output_tokens: Optional[int] = None

        current_event: Optional[str] = None

        for line in accumulated_chunks.split("\n"):
            line = line.strip()
            if not line:
                current_event = None
                continue

            if line.startswith("event: "):
                current_event = line[7:].strip()
                continue

            if not line.startswith("data: "):
                current_event = None
                continue

            data_str = line[6:].strip()
            if data_str == "[DONE]":
                continue

            try:
                data = json.loads(data_str)
            except json.JSONDecodeError:
                current_event = None
                continue

            evt_type = current_event or data.get("type")

            if evt_type == "message_start":
                msg = data.get("message", {})
                usage = msg.get("usage", {})
                if usage and usage.get("input_tokens") is not None:
                    input_tokens = usage["input_tokens"]

            elif evt_type == "message_delta":
                usage = data.get("usage", {})
                if usage and usage.get("output_tokens") is not None:
                    output_tokens = usage["output_tokens"]

            current_event = None

        if input_tokens is None and output_tokens is None:
            return _EMPTY_USAGE

        total = None
        if input_tokens is not None and output_tokens is not None:
            total = input_tokens + output_tokens

        return {
            "prompt_tokens": input_tokens,
            "completion_tokens": output_tokens,
            "total_tokens": total,
        }


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
