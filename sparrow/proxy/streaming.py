from __future__ import annotations

import asyncio
import json
import time
from typing import AsyncIterator, Optional

import httpx


HOP_BY_HOP_HEADERS = frozenset(
    {
        "connection",
        "keep-alive",
        "proxy-authenticate",
        "proxy-authorization",
        "te",
        "trailers",
        "transfer-encoding",
        "upgrade",
    }
)


def filter_headers(headers: httpx.Headers) -> dict[str, str]:
    return {
        k: v
        for k, v in headers.items()
        if k.lower() not in HOP_BY_HOP_HEADERS and k.lower() != "host"
    }


async def stream_response(
    client: httpx.AsyncClient,
    method: str,
    url: str,
    headers: dict[str, str],
    body: Optional[bytes],
    timeout: float,
) -> tuple[AsyncIterator[bytes], httpx.Response]:
    req = client.build_request(method, url, headers=headers, content=body)
    response = await client.send(req, stream=True, timeout=timeout)
    return response.aiter_bytes(), response


async def accumulate_and_forward_sse(
    byte_iterator: AsyncIterator[bytes],
    timeout: float,
) -> AsyncIterator[tuple[bytes, bool]]:
    accumulated = []
    last_chunk_time = time.monotonic()

    async for chunk in byte_iterator:
        last_chunk_time = time.monotonic()
        accumulated.append(chunk)
        yield chunk, False

    yield b"", True


async def stream_with_accumulation(
    byte_iterator: AsyncIterator[bytes],
    timeout: float,
) -> AsyncIterator[tuple[bytes, bool]]:
    last_chunk_time = time.monotonic()

    async for chunk in byte_iterator:
        last_chunk_time = time.monotonic()
        yield chunk, False

    yield b"", True
