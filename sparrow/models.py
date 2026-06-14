from __future__ import annotations

import datetime
from typing import Optional

from sqlalchemy import Index, String, Text, Float, Integer, DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Trace(Base):
    __tablename__ = "traces"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    timestamp: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=func.now(), nullable=False
    )
    request_method: Mapped[str] = mapped_column(String(10), nullable=False)
    request_path: Mapped[str] = mapped_column(String(500), nullable=False)
    request_headers: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    request_body: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    response_status: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    response_headers: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    response_body: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    duration_ms: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    ttfb_ms: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    model_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    prompt_tokens: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    completion_tokens: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    total_tokens: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    cost: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="success")
    is_streaming: Mapped[bool] = mapped_column(default=False, nullable=False)
    target_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)

    __table_args__ = (
        Index("ix_traces_timestamp", "timestamp"),
        Index("ix_traces_request_path", "request_path"),
        Index("ix_traces_response_status", "response_status"),
        Index("ix_traces_model_name", "model_name"),
        Index("ix_traces_duration_ms", "duration_ms"),
    )


def truncate_body(body: Optional[str], max_bytes: int) -> Optional[str]:
    if body is None:
        return None
    encoded = body.encode("utf-8")
    if len(encoded) <= max_bytes:
        return body
    return encoded[:max_bytes].decode("utf-8", errors="ignore") + "[TRUNCATED]"
