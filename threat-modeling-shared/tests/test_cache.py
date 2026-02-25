"""Tests for cache module."""

from unittest.mock import MagicMock, patch

from threat_modeling_shared.cache import RedisCacheBackend, get_cache_backend  # pragma: allowlist secret


class TestRedisCacheBackend:
    def test_init_defaults(self):
        backend = RedisCacheBackend()
        assert backend._redis_url == "redis://localhost:6379/0"
        assert backend._client is None

    def test_init_custom_url(self):
        backend = RedisCacheBackend(redis_url="redis://custom:6380/1")
        assert backend._redis_url == "redis://custom:6380/1"

    @patch("redis.from_url")
    def test_get_client_lazy_init(self, mock_from_url):
        mock_client = MagicMock()
        mock_from_url.return_value = mock_client
        backend = RedisCacheBackend(redis_url="redis://test:6379/0")

        client = backend._get_client()

        mock_from_url.assert_called_once_with(
            "redis://test:6379/0",
            encoding="utf-8",
            decode_responses=True,
        )
        assert client is mock_client
        assert backend._client is mock_client

    def test_get_client_reuses_existing(self):
        backend = RedisCacheBackend()
        existing_client = MagicMock()
        backend._client = existing_client

        client = backend._get_client()

        assert client is existing_client

    def test_get_returns_value(self):
        backend = RedisCacheBackend()
        mock_client = MagicMock()
        mock_client.get.return_value = "cached_value"
        backend._client = mock_client

        result = backend.get("my_key")

        mock_client.get.assert_called_once_with("my_key")
        assert result == "cached_value"

    def test_get_returns_none_on_miss(self):
        backend = RedisCacheBackend()
        mock_client = MagicMock()
        mock_client.get.return_value = None
        backend._client = mock_client

        result = backend.get("missing_key")

        assert result is None

    def test_get_returns_none_on_exception(self):
        backend = RedisCacheBackend()
        mock_client = MagicMock()
        mock_client.get.side_effect = ConnectionError("connection refused")
        backend._client = mock_client

        result = backend.get("key")

        assert result is None

    def test_set_with_ttl(self):
        backend = RedisCacheBackend()
        mock_client = MagicMock()
        backend._client = mock_client

        backend.set("key", "value", ttl_seconds=60)

        mock_client.setex.assert_called_once_with("key", 60, "value")
        mock_client.set.assert_not_called()

    def test_set_without_ttl(self):
        backend = RedisCacheBackend()
        mock_client = MagicMock()
        backend._client = mock_client

        backend.set("key", "value")

        mock_client.set.assert_called_once_with("key", "value")
        mock_client.setex.assert_not_called()

    def test_set_with_zero_ttl(self):
        backend = RedisCacheBackend()
        mock_client = MagicMock()
        backend._client = mock_client

        backend.set("key", "value", ttl_seconds=0)

        mock_client.set.assert_called_once_with("key", "value")
        mock_client.setex.assert_not_called()

    def test_set_swallows_exception(self):
        backend = RedisCacheBackend()
        mock_client = MagicMock()
        mock_client.set.side_effect = ConnectionError("fail")
        backend._client = mock_client

        backend.set("key", "value")

    def test_set_with_ttl_swallows_exception(self):
        backend = RedisCacheBackend()
        mock_client = MagicMock()
        mock_client.setex.side_effect = ConnectionError("fail")
        backend._client = mock_client

        backend.set("key", "value", ttl_seconds=30)


class TestGetCacheBackend:
    def test_returns_redis_backend(self):
        backend = get_cache_backend()
        assert isinstance(backend, RedisCacheBackend)
        assert backend._redis_url == "redis://localhost:6379/0"

    def test_returns_redis_backend_custom_url(self):
        backend = get_cache_backend(redis_url="redis://custom:6380/2")
        assert isinstance(backend, RedisCacheBackend)
        assert backend._redis_url == "redis://custom:6380/2"
