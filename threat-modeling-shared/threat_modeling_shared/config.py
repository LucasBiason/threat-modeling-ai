"""Configuration helpers and base settings for Threat Modeling AI services."""

from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def parse_cors_origins(raw: str | list[str] | None) -> list[str]:
    """Parse CORS origins from comma-separated string or return list as-is."""
    if raw is None:
        return ["*"]
    if isinstance(raw, list):
        return raw
    return [o.strip() for o in str(raw).split(",") if o.strip()] or ["*"]


class BaseSettings(BaseSettings):
    """Base settings shared by all Threat Modeling AI backends.

    Environment variables are injected via Docker (configs/.env); no env file
    resolution. Use os.getenv in code; Pydantic reads from environment.
    """

    model_config = SettingsConfigDict(
        env_file=None,
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        populate_by_name=True,
    )

    app_name: str = "Threat Modeling AI"
    app_version: str = "1.0.0"
    debug: bool = False
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"

    redis_url: str = "redis://localhost:6379/0"
    database_url: str = ""

    cors_origins_raw: str = Field(default="*", alias="cors_origins")
    cors_allow_credentials: bool = True
    cors_allow_methods: list[str] = Field(default_factory=lambda: ["*"])
    cors_allow_headers: list[str] = Field(default_factory=lambda: ["*"])

    @property
    def cors_origins(self) -> list[str]:
        """Parse CORS origins from comma-separated string."""
        raw = getattr(self, "cors_origins_raw", "*") or "*"
        return parse_cors_origins(raw)
