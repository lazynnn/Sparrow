from __future__ import annotations

import datetime
from typing import Optional

from pydantic import BaseModel, Field


class TraceListItem(BaseModel):
    id: int
    timestamp: Optional[str] = None
    request_method: str
    request_path: str
    response_status: Optional[int] = None
    model_name: Optional[str] = None
    duration_ms: Optional[float] = None
    ttfb_ms: Optional[float] = None
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    cost: Optional[float] = None
    status: str
    is_streaming: bool


class TraceDetail(TraceListItem):
    request_headers: Optional[str] = None
    request_body: Optional[str] = None
    response_headers: Optional[str] = None
    response_body: Optional[str] = None
    target_url: Optional[str] = None


class TraceListResponse(BaseModel):
    traces: list[TraceListItem]
    total: int
    page: int
    page_size: int
    total_pages: int


class TraceFilterParams(BaseModel):
    model: Optional[str] = None
    status: Optional[str] = None
    status_code: Optional[int] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    min_duration: Optional[float] = None
    path: Optional[str] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=50, ge=1, le=200)


class ModelUsage(BaseModel):
    model_name: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    cost: Optional[float] = None
    request_count: int


class DashboardResponse(BaseModel):
    total_requests: int
    total_prompt_tokens: int
    total_completion_tokens: int
    total_tokens: int
    total_cost: Optional[float] = None
    avg_duration_ms: Optional[float] = None
    models: list[ModelUsage]


class ArchiveInfo(BaseModel):
    filename: str
    path: str
    size: int
    archive_timestamp: Optional[str] = None
    trace_count: Optional[int] = None


class ArchiveCreateRequest(BaseModel):
    older_than: Optional[str] = None


class ArchiveImportRequest(BaseModel):
    path: str
