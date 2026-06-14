from __future__ import annotations

import time
from typing import Optional

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from sparrow.config import AppConfig
from sparrow.database import Database
from sparrow.tracing.tracer import save_trace


class TracingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, db: Database, config: AppConfig):
        super().__init__(app)
        self.db = db
        self.config = config

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        start = time.monotonic()
        response = await call_next(request)
        duration_ms = (time.monotonic() - start) * 1000
        return response
