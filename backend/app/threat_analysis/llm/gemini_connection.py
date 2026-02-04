"""Gemini LLM connection - lazy proxy to ChatGoogleGenerativeAI."""

import base64
from typing import Any

from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from app.core.config import Settings
from app.core.logging import get_logger
from app.threat_analysis.llm.base import LLMConnection

logger = get_logger("llm.gemini")


class GeminiConnection(LLMConnection):
    """Gemini connection - instantiated only when used."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._llm: ChatGoogleGenerativeAI | None = None

    @property
    def name(self) -> str:
        return "Gemini"

    def _ensure_llm(self) -> ChatGoogleGenerativeAI | None:
        """Lazy init - only create client when first used."""
        if self._llm is not None:
            return self._llm
        if not self._settings.google_api_key:
            return None
        try:
            self._llm = ChatGoogleGenerativeAI(
                model=self._settings.primary_model,
                temperature=self._settings.llm_temperature,
                google_api_key=self._settings.google_api_key,
            )
            logger.info("Gemini connection initialized: %s", self._settings.primary_model)
            return self._llm
        except Exception as e:
            logger.error("Gemini init failed: %s", e)
            return None

    def is_configured(self) -> bool:
        return bool(self._settings.google_api_key)

    async def invoke_vision(
        self, prompt: str, image_bytes: bytes, **kwargs: Any
    ) -> dict[str, Any]:
        llm = self._ensure_llm()
        if not llm:
            return {"error": "Gemini not configured", "error_type": "config", "service": self.name}

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

    async def invoke_text(self, messages: list[dict[str, str]], **kwargs: Any) -> dict[str, Any]:
        llm = self._ensure_llm()
        if not llm:
            return {"error": "Gemini not configured", "error_type": "config", "service": self.name}

        from langchain_core.messages import BaseMessage

        lc_messages: list[BaseMessage] = []
        for m in messages:
            role = m.get("role", "user")
            content = m.get("content", "")
            if role == "system":
                from langchain_core.messages import SystemMessage

                lc_messages.append(SystemMessage(content=content))
            else:
                lc_messages.append(HumanMessage(content=content))

        return await self._invoke(llm.ainvoke(lc_messages))

    async def _invoke(self, coro) -> dict[str, Any]:
        try:
            response = await coro
            text = getattr(response, "content", str(response))
            return self._parse_json(text)
        except Exception as e:
            err = str(e)
            if "API key" in err or "invalid" in err.lower():
                return {"error": err, "error_type": "invalid_api_key", "service": self.name}
            return {"error": err, "error_type": "processing_error", "service": self.name}

    def _parse_json(self, text: str) -> dict[str, Any]:
        import json
        import re

        if not text:
            return {"error": "Empty response", "error_type": "empty", "service": self.name}
        text = text.strip()
        for start, end in [("{", "}"), ("[", "]")]:
            idx = text.find(start)
            if idx != -1:
                depth = 0
                for i, c in enumerate(text[idx:], idx):
                    if c == start:
                        depth += 1
                    elif c == end:
                        depth -= 1
                        if depth == 0:
                            try:
                                return json.loads(text[idx : i + 1])
                            except json.JSONDecodeError:
                                pass
        match = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
        if match:
            try:
                return json.loads(match.group(1).strip())
            except json.JSONDecodeError:
                pass
        return {"error": "Invalid JSON response", "error_type": "invalid_json", "service": self.name}
