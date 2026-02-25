"""Unit tests for app.threat_analysis.llm.openai_connection."""

from unittest.mock import MagicMock, patch

from app.threat_analysis.llm.openai_connection import OpenAIConnection


def _make_settings(openai_api_key="test-key"):
    s = MagicMock()
    s.openai_api_key = openai_api_key
    s.fallback_model = "gpt-4o"
    s.llm_temperature = 0.0
    return s


class TestOpenAIConnectionProperties:
    def test_name(self):
        conn = OpenAIConnection(_make_settings())
        assert conn.name == "OpenAI"

    def test_init_stores_settings(self):
        settings = _make_settings()
        conn = OpenAIConnection(settings)
        assert conn._settings is settings
        assert conn._llm is None

    def test_is_configured_with_key(self):
        conn = OpenAIConnection(_make_settings("my-key"))
        assert conn.is_configured() is True

    def test_is_configured_without_key(self):
        conn = OpenAIConnection(_make_settings(None))
        assert conn.is_configured() is False

    def test_is_configured_empty_key(self):
        conn = OpenAIConnection(_make_settings(""))
        assert conn.is_configured() is False


class TestEnsureLLM:
    @patch("app.threat_analysis.llm.openai_connection.ChatOpenAI")
    def test_success(self, mock_chat):
        mock_llm = MagicMock()
        mock_chat.return_value = mock_llm
        conn = OpenAIConnection(_make_settings())
        result = conn._ensure_llm()
        assert result is mock_llm
        assert conn._llm is mock_llm

    def test_not_configured(self):
        conn = OpenAIConnection(_make_settings(None))
        result = conn._ensure_llm()
        assert result is None

    @patch("app.threat_analysis.llm.openai_connection.ChatOpenAI")
    def test_init_error(self, mock_chat):
        mock_chat.side_effect = RuntimeError("init failed")
        conn = OpenAIConnection(_make_settings())
        result = conn._ensure_llm()
        assert result is None

    @patch("app.threat_analysis.llm.openai_connection.ChatOpenAI")
    def test_cached(self, mock_chat):
        sentinel = MagicMock()
        conn = OpenAIConnection(_make_settings())
        conn._llm = sentinel
        result = conn._ensure_llm()
        assert result is sentinel
        mock_chat.assert_not_called()


class TestParseJson:
    def test_valid_json_object(self):
        conn = OpenAIConnection(_make_settings())
        result = conn._parse_json('{"key": "value"}')
        assert result == {"key": "value"}

    def test_valid_json_array(self):
        conn = OpenAIConnection(_make_settings())
        result = conn._parse_json('[{"a": 1}]')
        assert result == [{"a": 1}]

    def test_json_in_code_block_stripped(self):
        conn = OpenAIConnection(_make_settings())
        text = '```json\n{"x": 1}\n```'
        result = conn._parse_json(text)
        assert result == {"x": 1}

    def test_empty_response(self):
        conn = OpenAIConnection(_make_settings())
        result = conn._parse_json("")
        assert result["error_type"] == "empty"
        assert result["service"] == "OpenAI"

    def test_none_response(self):
        conn = OpenAIConnection(_make_settings())
        result = conn._parse_json(None)
        assert result["error_type"] == "empty"

    def test_invalid_json(self):
        conn = OpenAIConnection(_make_settings())
        result = conn._parse_json("no json here at all")
        assert result["error_type"] == "invalid_json"
        assert result["service"] == "OpenAI"

    def test_json_with_surrounding_text(self):
        conn = OpenAIConnection(_make_settings())
        result = conn._parse_json('Result: {"threats": []} end')
        assert result == {"threats": []}

    def test_array_appears_first(self):
        conn = OpenAIConnection(_make_settings())
        result = conn._parse_json('[1, 2] then {"a": 1}')
        assert result == [1, 2]

    def test_invalid_json_inside_brackets(self):
        conn = OpenAIConnection(_make_settings())
        text = "{not: valid json}"
        result = conn._parse_json(text)
        assert result["error_type"] == "invalid_json"
