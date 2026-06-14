from __future__ import annotations

import datetime
import io
import json
import os
import tarfile
from typing import Optional

from sqlalchemy import delete, select, func

from sparrow.database import Database
from sparrow.models import Trace


def _trace_to_dict(trace: Trace) -> dict:
    return {
        "id": trace.id,
        "timestamp": trace.timestamp.isoformat() if trace.timestamp else None,
        "request_method": trace.request_method,
        "request_path": trace.request_path,
        "request_headers": trace.request_headers,
        "request_body": trace.request_body,
        "response_status": trace.response_status,
        "response_headers": trace.response_headers,
        "response_body": trace.response_body,
        "duration_ms": trace.duration_ms,
        "ttfb_ms": trace.ttfb_ms,
        "model_name": trace.model_name,
        "prompt_tokens": trace.prompt_tokens,
        "completion_tokens": trace.completion_tokens,
        "total_tokens": trace.total_tokens,
        "cost": trace.cost,
        "status": trace.status,
        "is_streaming": trace.is_streaming,
        "target_url": trace.target_url,
    }


async def create_archive(
    db: Database,
    archive_dir: str,
    older_than: Optional[datetime.datetime] = None,
    trace_ids: Optional[list[int]] = None,
) -> str:
    os.makedirs(archive_dir, exist_ok=True)

    async with db.session() as session:
        if trace_ids is not None:
            result = await session.execute(select(Trace).where(Trace.id.in_(trace_ids)))
        elif older_than is not None:
            result = await session.execute(
                select(Trace).where(Trace.timestamp < older_than)
            )
        else:
            result = await session.execute(select(Trace))

        traces = result.scalars().all()

        if not traces:
            return ""

        date_range = {
            "oldest": traces[0].timestamp.isoformat() if traces else None,
            "newest": traces[-1].timestamp.isoformat() if traces else None,
        }

        metadata = {
            "archive_timestamp": datetime.datetime.now(
                datetime.timezone.utc
            ).isoformat(),
            "trace_count": len(traces),
            "date_range": date_range,
        }

        traces_jsonl = "\n".join(
            json.dumps(_trace_to_dict(t), ensure_ascii=False) for t in traces
        )

        now = datetime.datetime.now()
        archive_name = f"sparrow-archive-{now.strftime('%Y%m%d-%H%M%S')}.tar.gz"
        archive_path = os.path.join(archive_dir, archive_name)

        with tarfile.open(archive_path, "w:gz") as tar:
            meta_bytes = json.dumps(metadata, indent=2, ensure_ascii=False).encode(
                "utf-8"
            )
            meta_info = tarfile.TarInfo(name="metadata.json")
            meta_info.size = len(meta_bytes)
            tar.addfile(meta_info, io.BytesIO(meta_bytes))

            traces_bytes = traces_jsonl.encode("utf-8")
            traces_info = tarfile.TarInfo(name="traces.jsonl")
            traces_info.size = len(traces_bytes)
            tar.addfile(traces_info, io.BytesIO(traces_bytes))

        if trace_ids is not None:
            await session.execute(delete(Trace).where(Trace.id.in_(trace_ids)))
        elif older_than is not None:
            await session.execute(delete(Trace).where(Trace.timestamp < older_than))
        else:
            await session.execute(delete(Trace))

        await session.commit()

    return archive_path


async def import_archive(db: Database, archive_path: str) -> int:
    count = 0
    with tarfile.open(archive_path, "r:gz") as tar:
        for member in tar.getmembers():
            if member.name == "traces.jsonl":
                f = tar.extractfile(member)
                if f is None:
                    continue
                content = f.read().decode("utf-8")
                async with db.session() as session:
                    for line in content.strip().split("\n"):
                        if not line.strip():
                            continue
                        data = json.loads(line)
                        existing = await session.get(Trace, data["id"])
                        if existing is not None:
                            continue

                        trace = Trace(
                            id=data["id"],
                            timestamp=datetime.datetime.fromisoformat(data["timestamp"])
                            if data.get("timestamp")
                            else None,
                            request_method=data["request_method"],
                            request_path=data["request_path"],
                            request_headers=data.get("request_headers"),
                            request_body=data.get("request_body"),
                            response_status=data.get("response_status"),
                            response_headers=data.get("response_headers"),
                            response_body=data.get("response_body"),
                            duration_ms=data.get("duration_ms"),
                            ttfb_ms=data.get("ttfb_ms"),
                            model_name=data.get("model_name"),
                            prompt_tokens=data.get("prompt_tokens"),
                            completion_tokens=data.get("completion_tokens"),
                            total_tokens=data.get("total_tokens"),
                            cost=data.get("cost"),
                            status=data.get("status", "success"),
                            is_streaming=data.get("is_streaming", False),
                            target_url=data.get("target_url"),
                        )
                        session.add(trace)
                        count += 1
                    await session.commit()
    return count


async def list_archives(archive_dir: str) -> list[dict]:
    if not os.path.isdir(archive_dir):
        return []

    archives = []
    for name in sorted(os.listdir(archive_dir), reverse=True):
        if not name.endswith(".tar.gz"):
            continue
        path = os.path.join(archive_dir, name)
        try:
            with tarfile.open(path, "r:gz") as tar:
                meta_member = tar.getmember("metadata.json")
                f = tar.extractfile(meta_member)
                if f:
                    metadata = json.loads(f.read().decode("utf-8"))
                    archives.append(
                        {
                            "filename": name,
                            "path": path,
                            "size": os.path.getsize(path),
                            **metadata,
                        }
                    )
        except (tarfile.TarError, KeyError, json.JSONDecodeError):
            archives.append(
                {
                    "filename": name,
                    "path": path,
                    "size": os.path.getsize(path),
                }
            )
    return archives
