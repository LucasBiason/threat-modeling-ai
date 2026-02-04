"""OpenAI LLM connection - lazy proxy to ChatOpenAI."""

import base64
import json
import re
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from app.core.config import Settings
from app.core.logging import get_logger
from app.threat_analysis.llm.base import LLMConnection

logger = get_logger("llm.openai")


class OpenAIConnection(LLMConnection):
    """OpenAI connection - instantiated only when used."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._llm: ChatOpenAI | None = None

    @property
    def name(self) -> str:
        return "OpenAI"

    def _ensure_llm(self) -> ChatOpenAI | None:
        if self._llm is not None:
            return self._llm
        if not self._settings.openai_api_key:
            return None
        try:
            self._llm = ChatOpenAI(
                model=self._settings.fallback_model,
                temperature=self._settings.llm_temperature,
                api_key=self._settings.openai_api_key,
            )
            logger.info("OpenAI connection initialized: %s", self._settings.fallback_model)
            return self._llm
        except Exception as e:
            logger.error("OpenAI init failed: %s", e)
            return None

    def is_configured(self) -> bool:
        return bool(self._settings.openai_api_key)

    async def invoke_vision(
        self, prompt: str, image_bytes: bytes, **kwargs: Any
    ) -> dict[str, Any]:
        llm = self._ensure_llm()
        if not llm:
            return {"error": "OpenAI not configured", "error_type": "config", "service": self.name}

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
            return {"error": "OpenAI not configured", "error_type": "config", "service": self.name}

        from langchain_core.messages import BaseMessage

        lc_messages: list[BaseMessage] = []
        for m in messages:
            role = m.get("role", "user")
            content = m.get("content", "")
            if role == "system":
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
            if "API key" in err or "401" in err or "invalid" in err.lower():
                return {"error": err, "error_type": "invalid_api_key", "service": self.name}
            return {"error": err, "error_type": "processing_error", "service": self.name}

    def _parse_json(self, text: str) -> dict[str, Any]:
        if not text:
            return {"error": "Empty response", "error_type": "empty", "service": self.name}
        text = text.strip().replace("```json", "").replace("```", "").strip()
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
        return {"error": "Invalid JSON response", "error_type": "invalid_json", "service": self.name}
