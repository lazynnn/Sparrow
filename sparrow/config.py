from __future__ import annotations

import pathlib
import shutil

import yaml
from pydantic import BaseModel, Field, field_validator


def _parse_size(value: str) -> int:
    units = {"B": 1, "KB": 1024, "MB": 1024**2, "GB": 1024**3}
    value = value.strip()
    for suffix, multiplier in sorted(units.items(), key=lambda x: -len(x[0])):
        if value.upper().endswith(suffix):
            return int(float(value[: -len(suffix)]) * multiplier)
    return int(value)


class RouteConfig(BaseModel):
    prefix: str
    target_url: str


class ModelPricing(BaseModel):
    input: float
    output: float


class StorageConfig(BaseModel):
    database: str = "./sparrow.db"
    max_body_size: str = "1MB"
    archive_dir: str = "./archives"

    @property
    def max_body_bytes(self) -> int:
        return _parse_size(self.max_body_size)


class UpstreamProxyConfig(BaseModel):
    http_proxy: str | None = None
    https_proxy: str | None = None
    no_proxy: str | None = None
    ssl_verify: bool = True
    trust_env: bool | None = None

    @field_validator("http_proxy", "https_proxy")
    @classmethod
    def _validate_proxy_url(cls, v: str | None) -> str | None:
        if v is None:
            return v
        v = v.strip()
        if not v:
            return None
        if not v.startswith(("http://", "https://", "socks5://", "socks5h://")):
            raise ValueError(
                f"Invalid proxy URL: {v}. Must start with http://, https://, socks5://, or socks5h://"
            )
        return v

    @field_validator("no_proxy")
    @classmethod
    def _validate_no_proxy(cls, v: str | None) -> str | None:
        if v is None:
            return v
        v = v.strip()
        if not v:
            return None
        return v

    @property
    def has_proxy(self) -> bool:
        return self.http_proxy is not None or self.https_proxy is not None

    @property
    def resolved_trust_env(self) -> bool:
        if self.trust_env is not None:
            return self.trust_env
        if self.has_proxy or self.no_proxy is not None:
            return False
        return True


class AppConfig(BaseModel):
    proxy_port: int = Field(default=8080, ge=1, le=65535)
    ui_port: int = Field(default=8081, ge=1, le=65535)
    log_level: str = "INFO"
    routes: list[RouteConfig] = Field(
        default_factory=lambda: [
            RouteConfig(prefix="/v1", target_url="https://api.openai.com/v1")
        ]
    )
    storage: StorageConfig = Field(default_factory=StorageConfig)
    pricing: dict[str, ModelPricing] = Field(default_factory=dict)
    upstream_proxy: UpstreamProxyConfig = Field(default_factory=UpstreamProxyConfig)
    stream_timeout: int = Field(default=300, ge=1)


def load_config(path: str) -> AppConfig:
    config_path = pathlib.Path(path)
    if not config_path.exists():
        example = pathlib.Path(__file__).parent.parent / "config.example.yaml"
        if example.exists():
            shutil.copy2(example, config_path)
            print(f"Created default config at {config_path}")
        else:
            config_path.write_text(_DEFAULT_CONFIG)
            print(f"Created default config at {config_path}")

    with open(config_path) as f:
        data = yaml.safe_load(f) or {}

    if data.get("upstream_proxy") is None:
        data["upstream_proxy"] = {}

    return AppConfig(**data)


_DEFAULT_CONFIG = """\
proxy_port: 8080
ui_port: 8081
log_level: INFO
routes:
  - prefix: "/v1"
    target_url: "https://api.openai.com/v1"
storage:
  database: "./sparrow.db"
  max_body_size: "1MB"
  archive_dir: "./archives"
pricing: {}
upstream_proxy: {}
stream_timeout: 300
"""
