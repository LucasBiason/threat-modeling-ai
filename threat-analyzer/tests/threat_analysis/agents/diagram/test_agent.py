"""Unit tests for app.threat_analysis.agents.diagram.agent."""

import asyncio
from unittest.mock import AsyncMock, patch

from app.config import get_settings
from app.threat_analysis.agents.diagram.agent import (
    DiagramAgent,
    _validate_diagram_result,
)


def test_analyze_returns_fallback_on_error():
    with patch(
        "app.threat_analysis.agents.diagram.agent.run_vision_with_fallback",
        new_callable=AsyncMock,
        return_value={"error": "All LLM providers failed"},
    ):
        settings = get_settings()
        agent = DiagramAgent(settings)
        result = asyncio.run(agent.analyze(b"fake image"))
        assert result["model"] == "Fallback/Error"
        assert "components" in result
        assert len(result["components"]) == 1
        assert result["components"][0]["id"] == "unknown_1"


def test_analyze_returns_valid_result():
    valid = {
        "model": "Gemini",
        "components": [{"id": "c1", "type": "Server", "name": "Web"}],
        "connections": [],
        "boundaries": [],
    }
    with patch(
        "app.threat_analysis.agents.diagram.agent.run_vision_with_fallback",
        new_callable=AsyncMock,
        return_value=valid,
    ):
        settings = get_settings()
        agent = DiagramAgent(settings)
        result = asyncio.run(agent.analyze(b"fake image"))
        assert result == valid
        assert result["model"] == "Gemini"


def test_validate_diagram_result_not_dict():
    assert _validate_diagram_result("not a dict") is False


def test_validate_diagram_result_contains_error():
    assert _validate_diagram_result({"error": "timeout"}) is False


def test_validate_diagram_result_components_not_list():
    assert _validate_diagram_result({"components": "not a list"}) is False


def test_validate_diagram_result_valid():
    assert (
        _validate_diagram_result(
            {
                "components": [{"id": "c1", "type": "Server", "name": "API"}],
                "connections": [],
            }
        )
        is True
    )
