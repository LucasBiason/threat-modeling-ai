"""Unit tests for app.threat_analysis.llm.base (LLMConnection ABC)."""

import asyncio
import base64
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

from app.threat_analysis.llm.base import LLMConnection


class ConcreteLLM(LLMConnection):
    """Minimal concrete subclass for testing the ABC methods."""

    def __init__(self, name="TestLLM", configured=True, llm=None, parse_result=None):
        self._name = name
        self._configured = configured
        self._llm = llm
        self._parse_result = parse_result or {"result": "ok"}

    @property
    def name(self) -> str:
        return self._name

    def is_configured(self) -> bool:
        return self._configured

    def _ensure_llm(self) -> Any:
        return self._llm

    def _parse_json(self, text: str) -> dict[str, Any]:
        return self._parse_result


class TestAbstractMethodBodies:
    """Cover the `pass` bodies in abstract methods via super() calls."""

    def test_abstract_name_body(self):
        result = LLMConnection.name.fget(ConcreteLLM())
        assert result is None

    def test_abstract_is_configured_body(self):
        result = LLMConnection.is_configured(ConcreteLLM())
        assert result is None

    def test_abstract_ensure_llm_body(self):
        result = LLMConnection._ensure_llm(ConcreteLLM())
        assert result is None

    def test_abstract_parse_json_body(self):
        result = LLMConnection._parse_json(ConcreteLLM(), "text")
        assert result is None


class TestInvoke:
    def test_success(self):
        parsed = {"threats": []}
        conn = ConcreteLLM(parse_result=parsed)
        mock_response = MagicMock()
        mock_response.content = '{"threats": []}'

        async def fake_coro():
            return mock_response

        result = asyncio.run(conn._invoke(fake_coro()))
        assert result == parsed

    def test_api_key_error(self):
        conn = ConcreteLLM()

        async def fail_coro():
            raise ValueError("Invalid API key provided")

        result = asyncio.run(conn._invoke(fail_coro()))
        assert result["error_type"] == "invalid_api_key"
        assert result["service"] == "TestLLM"

    def test_401_error(self):
        conn = ConcreteLLM()

        async def fail_coro():
            raise RuntimeError("HTTP 401 Unauthorized")

        result = asyncio.run(conn._invoke(fail_coro()))
        assert result["error_type"] == "invalid_api_key"

    def test_generic_error(self):
        conn = ConcreteLLM()

        async def fail_coro():
            raise RuntimeError("Connection refused")

        result = asyncio.run(conn._invoke(fail_coro()))
        assert result["error_type"] == "processing_error"
        assert result["service"] == "TestLLM"
        assert "Connection refused" in result["error"]

    def test_response_without_content_attr(self):
        parsed = {"data": "x"}
        conn = ConcreteLLM(parse_result=parsed)

        async def fake_coro():
            return "raw string response"

        result = asyncio.run(conn._invoke(fake_coro()))
        assert result == parsed

    def test_none_content_length(self):
        parsed = {"ok": True}
        conn = ConcreteLLM(parse_result=parsed)
        mock_response = MagicMock()
        mock_response.content = None

        async def fake_coro():
            return mock_response

        result = asyncio.run(conn._invoke(fake_coro()))
        assert result == parsed


class TestNotConfiguredResponse:
    def test_returns_config_error(self):
        conn = ConcreteLLM(name="MyLLM")
        resp = conn._not_configured_response()
        assert resp["error"] == "MyLLM not configured"
        assert resp["error_type"] == "config"
        assert resp["service"] == "MyLLM"


class TestInvokeVision:
    def test_success(self):
        parsed = {"components": []}
        mock_llm = MagicMock()
        mock_llm.ainvoke = AsyncMock(return_value=MagicMock(content='{"components": []}'))
        conn = ConcreteLLM(llm=mock_llm, parse_result=parsed)

        result = asyncio.run(conn.invoke_vision("analyze this", b"\x89PNG"))
        assert result == parsed
        mock_llm.ainvoke.assert_called_once()
        call_args = mock_llm.ainvoke.call_args[0][0]
        assert len(call_args) == 1
        msg = call_args[0]
        assert len(msg.content) == 2
        assert msg.content[0]["type"] == "text"
        assert msg.content[1]["type"] == "image_url"
        img_b64 = base64.b64encode(b"\x89PNG").decode("utf-8")
        assert img_b64 in msg.content[1]["image_url"]["url"]

    def test_not_configured(self):
        conn = ConcreteLLM(llm=None)
        result = asyncio.run(conn.invoke_vision("analyze", b"img"))
        assert result["error_type"] == "config"


class TestInvokeText:
    def test_success(self):
        parsed = {"threats": ["x"]}
        mock_llm = MagicMock()
        mock_llm.ainvoke = AsyncMock(return_value=MagicMock(content="{}"))
        conn = ConcreteLLM(llm=mock_llm, parse_result=parsed)

        messages = [{"role": "user", "content": "hello"}]
        result = asyncio.run(conn.invoke_text(messages))
        assert result == parsed

    def test_not_configured(self):
        conn = ConcreteLLM(llm=None)
        messages = [{"role": "user", "content": "hi"}]
        result = asyncio.run(conn.invoke_text(messages))
        assert result["error_type"] == "config"

    def test_system_and_user_messages(self):
        parsed = {"ok": True}
        mock_llm = MagicMock()
        mock_llm.ainvoke = AsyncMock(return_value=MagicMock(content="{}"))
        conn = ConcreteLLM(llm=mock_llm, parse_result=parsed)

        messages = [
            {"role": "system", "content": "You are helpful"},
            {"role": "user", "content": "Analyze this"},
        ]
        result = asyncio.run(conn.invoke_text(messages))
        assert result == parsed
        call_args = mock_llm.ainvoke.call_args[0][0]
        assert len(call_args) == 2
        from langchain_core.messages import SystemMessage, HumanMessage
        assert isinstance(call_args[0], SystemMessage)
        assert isinstance(call_args[1], HumanMessage)
