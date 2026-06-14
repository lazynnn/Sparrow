from __future__ import annotations

import json
import time
from contextlib import asynccontextmanager
from typing import Optional

import httpx
from fastapi import FastAPI, Request, Response
from fastapi.background import BackgroundTasks
from fastapi.responses import StreamingResponse

from sparrow.config import AppConfig
from sparrow.database import Database
from sparrow.proxy.streaming import filter_headers
from sparrow.tracing.tracer import save_trace


def _match_route(path: str, routes: list) -> Optional[str]:
    best_match = None
    best_prefix = ""
    for route in routes:
        if path.startswith(route.prefix) and len(route.prefix) > len(best_prefix):
            best_match = route.target_url
            best_prefix = route.prefix
    return best_match


def _build_target_url(target_base: str, request_path: str, prefix: str) -> str:
    remaining = request_path[len(prefix) :]
    if not remaining.startswith("/") and remaining:
        remaining = "/" + remaining
    base = target_base.rstrip("/")
    return f"{base}{remaining}"


def _get_request_path(request: Request) -> str:
    path = f"/{request.path_params.get('path', '')}"
    qp = str(request.query_params)
    if qp:
        path = f"{path}?{qp}"
    return path


def create_proxy_app(config: AppConfig, db: Database) -> FastAPI:
    client = httpx.AsyncClient(
        timeout=httpx.Timeout(config.stream_timeout, connect=10.0),
        follow_redirects=True,
    )

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        yield
        await client.aclose()

    app = FastAPI(
        title="Sparrow Proxy", docs_url=None, redoc_url=None, lifespan=lifespan
    )

    @app.api_route(
        "/{path:path}",
        methods=["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"],
    )
    async def proxy_request(request: Request, path: str):
        request_path = _get_request_path(request)

        target_base = _match_route(request_path, config.routes)
        if target_base is None:
            return Response(status_code=404, content="No matching route")

        for route in config.routes:
            if target_base == route.target_url:
                target_url = _build_target_url(target_base, request_path, route.prefix)
                break
        else:
            target_url = _build_target_url(target_base, request_path, "")

        forward_headers = filter_headers(request.headers)

        body = await request.body()

        is_streaming_request = False
        if body:
            try:
                body_json = json.loads(body)
                is_streaming_request = body_json.get("stream", False)
            except (json.JSONDecodeError, UnicodeDecodeError):
                pass

        start = time.monotonic()

        try:
            if is_streaming_request:
                return await _handle_streaming(
                    request,
                    client,
                    target_url,
                    forward_headers,
                    body,
                    config,
                    db,
                    start,
                )
            else:
                return await _handle_non_streaming(
                    request,
                    client,
                    target_url,
                    forward_headers,
                    body,
                    config,
                    db,
                    start,
                )
        except httpx.TimeoutException:
            duration_ms = (time.monotonic() - start) * 1000
            bg = BackgroundTasks()
            bg.add_task(
                save_trace,
                db,
                config,
                request.method,
                request_path,
                _headers_to_json(forward_headers),
                body.decode("utf-8", errors="replace") if body else None,
                None,
                None,
                None,
                duration_ms,
                None,
                is_streaming_request,
                "timeout",
                target_url,
            )
            return Response(status_code=504, content="Gateway Timeout")
        except Exception as exc:
            duration_ms = (time.monotonic() - start) * 1000
            bg = BackgroundTasks()
            bg.add_task(
                save_trace,
                db,
                config,
                request.method,
                request_path,
                _headers_to_json(forward_headers),
                body.decode("utf-8", errors="replace") if body else None,
                500,
                None,
                str(exc),
                duration_ms,
                None,
                is_streaming_request,
                "error",
                target_url,
            )
            return Response(status_code=502, content=f"Bad Gateway: {exc}")

    async def _handle_streaming(
        request,
        client,
        target_url,
        forward_headers,
        body,
        config,
        db,
        start,
    ):
        request_path = _get_request_path(request)

        req = client.build_request(
            request.method, target_url, headers=forward_headers, content=body
        )
        response = await client.send(req, stream=True)

        ttfb_ms = (time.monotonic() - start) * 1000
        status_code = response.status_code

        response_headers = filter_headers(response.headers)
        response_headers.pop("content-length", None)
        response_headers.pop("transfer-encoding", None)

        accumulated_chunks: list[bytes] = []

        async def generate():
            try:
                async for chunk in response.aiter_bytes():
                    accumulated_chunks.append(chunk)
                    yield chunk
            except Exception:
                pass
            finally:
                await response.aclose()
                duration_ms = (time.monotonic() - start) * 1000
                full_body = b"".join(accumulated_chunks).decode(
                    "utf-8", errors="replace"
                )

                await save_trace(
                    db,
                    config,
                    request.method,
                    request_path,
                    _headers_to_json(forward_headers),
                    body.decode("utf-8", errors="replace") if body else None,
                    status_code,
                    _headers_to_json(dict(response.headers)),
                    full_body,
                    duration_ms,
                    ttfb_ms,
                    True,
                    "success",
                    target_url,
                )

        return StreamingResponse(
            generate(),
            status_code=status_code,
            headers=response_headers,
        )

    async def _handle_non_streaming(
        request,
        client,
        target_url,
        forward_headers,
        body,
        config,
        db,
        start,
    ):
        request_path = _get_request_path(request)

        resp = await client.request(
            request.method, target_url, headers=forward_headers, content=body
        )
        duration_ms = (time.monotonic() - start) * 1000

        resp_headers = filter_headers(resp.headers)

        bg = BackgroundTasks()
        bg.add_task(
            save_trace,
            db,
            config,
            request.method,
            request_path,
            _headers_to_json(forward_headers),
            body.decode("utf-8", errors="replace") if body else None,
            resp.status_code,
            _headers_to_json(dict(resp.headers)),
            resp.text,
            duration_ms,
            None,
            False,
            "success",
            target_url,
        )

        return Response(
            content=resp.content,
            status_code=resp.status_code,
            headers=resp_headers,
            background=bg,
        )

    return app


def _headers_to_json(headers) -> Optional[str]:
    if not headers:
        return None
    try:
        if isinstance(headers, dict):
            return json.dumps(headers)
        return json.dumps(dict(headers))
    except (TypeError, ValueError):
        return None
