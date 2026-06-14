from __future__ import annotations

import pathlib

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from sparrow.api.routes import router, init_api_routes
from sparrow.config import AppConfig
from sparrow.database import Database


def create_web_app(config: AppConfig, db: Database) -> FastAPI:
    app = FastAPI(title="Sparrow Web UI", docs_url=None, redoc_url=None)

    init_api_routes(db, config)
    app.include_router(router)

    web_dir = pathlib.Path(__file__).parent / "web"
    static_dir = web_dir / "static"
    templates_dir = web_dir / "templates"

    templates = Jinja2Templates(directory=str(templates_dir))

    app.mount(
        "/static",
        StaticFiles(directory=str(static_dir)),
        name="static",
    )

    @app.get("/")
    async def index(request: Request):
        return templates.TemplateResponse(request, "index.html")

    return app
