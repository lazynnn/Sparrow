import pytest

from sparrow.config import (
    AppConfig,
    UpstreamProxyConfig,
    load_config,
    StorageConfig,
    RouteConfig,
)


class TestConfigValidation:
    def test_defaults(self):
        config = AppConfig()
        assert config.proxy_port == 8080
        assert config.ui_port == 8081
        assert config.log_level == "INFO"
        assert config.stream_timeout == 300

    def test_custom_ports(self):
        config = AppConfig(proxy_port=9090, ui_port=9091)
        assert config.proxy_port == 9090
        assert config.ui_port == 9091

    def test_invalid_port(self):
        with pytest.raises(Exception):
            AppConfig(proxy_port=99999)

    def test_routes(self):
        config = AppConfig(
            routes=[RouteConfig(prefix="/v1", target_url="https://api.openai.com/v1")]
        )
        assert len(config.routes) == 1
        assert config.routes[0].prefix == "/v1"

    def test_storage_max_body_bytes(self):
        storage = StorageConfig(max_body_size="1MB")
        assert storage.max_body_bytes == 1024 * 1024

    def test_storage_default_path(self):
        storage = StorageConfig()
        assert storage.database == "./sparrow.db"

    def test_pricing(self):
        from sparrow.config import ModelPricing

        config = AppConfig(pricing={"gpt-4o": ModelPricing(input=2.50, output=10.00)})
        assert config.pricing["gpt-4o"].input == 2.50

    def test_load_config_creates_default(self, tmp_path):
        config_path = tmp_path / "config.yaml"
        config = load_config(str(config_path))
        assert config_path.exists()
        assert config.proxy_port == 8080


class TestUpstreamProxyConfig:
    def test_defaults(self):
        proxy = UpstreamProxyConfig()
        assert proxy.http_proxy is None
        assert proxy.https_proxy is None
        assert proxy.no_proxy is None
        assert proxy.has_proxy is False

    def test_valid_http_proxy(self):
        proxy = UpstreamProxyConfig(http_proxy="http://proxy.corp:8080")
        assert proxy.http_proxy == "http://proxy.corp:8080"
        assert proxy.has_proxy is True

    def test_valid_https_proxy(self):
        proxy = UpstreamProxyConfig(https_proxy="https://proxy.corp:8443")
        assert proxy.https_proxy == "https://proxy.corp:8443"

    def test_valid_socks5_proxy(self):
        proxy = UpstreamProxyConfig(http_proxy="socks5://proxy.corp:1080")
        assert proxy.http_proxy == "socks5://proxy.corp:1080"

    def test_invalid_proxy_url(self):
        with pytest.raises(Exception):
            UpstreamProxyConfig(http_proxy="not-a-url")

    def test_invalid_proxy_no_scheme(self):
        with pytest.raises(Exception):
            UpstreamProxyConfig(https_proxy="proxy.corp:8080")

    def test_empty_string_treated_as_none(self):
        proxy = UpstreamProxyConfig(http_proxy="  ")
        assert proxy.http_proxy is None
        assert proxy.has_proxy is False

    def test_no_proxy_stripped(self):
        proxy = UpstreamProxyConfig(no_proxy="  localhost,.internal  ")
        assert proxy.no_proxy == "localhost,.internal"

    def test_no_proxy_empty_becomes_none(self):
        proxy = UpstreamProxyConfig(no_proxy="  ")
        assert proxy.no_proxy is None

    def test_empty_section_in_app_config(self):
        config = AppConfig(upstream_proxy={})
        assert config.upstream_proxy.has_proxy is False

    def test_proxy_in_app_config(self):
        config = AppConfig(
            upstream_proxy={
                "http_proxy": "http://proxy:8080",
                "https_proxy": "http://proxy:8080",
            }
        )
        assert config.upstream_proxy.has_proxy is True
        assert config.upstream_proxy.http_proxy == "http://proxy:8080"
