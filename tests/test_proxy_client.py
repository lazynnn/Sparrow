import httpx
import pytest
import pytest_asyncio

from sparrow.config import AppConfig, UpstreamProxyConfig, RouteConfig
from sparrow.database import Database
from sparrow.proxy.router import (
    _build_proxy_client,
    create_proxy_app,
    _should_bypass_proxy,
    _NoProxyTransport,
)

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


class TestShouldBypassProxy:
    def test_exact_hostname_match(self):
        assert _should_bypass_proxy("localhost", "localhost") is True

    def test_exact_hostname_no_match(self):
        assert _should_bypass_proxy("api.openai.com", "localhost") is False

    def test_domain_suffix_match(self):
        assert _should_bypass_proxy("api.service.internal", ".internal") is True

    def test_domain_suffix_exact_domain(self):
        assert _should_bypass_proxy("internal", ".internal") is True

    def test_domain_suffix_no_match(self):
        assert _should_bypass_proxy("api.external.com", ".internal") is False

    def test_cidr_match(self):
        assert _should_bypass_proxy("10.1.2.3", "10.0.0.0/8") is True

    def test_cidr_no_match(self):
        assert _should_bypass_proxy("192.168.1.1", "10.0.0.0/8") is False

    def test_multiple_patterns(self):
        assert (
            _should_bypass_proxy("localhost", "localhost,10.0.0.0/8,.internal") is True
        )
        assert (
            _should_bypass_proxy("10.1.2.3", "localhost,10.0.0.0/8,.internal") is True
        )
        assert (
            _should_bypass_proxy(
                "api.service.internal", "localhost,10.0.0.0/8,.internal"
            )
            is True
        )
        assert (
            _should_bypass_proxy("api.openai.com", "localhost,10.0.0.0/8,.internal")
            is False
        )

    def test_whitespace_handling(self):
        assert _should_bypass_proxy("localhost", "  localhost ,  .internal  ") is True

    def test_empty_no_proxy(self):
        assert _should_bypass_proxy("localhost", "") is False

    def test_invalid_cidr_ignored(self):
        assert _should_bypass_proxy("10.1.2.3", "not-a-cidr/8") is False


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


class TestSslVerifyConfig:
    def test_ssl_verify_default_is_true(self):
        proxy = UpstreamProxyConfig()
        assert proxy.ssl_verify is True

    def test_ssl_verify_false(self):
        proxy = UpstreamProxyConfig(ssl_verify=False)
        assert proxy.ssl_verify is False

    def test_ssl_verify_passed_to_client_no_proxy(self):
        proxy_config = UpstreamProxyConfig(ssl_verify=False)
        timeout = httpx.Timeout(300, connect=10.0)
        client = _build_proxy_client(proxy_config, timeout)
        assert client is not None

    def test_ssl_verify_passed_to_client_with_proxy(self):
        proxy_config = UpstreamProxyConfig(
            https_proxy="http://proxy:8080",
            ssl_verify=False,
        )
        timeout = httpx.Timeout(300, connect=10.0)
        client = _build_proxy_client(proxy_config, timeout)
        assert client is not None

    def test_ssl_verify_passed_to_client_with_no_proxy_list(self):
        proxy_config = UpstreamProxyConfig(
            https_proxy="http://proxy:8080",
            no_proxy="localhost,.internal",
            ssl_verify=False,
        )
        timeout = httpx.Timeout(300, connect=10.0)
        client = _build_proxy_client(proxy_config, timeout)
        assert client is not None


class TestNoProxyBypass:
    def test_no_proxy_uses_custom_transport(self):
        proxy_config = UpstreamProxyConfig(
            https_proxy="http://proxy:8080",
            no_proxy="localhost,.internal",
        )
        timeout = httpx.Timeout(300, connect=10.0)
        client = _build_proxy_client(proxy_config, timeout)
        has_noproxy = any(
            isinstance(t, _NoProxyTransport) for t in client._mounts.values()
        )
        assert has_noproxy

    def test_no_proxy_same_proxy_uses_custom_transport(self):
        proxy_config = UpstreamProxyConfig(
            http_proxy="http://proxy:8080",
            https_proxy="http://proxy:8080",
            no_proxy="localhost",
        )
        timeout = httpx.Timeout(300, connect=10.0)
        client = _build_proxy_client(proxy_config, timeout)
        transport = client._transport
        assert isinstance(transport, _NoProxyTransport)

    def test_no_proxy_different_proxies_uses_mount_transports(self):
        proxy_config = UpstreamProxyConfig(
            http_proxy="http://proxy-http:8080",
            https_proxy="http://proxy-https:8443",
            no_proxy="localhost",
        )
        timeout = httpx.Timeout(300, connect=10.0)
        client = _build_proxy_client(proxy_config, timeout)
        noproxy_transports = [
            t for t in client._mounts.values() if isinstance(t, _NoProxyTransport)
        ]
        assert len(noproxy_transports) == 2

    def test_no_proxy_without_no_proxy_uses_direct_proxy(self):
        proxy_config = UpstreamProxyConfig(
            https_proxy="http://proxy:8080",
        )
        timeout = httpx.Timeout(300, connect=10.0)
        client = _build_proxy_client(proxy_config, timeout)
        assert not isinstance(client._transport, _NoProxyTransport)
