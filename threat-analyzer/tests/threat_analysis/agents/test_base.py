"""Unit tests for app.threat_analysis.agents.base (via DiagramAgent as concrete subclass)."""

from unittest.mock import patch

import pytest

from app.config import get_settings
from app.threat_analysis.agents.diagram.agent import DiagramAgent
from app.threat_analysis.exceptions import JSONParsingError
from app.threat_analysis.schemas.component import Component


class TestBaseAgentParseJson:
    """Test BaseAgent.parse_json_response and _extract_json_content."""

    def test_parse_json_response_valid(self):
        with patch("app.threat_analysis.agents.diagram.agent.LLMCacheService"):
            agent = DiagramAgent(get_settings())
        assert agent.parse_json_response('{"a": 1}') == {"a": 1}

    def test_parse_json_response_empty_returns_default(self):
        with patch("app.threat_analysis.agents.diagram.agent.LLMCacheService"):
            agent = DiagramAgent(get_settings())
        assert agent.parse_json_response("", default=[]) == []

    def test_parse_json_response_empty_raise_on_error(self):
        with patch("app.threat_analysis.agents.diagram.agent.LLMCacheService"):
            agent = DiagramAgent(get_settings())
        with pytest.raises(JSONParsingError) as exc_info:
            agent.parse_json_response("", raise_on_error=True)
        assert "empty" in str(exc_info.value.message).lower()

    def test_parse_json_response_invalid_json_returns_default(self):
        with patch("app.threat_analysis.agents.diagram.agent.LLMCacheService"):
            agent = DiagramAgent(get_settings())
        assert agent.parse_json_response("not json", default=None) is None

    def test_parse_json_response_invalid_json_raise_on_error(self):
        with patch("app.threat_analysis.agents.diagram.agent.LLMCacheService"):
            agent = DiagramAgent(get_settings())
        with pytest.raises(JSONParsingError):
            agent.parse_json_response("not json", raise_on_error=True)

    def test_extract_json_content_json_code_block(self):
        with patch("app.threat_analysis.agents.diagram.agent.LLMCacheService"):
            agent = DiagramAgent(get_settings())
        out = agent._extract_json_content('```json\n{"x": 1}\n```')
        assert out.strip() == '{"x": 1}'

    def test_extract_json_content_generic_code_block(self):
        with patch("app.threat_analysis.agents.diagram.agent.LLMCacheService"):
            agent = DiagramAgent(get_settings())
        out = agent._extract_json_content('```\n{"y": 2}\n```')
        assert out.strip() == '{"y": 2}'

    def test_extract_json_content_raw_object(self):
        with patch("app.threat_analysis.agents.diagram.agent.LLMCacheService"):
            agent = DiagramAgent(get_settings())
        out = agent._extract_json_content('  {"z": 3}  ')
        assert out == '{"z": 3}'

    def test_extract_json_content_raw_array(self):
        with patch("app.threat_analysis.agents.diagram.agent.LLMCacheService"):
            agent = DiagramAgent(get_settings())
        out = agent._extract_json_content("  [1, 2]  ")
        assert out == "[1, 2]"

    def test_extract_json_content_object_with_escaped_quote(self):
        """Covers in_string and escape_next branches in _extract_json_content."""
        with patch("app.threat_analysis.agents.diagram.agent.LLMCacheService"):
            agent = DiagramAgent(get_settings())
        # Content with \" inside string so depth loop hits in_string and escape_next
        raw = '  {"msg": "say \\"hi\\""}  '
        out = agent._extract_json_content(raw)
        assert out == '{"msg": "say \\"hi\\""}'


class TestBaseAgentValidateWithSchema:
    """Test BaseAgent.validate_with_schema."""

    def test_validate_with_schema_dict_valid(self):
        with patch("app.threat_analysis.agents.diagram.agent.LLMCacheService"):
            agent = DiagramAgent(get_settings())
        data = {"id": "c1", "type": "Server", "name": "API", "description": None}
        result = agent.validate_with_schema(data, Component)
        assert result is not None
        assert result.id == "c1"

    def test_validate_with_schema_list_valid(self):
        with patch("app.threat_analysis.agents.diagram.agent.LLMCacheService"):
            agent = DiagramAgent(get_settings())
        data = [{"id": "c1", "type": "Server", "name": "A", "description": None}]
        result = agent.validate_with_schema(data, Component)
        assert result is not None
        assert len(result) == 1
        assert result[0].id == "c1"

    def test_validate_with_schema_invalid_returns_none(self, caplog):
        with patch("app.threat_analysis.agents.diagram.agent.LLMCacheService"):
            agent = DiagramAgent(get_settings())
        result = agent.validate_with_schema({"id": 123, "type": 1}, Component)
        assert result is None
        assert "Schema validation failed" in caplog.text
