"""LLM response cache — uses shared CacheSystem (Redis or swapable backend)."""

import hashlib
import json
from typing import Any

from threat_modeling_shared import get_cache_backend
from threat_modeling_shared.logging import get_logger

logger = get_logger("llm.cache")

# TTL padrão: 2 horas (em segundos)
CACHE_TTL_SECONDS = 2 * 60 * 60


class LLMCacheService:
    """Cache for LLM responses using shared cache backend (e.g. Redis). TTL 2 hours."""

    def __init__(self, redis_url: str = "redis://localhost:6379/0") -> None:
        """Initialize with cache backend from shared (Redis by default).

        Args:
            redis_url: Passed to shared get_cache_backend; change backend in shared to swap.
        """
        self._backend = get_cache_backend(redis_url=redis_url)

    def _key(self, prefix: str, *parts: Any) -> str:
        content = json.dumps(parts, default=str, sort_keys=True)
        h = hashlib.sha256(content.encode()).hexdigest()
        return f"llm:{prefix}:{h}"

    def get(self, prefix: str, *parts: Any) -> Any | None:
        """Get cached value if exists."""
        key = self._key(prefix, *parts)
        try:
            data = self._backend.get(key)
            if data is None:
                return None
            return json.loads(data)
        except Exception as e:
            logger.warning("Cache get failed for %s: %s", key, e)
            return None

    def set(self, prefix: str, value: Any, *parts: Any) -> None:
        """Store value in cache with 2-hour TTL."""
        key = self._key(prefix, *parts)
        try:
            serialized = json.dumps(value, default=str)
            self._backend.set(key, serialized, ttl_seconds=CACHE_TTL_SECONDS)
        except Exception as e:
            logger.warning("Cache set failed for %s: %s", key, e)
