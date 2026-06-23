import httpx
import pytest
import pytest_asyncio

from sparrow.config import AppConfig, UpstreamProxyConfig, RouteConfig
from sparrow.database import Database
from sparrow.proxy.router import _build_proxy_client, create_proxy_app

from httpx import ASGITransport


@pytest_asyncio.fixture
async def db(tmp_path):
    database = Database(str(tmp_path / "test_proxy_client.db"))
    await database.init()
    yield database
    await database.close()


class TestBuildProxyClient:
    def test_no_proxy_trust_env(self):
        proxy_config = UpstreamProxyConfig()
        timeout = httpx.Timeout(300, connect=10.0)
        client = _build_proxy_client(proxy_config, timeout)
        assert client._transport is not None

    def test_single_http_proxy(self):
        proxy_config = UpstreamProxyConfig(http_proxy="http://proxy:8080")
        timeout = httpx.Timeout(300, connect=10.0)
        client = _build_proxy_client(proxy_config, timeout)
        assert client is not None

    def test_single_https_proxy(self):
        proxy_config = UpstreamProxyConfig(https_proxy="http://proxy:8080")
        timeout = httpx.Timeout(300, connect=10.0)
        client = _build_proxy_client(proxy_config, timeout)
        assert client is not None

    def test_same_proxy_for_both(self):
        proxy_config = UpstreamProxyConfig(
            http_proxy="http://proxy:8080",
            https_proxy="http://proxy:8080",
        )
        timeout = httpx.Timeout(300, connect=10.0)
        client = _build_proxy_client(proxy_config, timeout)
        assert client is not None

    def test_different_proxy_for_http_and_https(self):
        proxy_config = UpstreamProxyConfig(
            http_proxy="http://proxy-http:8080",
            https_proxy="http://proxy-https:8443",
        )
        timeout = httpx.Timeout(300, connect=10.0)
        client = _build_proxy_client(proxy_config, timeout)
        assert client is not None

    def test_no_proxy_with_proxy(self):
        proxy_config = UpstreamProxyConfig(
            https_proxy="http://proxy:8080",
            no_proxy="localhost,.internal",
        )
        timeout = httpx.Timeout(300, connect=10.0)
        client = _build_proxy_client(proxy_config, timeout)
        assert client is not None

    def test_no_config_preserves_trust_env(self):
        proxy_config = UpstreamProxyConfig()
        timeout = httpx.Timeout(300, connect=10.0)
        client = _build_proxy_client(proxy_config, timeout)
        assert client._trust_env is True

    def test_proxy_config_disables_trust_env(self):
        proxy_config = UpstreamProxyConfig(https_proxy="http://proxy:8080")
        timeout = httpx.Timeout(300, connect=10.0)
        client = _build_proxy_client(proxy_config, timeout)
        assert client._trust_env is False


class TestProxyClientIntegration:
    @pytest.mark.asyncio
    async def test_proxy_config_creates_valid_client(self, db):
        config = AppConfig(
            routes=[RouteConfig(prefix="/v1", target_url="https://httpbin.org")],
            upstream_proxy=UpstreamProxyConfig(
                https_proxy="http://proxy.corp:8080",
            ),
        )
        app = create_proxy_app(config, db)
        assert app is not None

    @pytest.mark.asyncio
    async def test_no_proxy_config_creates_valid_client(self, db):
        config = AppConfig(
            routes=[RouteConfig(prefix="/v1", target_url="https://httpbin.org")],
        )
        app = create_proxy_app(config, db)
        assert app is not None

    @pytest.mark.asyncio
    async def test_no_proxy_bypass_creates_valid_client(self, db):
        config = AppConfig(
            routes=[RouteConfig(prefix="/v1", target_url="https://httpbin.org")],
            upstream_proxy=UpstreamProxyConfig(
                https_proxy="http://proxy.corp:8080",
                no_proxy="localhost,.internal",
            ),
        )
        app = create_proxy_app(config, db)
        assert app is not None
