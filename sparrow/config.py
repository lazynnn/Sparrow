from __future__ import annotations

import pathlib
import shutil
from typing import Optional

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


class AppConfig(BaseModel):
    proxy_port: int = Field(default=8080, ge=1, le=65535)
    ui_port: int = Field(default=8081, ge=1, le=65535)
    log_level: str = "INFO"
    routes: list[RouteConfig] = Field(default_factory=lambda: [RouteConfig(prefix="/v1", target_url="https://api.openai.com/v1")])
    storage: StorageConfig = Field(default_factory=StorageConfig)
    pricing: dict[str, ModelPricing] = Field(default_factory=dict)
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
stream_timeout: 300
"""
