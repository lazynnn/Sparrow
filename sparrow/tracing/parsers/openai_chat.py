from __future__ import annotations

import json
from typing import Optional

from sparrow.tracing.parsers.base import TokenUsage

_EMPTY_USAGE: TokenUsage = {
    "prompt_tokens": None,
    "completion_tokens": None,
    "total_tokens": None,
}


class OpenAIChatParser:
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
            return {
                "prompt_tokens": usage.get("prompt_tokens"),
                "completion_tokens": usage.get("completion_tokens"),
                "total_tokens": usage.get("total_tokens"),
            }
        except (json.JSONDecodeError, AttributeError):
            return _EMPTY_USAGE

    def extract_token_usage_from_sse(self, accumulated_chunks: str) -> TokenUsage:
        if not accumulated_chunks:
            return _EMPTY_USAGE

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

        return _EMPTY_USAGE
