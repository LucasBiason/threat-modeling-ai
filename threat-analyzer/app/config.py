"""Application configuration using Pydantic Settings."""

from functools import lru_cache
from pathlib import Path

from pydantic import Field, field_validator
from threat_modeling_shared.config import BaseSettings


class Settings(BaseSettings):
    """Threat Analyzer settings — extends shared BaseSettings."""

    # API (override defaults)
    app_name: str = "Threat Modeling AI"
    app_version: str = "1.0.0"

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

    @field_validator("knowledge_base_path", mode="before")
    @classmethod
    def parse_knowledge_base_path(cls, v: str | Path | None) -> Path | None:
        """Pasta da base RAG: dentro de app/rag_data (container: /app/app/rag_data)."""
        if v is None:
            path = Path(__file__).resolve().parent / "rag_data"
        else:
            path = Path(v) if isinstance(v, str) else v
        if not path.exists():
            return None
        return path

    @property
    def max_upload_size_bytes(self) -> int:
        """Get max upload size in bytes."""
        return self.max_upload_size_mb * 1024 * 1024


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
