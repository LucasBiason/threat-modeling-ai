"""Unit tests for app.threat_analysis.llm.fallback."""

import asyncio
from unittest.mock import MagicMock

from app.threat_analysis.llm.base import LLMConnection
from app.threat_analysis.llm.fallback import (
    is_error_result,
    run_text_with_fallback,
    run_vision_with_fallback,
)


def test_is_error_result():
    assert is_error_result({"error": "x"}) is True
    assert is_error_result({"components": []}) is False


class MockConnection(LLMConnection):
    def __init__(
        self, settings, name="Mock", configured=True, result=None, raise_err=None
    ):
        self.settings = settings
        self._name = name
        self._configured = configured
        self._result = result or {"components": [], "connections": []}
        self._raise = raise_err

    @property
    def name(self) -> str:
        return self._name

    def is_configured(self) -> bool:
        return self._configured

    def _ensure_llm(self):
        return None

    def _parse_json(self, text: str) -> dict:
        return self._result

    async def invoke_vision(self, prompt: str, image_bytes: bytes, **kwargs) -> dict:
        if self._raise:
            raise self._raise
        return self._result

    async def invoke_text(self, messages: list, **kwargs) -> dict:
        if self._raise:
            raise self._raise
        return self._result


class TestRunVisionWithFallback:
    def test_cache_hit(self):
        cached = {"components": [{"id": "1"}]}
        cache_get = MagicMock(return_value=cached)
        result = asyncio.run(
            run_vision_with_fallback(
                connections=[],
                settings=MagicMock(),
                prompt="p",
                image_bytes=b"x",
                cache_get=cache_get,
                cache_set=MagicMock(),
                cache_key_prefix="diagram",
            )
        )
        assert result == cached
        cache_get.assert_called_once()

    def test_first_connection_succeeds(self):
        valid = {"components": [{"id": "1"}], "connections": []}

        class MockOk(MockConnection):
            def __init__(self, s):
                super().__init__(s, result=valid)

        result = asyncio.run(
            run_vision_with_fallback(
                connections=[MockOk],
                settings=MagicMock(),
                prompt="p",
                image_bytes=b"x",
            )
        )
        assert result == valid

    def test_all_fail_returns_aggregated_errors(self):
        class MockFail(MockConnection):
            def __init__(self, s):
                super().__init__(s, result={"error": "failed"}, configured=True)

        result = asyncio.run(
            run_vision_with_fallback(
                connections=[MockFail],
                settings=MagicMock(),
                prompt="p",
                image_bytes=b"x",
            )
        )
        assert "error" in result
        assert "All LLM providers failed" in result["error"]
        assert "engine_errors" in result


class TestRunTextWithFallback:
    def test_cache_hit(self):
        cached = [{"threat_type": "Spoofing"}]
        cache_get = MagicMock(return_value=cached)
        messages = [{"role": "user", "content": "hello"}]
        result = asyncio.run(
            run_text_with_fallback(
                connections=[],
                settings=MagicMock(),
                messages=messages,
                cache_get=cache_get,
                cache_set=MagicMock(),
                cache_key_prefix="text",
            )
        )
        assert result == cached
        cache_get.assert_called_once()

    def test_first_connection_succeeds(self):
        valid = [{"threat_type": "Spoofing", "description": "d"}]

        class MockOk(MockConnection):
            def __init__(self, s):
                super().__init__(s, result=valid)

        result = asyncio.run(
            run_text_with_fallback(
                connections=[MockOk],
                settings=MagicMock(),
                messages=[{"role": "user", "content": "analyze"}],
            )
        )
        assert result == valid

    def test_all_fail_returns_aggregated_errors(self):
        class MockFail(MockConnection):
            def __init__(self, s):
                super().__init__(s, result={"error": "failed"}, configured=True)

        result = asyncio.run(
            run_text_with_fallback(
                connections=[MockFail],
                settings=MagicMock(),
                messages=[{"role": "user", "content": "x"}],
            )
        )
        assert "error" in result
        assert "All LLM providers failed" in result["error"]
        assert "engine_errors" in result
