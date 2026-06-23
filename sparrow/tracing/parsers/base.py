from __future__ import annotations

from typing import Optional, Protocol, TypedDict, runtime_checkable


class TokenUsage(TypedDict):
    prompt_tokens: Optional[int]
    completion_tokens: Optional[int]
    total_tokens: Optional[int]


@runtime_checkable
class ResponseParser(Protocol):
    def extract_model_name(self, request_body: Optional[str]) -> Optional[str]: ...

    def extract_token_usage(self, response_body: Optional[str]) -> TokenUsage: ...

    def extract_token_usage_from_sse(self, accumulated_chunks: str) -> TokenUsage: ...
