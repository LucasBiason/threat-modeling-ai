"""Ollama LLM connection - lazy proxy to ChatOllama."""

import json
from typing import Any

from langchain_ollama import ChatOllama
from threat_modeling_shared.logging import get_logger

from app.config import Settings
from app.threat_analysis.llm.base import LLMConnection

logger = get_logger("llm.ollama")


class OllamaConnection(LLMConnection):
    """Ollama connection - instantiated only when used."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._llm: ChatOllama | None = None

    @property
    def name(self) -> str:
        return "Ollama"

    def _ensure_llm(self) -> ChatOllama | None:
        if self._llm is not None:
            return self._llm
        try:
            self._llm = ChatOllama(
                model=self._settings.ollama_model,
                base_url=self._settings.ollama_base_url,
            )
            logger.info(
                "Ollama connection initialized: %s", self._settings.ollama_model
            )
            return self._llm
        except Exception as e:
            logger.error("Ollama init failed: %s", e)
            return None

    def is_configured(self) -> bool:
        return True  # Ollama has no API key, assume configured

    def _parse_json(self, text: str) -> dict[str, Any]:
        if not text:
            return {
                "error": "Empty response",
                "error_type": "empty",
                "service": self.name,
            }
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
        return {
            "error": "Invalid JSON response",
            "error_type": "invalid_json",
            "service": self.name,
        }
