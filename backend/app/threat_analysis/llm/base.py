"""Base LLM connection interface."""

from abc import ABC, abstractmethod
from typing import Any


class LLMConnection(ABC):
    """Abstract base for LLM connection - proxy to a specific LLM service."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Display name for logging."""
        pass

    @abstractmethod
    def is_configured(self) -> bool:
        """Check if this connection is properly configured (API key, etc.)."""
        pass

    @abstractmethod
    async def invoke_vision(
        self, prompt: str, image_bytes: bytes, **kwargs: Any
    ) -> dict[str, Any]:
        """Invoke LLM with image input (vision).

        Returns:
            Parsed result dict or {"error": str, "error_type": str, "service": str}
        """
        pass

    @abstractmethod
    async def invoke_text(self, messages: list[dict[str, str]], **kwargs: Any) -> dict[str, Any]:
        """Invoke LLM with text messages only.

        Returns:
            Parsed result dict or {"error": str, "error_type": str, "service": str}
        """
        pass
