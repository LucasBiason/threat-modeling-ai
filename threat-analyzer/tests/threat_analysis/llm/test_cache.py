"""Unit tests for app.threat_analysis.llm.cache (Redis-backed)."""

import os
from unittest.mock import MagicMock, patch

import pytest

from app.threat_analysis.llm.cache import CACHE_TTL_SECONDS, LLMCacheService

# Redis URL para testes (DB 1 para nao misturar com dev). Pode sobrescrever via env.
TEST_REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/1")


def _redis_available() -> bool:
    """Check if Redis is reachable (uses backend._get_client for RedisCacheBackend)."""
    try:
        cache = LLMCacheService(redis_url=TEST_REDIS_URL)
        backend = cache._backend
        if hasattr(backend, "_get_client"):
            client = backend._get_client()
            if client is None:
                return False
            client.ping()
        return True
    except Exception:
        return False


class _FakeBackend:
    """In-memory backend for tests (no Redis). Matches shared CacheBackend protocol."""

    def __init__(self):
        self._store = {}

    def get(self, key: str) -> str | None:
        return self._store.get(key)

    def set(self, key: str, value: str, ttl_seconds: int = 0) -> None:
        self._store[key] = value


class TestLLMCacheServiceWithMockBackend:
    """Tests that run without Redis by using a fake in-memory backend."""

    def test_get_set_roundtrip(self):
        fake = _FakeBackend()
        with patch(
            "app.threat_analysis.llm.cache.get_cache_backend", return_value=fake
        ):
            cache = LLMCacheService(redis_url="redis://localhost:6379/0")
            cache.set("prefix", {"a": 1}, "arg1", "arg2")
            result = cache.get("prefix", "arg1", "arg2")
        assert result == {"a": 1}

    def test_get_miss_returns_none(self):
        with patch(
            "app.threat_analysis.llm.cache.get_cache_backend",
            return_value=_FakeBackend(),
        ):
            cache = LLMCacheService(redis_url="redis://localhost:6379/0")
            assert cache.get("x", "y") is None

    def test_key_is_deterministic(self):
        with patch(
            "app.threat_analysis.llm.cache.get_cache_backend",
            return_value=_FakeBackend(),
        ):
            cache = LLMCacheService(redis_url="redis://localhost:6379/0")
            k1 = cache._key("p", "a", "b")
            k2 = cache._key("p", "a", "b")
        assert k1 == k2
        assert k1.startswith("llm:p:")

    def test_ttl_constant(self):
        assert CACHE_TTL_SECONDS == 2 * 60 * 60

    def test_get_logs_warning_on_backend_exception(self, caplog):
        backend = MagicMock()
        backend.get.side_effect = RuntimeError("connection lost")
        with patch(
            "app.threat_analysis.llm.cache.get_cache_backend", return_value=backend
        ):
            cache = LLMCacheService(redis_url="redis://localhost:6379/0")
            result = cache.get("p", "a")
        assert result is None
        assert "Cache get failed" in caplog.text or "connection lost" in caplog.text

    def test_set_logs_warning_on_backend_exception(self, caplog):
        backend = MagicMock()
        backend.set.side_effect = RuntimeError("write failed")
        with patch(
            "app.threat_analysis.llm.cache.get_cache_backend", return_value=backend
        ):
            cache = LLMCacheService(redis_url="redis://localhost:6379/0")
            cache.set("p", {"x": 1}, "a")
        assert "Cache set failed" in caplog.text or "write failed" in caplog.text


@pytest.mark.skipif(not _redis_available(), reason="Redis not available")
class TestLLMCacheServiceRedis:
    """Integration tests requiring a real Redis instance."""

    def test_get_set_roundtrip_redis(self):
        cache = LLMCacheService(redis_url=TEST_REDIS_URL)
        cache.set("prefix", {"a": 1}, "arg1", "arg2")
        result = cache.get("prefix", "arg1", "arg2")
        assert result == {"a": 1}

    def test_get_miss_returns_none_redis(self):
        cache = LLMCacheService(redis_url=TEST_REDIS_URL)
        assert cache.get("x", "y") is None
