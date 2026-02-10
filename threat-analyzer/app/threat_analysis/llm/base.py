"""Base LLM connection interface."""

import base64
import time
from abc import ABC, abstractmethod
from typing import Any

from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from threat_modeling_shared.logging import get_logger


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
    def _ensure_llm(self) -> Any:
        """Return the LLM client instance, or None if not available/configured."""
        pass

    @abstractmethod
    def _parse_json(self, text: str) -> dict[str, Any]:
        """Parse LLM text response into a result dict (JSON or error structure)."""
        pass

    async def _invoke(self, coro: Any) -> dict[str, Any]:
        """Run the given coroutine (e.g. llm.ainvoke(messages)) and return parsed result dict."""
        logger = get_logger(f"llm.{self.name.lower()}")
        try:
            logger.info("LLM %s: request sent, waiting for response...", self.name)
            start = time.perf_counter()
            response = await coro
            elapsed = time.perf_counter() - start
            text = getattr(response, "content", str(response))
            length = len(text) if text else 0
            logger.info(
                "LLM %s: response received in %.2fs, length=%d chars",
                self.name,
                elapsed,
                length,
            )
            return self._parse_json(text)
        except Exception as e:
            err = str(e)
            if "API key" in err or "401" in err or "invalid" in err.lower():
                return {
                    "error": err,
                    "error_type": "invalid_api_key",
                    "service": self.name,
                }
            logger.warning("LLM %s: invocation failed: %s", self.name, e)
            return {
                "error": err,
                "error_type": "processing_error",
                "service": self.name,
            }

    def _not_configured_response(self) -> dict[str, Any]:
        """Return standard error dict when this connection is not configured."""
        return {
            "error": f"{self.name} not configured",
            "error_type": "config",
            "service": self.name,
        }

    async def invoke_vision(
        self, prompt: str, image_bytes: bytes, **kwargs: Any
    ) -> dict[str, Any]:
        """Invoke LLM with image input (vision).

        Returns:
            Parsed result dict or {"error": str, "error_type": str, "service": str}
        """
        llm = self._ensure_llm()
        if not llm:
            return self._not_configured_response()
        img_b64 = base64.b64encode(image_bytes).decode("utf-8")
        message = HumanMessage(
            content=[
                {"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"},
                },
            ]
        )
        return await self._invoke(llm.ainvoke([message]))

    async def invoke_text(
        self, messages: list[dict[str, str]], **kwargs: Any
    ) -> dict[str, Any]:
        """Invoke LLM with text messages only.

        Returns:
            Parsed result dict or {"error": str, "error_type": str, "service": str}
        """
        llm = self._ensure_llm()
        if not llm:
            return self._not_configured_response()
        lc_messages: list[BaseMessage] = []
        for m in messages:
            role = m.get("role", "user")
            content = m.get("content", "")
            if role == "system":
                lc_messages.append(SystemMessage(content=content))
            else:
                lc_messages.append(HumanMessage(content=content))
        return await self._invoke(llm.ainvoke(lc_messages))
