"""LLM response cache - reduces redundant API calls."""

import hashlib
import json
import os
from pathlib import Path
from typing import Any

from app.core.logging import get_logger

logger = get_logger("llm.cache")

# Default cache dir - can be overridden via LANGCHAIN_CACHE or env
DEFAULT_CACHE_DIR = Path(os.getenv("LANGCHAIN_CACHE", ".langchain_cache"))


class LLMCacheService:
    """Simple file-based cache for LLM responses."""

    def __init__(self, cache_dir: Path | None = None) -> None:
        self._cache_dir = (cache_dir or DEFAULT_CACHE_DIR).resolve()
        self._memory: dict[str, Any] = {}
        self._use_file = self._cache_dir.exists() or self._ensure_dir()

    def _ensure_dir(self) -> bool:
        try:
            self._cache_dir.mkdir(parents=True, exist_ok=True)
            return True
        except OSError as e:
            logger.warning("Could not create cache dir %s: %s", self._cache_dir, e)
            return False

    def _key(self, prefix: str, *parts: Any) -> str:
        content = json.dumps(parts, default=str, sort_keys=True)
        h = hashlib.sha256(content.encode()).hexdigest()
        return f"{prefix}_{h}"

    def get(self, prefix: str, *parts: Any) -> Any | None:
        """Get cached value if exists."""
        key = self._key(prefix, *parts)
        if key in self._memory:
            return self._memory[key]
        if self._use_file:
            path = self._cache_dir / f"{key}.json"
            if path.exists():
                try:
                    data = json.loads(path.read_text())
                    self._memory[key] = data
                    return data
                except Exception as e:
                    logger.warning("Cache read failed for %s: %s", key, e)
        return None

    def set(self, prefix: str, value: Any, *parts: Any) -> None:
        """Store value in cache."""
        key = self._key(prefix, *parts)
        self._memory[key] = value
        if self._use_file:
            path = self._cache_dir / f"{key}.json"
            try:
                path.write_text(json.dumps(value, default=str))
            except Exception as e:
                logger.warning("Cache write failed for %s: %s", key, e)
