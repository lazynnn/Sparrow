import pytest

from sparrow.config import AppConfig, load_config, StorageConfig, RouteConfig


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
