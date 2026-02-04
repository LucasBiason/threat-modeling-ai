"""Application configuration using Pydantic Settings."""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def _env_file_paths() -> list[str]:
    """Resolve env file paths: configs/.env, ../configs/.env, .env."""
    cwd = Path.cwd()
    candidates = [
        cwd / "configs" / ".env",
        cwd / ".." / "configs" / ".env",
        cwd / ".env",
    ]
    return [str(p.resolve()) for p in candidates if p.resolve().exists()]


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=_env_file_paths() or ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        populate_by_name=True,
    )

    # API Settings
    app_name: str = "Threat Modeling AI"
    app_version: str = "1.0.0"
    debug: bool = False
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"

    # CORS Settings (comma-separated string, parsed to list)
    cors_origins_raw: str = Field(default="*", alias="cors_origins")
    cors_allow_credentials: bool = True
    cors_allow_methods: list[str] = Field(default_factory=lambda: ["*"])
    cors_allow_headers: list[str] = Field(default_factory=lambda: ["*"])

    # LLM Provider Settings
    google_api_key: str | None = None
    openai_api_key: str | None = None
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen2-vl"

    # Model Settings
    primary_model: str = "gemini-1.5-pro"
    fallback_model: str = "gpt-4o"
    fast_model: str = "gemini-1.5-flash"
    embedding_model: str = "models/embedding-001"
    llm_temperature: float = 0.0

    # RAG Settings
    knowledge_base_path: Path | None = None
    rag_chunk_size: int = 800
    rag_chunk_overlap: int = 80

    # File Upload Settings
    max_upload_size_mb: int = 10
    allowed_image_types: list[str] = Field(
        default_factory=lambda: ["image/jpeg", "image/png", "image/webp", "image/gif"]
    )

    # Pipeline (DummyPipeline só para testes unitários; default=False usa LLM)
    use_dummy_pipeline: bool = False

    @field_validator("use_dummy_pipeline", mode="before")
    @classmethod
    def parse_bool_env(cls, v: str | bool | None) -> bool:
        if isinstance(v, bool):
            return v
        if isinstance(v, str):
            return v.lower() in ("true", "1", "yes")
        return False

    @field_validator("knowledge_base_path", mode="before")
    @classmethod
    def parse_knowledge_base_path(cls, v: str | Path | None) -> Path | None:
        """Convert string to Path and validate existence."""
        if v is None:
            return None
        path = Path(v) if isinstance(v, str) else v
        if not path.exists():
            return None
        return path

    @property
    def cors_origins(self) -> list[str]:
        """Parse CORS origins from comma-separated string."""
        raw = getattr(self, "cors_origins_raw", "*") or "*"
        return [o.strip() for o in str(raw).split(",") if o.strip()] or ["*"]

    @property
    def max_upload_size_bytes(self) -> int:
        """Get max upload size in bytes."""
        return self.max_upload_size_mb * 1024 * 1024


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
