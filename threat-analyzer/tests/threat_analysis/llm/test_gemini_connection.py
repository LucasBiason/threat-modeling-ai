"""Unit tests for app.threat_analysis.llm.gemini_connection."""

from unittest.mock import MagicMock, patch

from app.threat_analysis.llm.gemini_connection import GeminiConnection


def _make_settings(google_api_key="test-key"):
    s = MagicMock()
    s.google_api_key = google_api_key
    s.primary_model = "gemini-pro"
    s.llm_temperature = 0.0
    return s


class TestGeminiConnectionProperties:
    def test_name(self):
        conn = GeminiConnection(_make_settings())
        assert conn.name == "Gemini"

    def test_init_stores_settings(self):
        settings = _make_settings()
        conn = GeminiConnection(settings)
        assert conn._settings is settings
        assert conn._llm is None

    def test_is_configured_with_key(self):
        conn = GeminiConnection(_make_settings("my-key"))
        assert conn.is_configured() is True

    def test_is_configured_without_key(self):
        conn = GeminiConnection(_make_settings(None))
        assert conn.is_configured() is False

    def test_is_configured_empty_key(self):
        conn = GeminiConnection(_make_settings(""))
        assert conn.is_configured() is False


class TestEnsureLLM:
    @patch("app.threat_analysis.llm.gemini_connection.ChatGoogleGenerativeAI")
    def test_success(self, mock_chat):
        mock_llm = MagicMock()
        mock_chat.return_value = mock_llm
        conn = GeminiConnection(_make_settings())
        result = conn._ensure_llm()
        assert result is mock_llm
        assert conn._llm is mock_llm

    def test_not_configured(self):
        conn = GeminiConnection(_make_settings(None))
        result = conn._ensure_llm()
        assert result is None

    @patch("app.threat_analysis.llm.gemini_connection.ChatGoogleGenerativeAI")
    def test_init_error(self, mock_chat):
        mock_chat.side_effect = RuntimeError("init failed")
        conn = GeminiConnection(_make_settings())
        result = conn._ensure_llm()
        assert result is None

    @patch("app.threat_analysis.llm.gemini_connection.ChatGoogleGenerativeAI")
    def test_cached(self, mock_chat):
        sentinel = MagicMock()
        conn = GeminiConnection(_make_settings())
        conn._llm = sentinel
        result = conn._ensure_llm()
        assert result is sentinel
        mock_chat.assert_not_called()


class TestParseJson:
    def test_valid_json_object(self):
        conn = GeminiConnection(_make_settings())
        result = conn._parse_json('{"key": "value"}')
        assert result == {"key": "value"}

    def test_valid_json_array(self):
        conn = GeminiConnection(_make_settings())
        result = conn._parse_json('[{"a": 1}]')
        assert result == [{"a": 1}]

    def test_json_in_code_block(self):
        conn = GeminiConnection(_make_settings())
        text = '```json\n{"x": 1}\n```'
        result = conn._parse_json(text)
        assert result == {"x": 1}

    def test_empty_response(self):
        conn = GeminiConnection(_make_settings())
        result = conn._parse_json("")
        assert result["error_type"] == "empty"
        assert result["service"] == "Gemini"

    def test_none_response(self):
        conn = GeminiConnection(_make_settings())
        result = conn._parse_json(None)
        assert result["error_type"] == "empty"

    def test_invalid_json(self):
        conn = GeminiConnection(_make_settings())
        result = conn._parse_json("no json here at all")
        assert result["error_type"] == "invalid_json"
        assert result["service"] == "Gemini"

    def test_json_with_surrounding_text(self):
        conn = GeminiConnection(_make_settings())
        result = conn._parse_json('Here is the result: {"threats": []} done')
        assert result == {"threats": []}

    def test_array_appears_first(self):
        conn = GeminiConnection(_make_settings())
        result = conn._parse_json('[1, 2, 3] and then {"a": 1}')
        assert result == [1, 2, 3]

    def test_code_block_fallback_when_brackets_fail(self):
        conn = GeminiConnection(_make_settings())
        text = 'Some text ```json\n{"valid": true}\n``` more text'
        result = conn._parse_json(text)
        assert result == {"valid": True}

    def test_invalid_json_inside_brackets(self):
        conn = GeminiConnection(_make_settings())
        text = "{not: valid json content}"
        result = conn._parse_json(text)
        assert result["error_type"] == "invalid_json"

    def test_code_block_fallback_when_outer_brackets_wrap(self):
        """Brackets wrap the code block → bracket match fails → code block regex succeeds."""
        conn = GeminiConnection(_make_settings())
        text = '{ prefix ```json\n{"x": 1}\n``` suffix }'
        result = conn._parse_json(text)
        assert result == {"x": 1}

    def test_code_block_fallback_with_invalid_json_in_block(self):
        """Code block regex matches but JSON inside is invalid."""
        conn = GeminiConnection(_make_settings())
        text = '{ prefix ```json\nnot valid json\n``` suffix }'
        result = conn._parse_json(text)
        assert result["error_type"] == "invalid_json"
