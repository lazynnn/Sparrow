from __future__ import annotations

from typing import Optional

from sparrow.tracing.parsers.base import ResponseParser

_parsers: list[tuple[str, ResponseParser]] = []
_default_parser: Optional[ResponseParser] = None


def register(prefix: str, parser: ResponseParser) -> None:
    _parsers.append((prefix, parser))


def set_default(parser: ResponseParser) -> None:
    global _default_parser
    _default_parser = parser


def get_parser(request_path: str) -> ResponseParser:
    clean = request_path.split("?")[0]

    best_match: Optional[ResponseParser] = None
    best_len = 0
    for prefix, parser in _parsers:
        if clean.startswith(prefix) and len(prefix) > best_len:
            best_match = parser
            best_len = len(prefix)

    if best_match is not None:
        return best_match

    if _default_parser is not None:
        return _default_parser

    raise RuntimeError("No default parser registered")
