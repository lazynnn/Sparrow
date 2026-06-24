from __future__ import annotations

import asyncio
import datetime
import json
from typing import Optional

from fastapi import APIRouter, Query
from sqlalchemy import select, func, delete

from sparrow.api.schemas import (
    TraceListItem,
    TraceDetail,
    TraceListResponse,
    DashboardResponse,
    ModelUsage,
    ArchiveInfo,
    ArchiveCreateRequest,
    ArchiveImportRequest,
)
from sparrow.archive.archiver import create_archive, import_archive, list_archives
from sparrow.config import AppConfig
from sparrow.database import Database
from sparrow.models import Trace
from sparrow.utils import utc_isoformat

router = APIRouter(prefix="/api")

_trace_events: list[asyncio.Queue] = []


def _trace_to_list_item(t: Trace) -> TraceListItem:
    return TraceListItem(
        id=t.id,
        timestamp=utc_isoformat(t.timestamp),
        request_method=t.request_method,
        request_path=t.request_path,
        response_status=t.response_status,
        model_name=t.model_name,
        duration_ms=t.duration_ms,
        ttfb_ms=t.ttfb_ms,
        prompt_tokens=t.prompt_tokens,
        completion_tokens=t.completion_tokens,
        total_tokens=t.total_tokens,
        cost=t.cost,
        status=t.status,
        is_streaming=t.is_streaming,
    )


@router.get("/traces", response_model=TraceListResponse)
async def list_traces(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=200),
    model: Optional[str] = None,
    status: Optional[str] = None,
    status_code: Optional[int] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    min_duration: Optional[float] = None,
    path: Optional[str] = None,
):
    from sparrow.api.routes import _db, _config

    async with _db.session() as session:
        query = select(Trace)
        count_query = select(func.count(Trace.id))

        if model:
            query = query.where(Trace.model_name == model)
            count_query = count_query.where(Trace.model_name == model)
        if status:
            query = query.where(Trace.status == status)
            count_query = count_query.where(Trace.status == status)
        if status_code:
            query = query.where(Trace.response_status == status_code)
            count_query = count_query.where(Trace.response_status == status_code)
        if date_from:
            dt = datetime.datetime.fromisoformat(date_from)
            if dt.tzinfo is not None:
                dt = dt.astimezone(datetime.timezone.utc).replace(tzinfo=None)
            query = query.where(Trace.timestamp >= dt)
            count_query = count_query.where(Trace.timestamp >= dt)
        if date_to:
            dt = datetime.datetime.fromisoformat(date_to)
            if dt.tzinfo is not None:
                dt = dt.astimezone(datetime.timezone.utc).replace(tzinfo=None)
            query = query.where(Trace.timestamp <= dt)
            count_query = count_query.where(Trace.timestamp <= dt)
        if min_duration:
            query = query.where(Trace.duration_ms >= min_duration)
            count_query = count_query.where(Trace.duration_ms >= min_duration)
        if path:
            query = query.where(Trace.request_path.contains(path))
            count_query = count_query.where(Trace.request_path.contains(path))

        total_result = await session.execute(count_query)
        total = total_result.scalar() or 0

        query = query.order_by(Trace.timestamp.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await session.execute(query)
        traces = result.scalars().all()

        total_pages = (total + page_size - 1) // page_size

        return TraceListResponse(
            traces=[_trace_to_list_item(t) for t in traces],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )


@router.get("/traces/stream")
async def stream_traces():
    from sse_starlette.sse import EventSourceResponse

    queue: asyncio.Queue = asyncio.Queue()
    _trace_events.append(queue)

    async def event_generator():
        try:
            while True:
                try:
                    data = await asyncio.wait_for(queue.get(), timeout=30)
                    yield {"event": "trace", "data": data}
                except asyncio.TimeoutError:
                    yield {"event": "ping", "data": ""}
        except asyncio.CancelledError:
            pass
        finally:
            if queue in _trace_events:
                _trace_events.remove(queue)

    return EventSourceResponse(event_generator())


@router.get("/traces/{trace_id}", response_model=TraceDetail)
async def get_trace(trace_id: int):
    from sparrow.api.routes import _db

    async with _db.session() as session:
        trace = await session.get(Trace, trace_id)
        if trace is None:
            from fastapi import HTTPException

            raise HTTPException(status_code=404, detail="Trace not found")

        return TraceDetail(
            id=trace.id,
            timestamp=utc_isoformat(trace.timestamp),
            request_method=trace.request_method,
            request_path=trace.request_path,
            request_headers=trace.request_headers,
            request_body=trace.request_body,
            response_status=trace.response_status,
            response_headers=trace.response_headers,
            response_body=trace.response_body,
            model_name=trace.model_name,
            duration_ms=trace.duration_ms,
            ttfb_ms=trace.ttfb_ms,
            prompt_tokens=trace.prompt_tokens,
            completion_tokens=trace.completion_tokens,
            total_tokens=trace.total_tokens,
            cost=trace.cost,
            status=trace.status,
            is_streaming=trace.is_streaming,
            target_url=trace.target_url,
        )


@router.get("/dashboard", response_model=DashboardResponse)
async def get_dashboard():
    from sparrow.api.routes import _db

    async with _db.session() as session:
        total_result = await session.execute(select(func.count(Trace.id)))
        total_requests = total_result.scalar() or 0

        token_result = await session.execute(
            select(
                func.coalesce(func.sum(Trace.prompt_tokens), 0),
                func.coalesce(func.sum(Trace.completion_tokens), 0),
                func.coalesce(func.sum(Trace.total_tokens), 0),
                func.sum(Trace.cost),
                func.avg(Trace.duration_ms),
            )
        )
        row = token_result.one()
        total_prompt = row[0] or 0
        total_completion = row[1] or 0
        total_tokens = row[2] or 0
        total_cost = row[3]
        avg_duration = row[4]

        model_result = await session.execute(
            select(
                Trace.model_name,
                func.coalesce(func.sum(Trace.prompt_tokens), 0),
                func.coalesce(func.sum(Trace.completion_tokens), 0),
                func.coalesce(func.sum(Trace.total_tokens), 0),
                func.sum(Trace.cost),
                func.count(Trace.id),
            )
            .where(Trace.model_name.isnot(None))
            .group_by(Trace.model_name)
        )
        models = []
        for row in model_result.all():
            models.append(
                ModelUsage(
                    model_name=row[0] or "unknown",
                    prompt_tokens=row[1],
                    completion_tokens=row[2],
                    total_tokens=row[3],
                    cost=row[4],
                    request_count=row[5],
                )
            )

        return DashboardResponse(
            total_requests=total_requests,
            total_prompt_tokens=total_prompt,
            total_completion_tokens=total_completion,
            total_tokens=total_tokens,
            total_cost=total_cost,
            avg_duration_ms=avg_duration,
            models=models,
        )


@router.get("/archives", response_model=list[ArchiveInfo])
async def list_archive_files():
    from sparrow.api.routes import _config

    archives = await list_archives(_config.storage.archive_dir)
    return [ArchiveInfo(**a) for a in archives]


@router.post("/archives")
async def create_archive_endpoint(req: ArchiveCreateRequest):
    from sparrow.api.routes import _db, _config

    older_than = None
    if req.older_than:
        older_than = datetime.datetime.fromisoformat(req.older_than)
        if older_than.tzinfo is not None:
            older_than = older_than.astimezone(datetime.timezone.utc).replace(
                tzinfo=None
            )

    path = await create_archive(_db, _config.storage.archive_dir, older_than=older_than)
    if not path:
        return {"message": "No traces to archive", "path": None}
    return {"message": "Archive created", "path": path}


@router.post("/archives/import")
async def import_archive_endpoint(req: ArchiveImportRequest):
    from sparrow.api.routes import _db

    count = await import_archive(_db, req.path)
    return {"message": f"Imported {count} traces", "count": count}


async def notify_new_trace(trace_data: dict):
    data = json.dumps(trace_data, ensure_ascii=False)
    dead_queues = []
    for q in _trace_events:
        try:
            q.put_nowait(data)
        except asyncio.QueueFull:
            dead_queues.append(q)
    for q in dead_queues:
        if q in _trace_events:
            _trace_events.remove(q)


_db: Database = None
_config: AppConfig = None


def init_api_routes(db: Database, config: AppConfig):
    global _db, _config
    _db = db
    _config = config
