import pytest
import pytest_asyncio
import json

from sparrow.database import Database
from sparrow.models import Trace
from sparrow.config import AppConfig, RouteConfig
from sparrow.proxy.router import create_proxy_app

from httpx import AsyncClient, ASGITransport


@pytest_asyncio.fixture
async def db(tmp_path):
    database = Database(str(tmp_path / "test_proxy.db"))
    await database.init()
    yield database
    await database.close()


@pytest_asyncio.fixture
def config():
    return AppConfig(
        routes=[RouteConfig(prefix="/v1", target_url="https://httpbin.org")],
        storage=AppConfig().storage,
    )


class TestProxyRouter:
    @pytest.mark.asyncio
    async def test_no_matching_route(self, db, config):
        app = create_proxy_app(config, db)
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/nonexistent/path")
            assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_proxy_with_mock_server(self, db, tmp_path):
        from starlette.applications import Starlette
        from starlette.responses import JSONResponse
        from starlette.routing import Route

        async def mock_handler(request):
            body = await request.json()
            return JSONResponse(
                {
                    "id": "chatcmpl-test",
                    "model": body.get("model", "unknown"),
                    "usage": {
                        "prompt_tokens": 10,
                        "completion_tokens": 5,
                        "total_tokens": 15,
                    },
                }
            )

        async def mock_error_handler(request):
            return JSONResponse({"error": "internal error"}, status_code=500)

        mock_app = Starlette(
            routes=[
                Route("/v1/chat/completions", mock_handler, methods=["POST"]),
                Route("/v1/error", mock_error_handler, methods=["GET"]),
            ]
        )
        mock_transport = ASGITransport(app=mock_app)

        async with AsyncClient(
            transport=mock_transport, base_url="http://mocktest"
        ) as mock_client:
            resp = await mock_client.post(
                "/v1/chat/completions",
                json={
                    "model": "gpt-4o",
                    "messages": [{"role": "user", "content": "Hello"}],
                },
            )
            assert resp.status_code == 200
            data = resp.json()
            assert data["model"] == "gpt-4o"
            assert data["usage"]["total_tokens"] == 15

            err_resp = await mock_client.get("/v1/error")
            assert err_resp.status_code == 500
