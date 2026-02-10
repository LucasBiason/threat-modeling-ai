"""Unit tests for app.threat_analysis.agents.dread.agent."""

import asyncio
from unittest.mock import AsyncMock, patch

from app.config import get_settings
from app.threat_analysis.agents.dread.agent import DreadAgent, _validate_dread_result


def test_validate_dread_result():
    assert _validate_dread_result([1, 2]) is True
    assert _validate_dread_result("not list") is False


def test_analyze_empty_threats_returns_empty():
    with patch("app.threat_analysis.agents.dread.agent.LLMCacheService"):
        agent = DreadAgent(get_settings())
    result = asyncio.run(agent.analyze([]))
    assert result == []


def test_analyze_success_returns_scored_threats():
    threats = [
        {
            "component_id": "c1",
            "threat_type": "Spoofing",
            "description": "d",
            "mitigation": "m",
        }
    ]
    scored = [
        {
            "component_id": "c1",
            "threat_type": "Spoofing",
            "description": "d",
            "mitigation": "m",
            "dread_score": 5.0,
        }
    ]
    with (
        patch("app.threat_analysis.agents.dread.agent.LLMCacheService"),
        patch(
            "app.threat_analysis.agents.dread.agent.run_text_with_fallback",
            new_callable=AsyncMock,
            return_value=scored,
        ),
    ):
        agent = DreadAgent(get_settings())
        result = asyncio.run(agent.analyze(threats))
    assert result == scored
    assert result[0]["dread_score"] == 5.0


def test_analyze_error_returns_original_threats():
    threats = [
        {
            "component_id": "c1",
            "threat_type": "Spoofing",
            "description": "d",
            "mitigation": "m",
        }
    ]
    with (
        patch("app.threat_analysis.agents.dread.agent.LLMCacheService"),
        patch(
            "app.threat_analysis.agents.dread.agent.run_text_with_fallback",
            new_callable=AsyncMock,
            return_value={"error": "All providers failed"},
        ),
    ):
        agent = DreadAgent(get_settings())
        result = asyncio.run(agent.analyze(threats))
    assert result == threats


def test_analyze_clamps_dread_score():
    threats = [
        {
            "component_id": "c1",
            "threat_type": "S",
            "description": "d",
            "mitigation": "m",
        }
    ]
    scored = [
        {
            "component_id": "c1",
            "threat_type": "S",
            "description": "d",
            "mitigation": "m",
            "dread_score": 99,
        }
    ]
    with (
        patch("app.threat_analysis.agents.dread.agent.LLMCacheService"),
        patch(
            "app.threat_analysis.agents.dread.agent.run_text_with_fallback",
            new_callable=AsyncMock,
            return_value=scored,
        ),
    ):
        agent = DreadAgent(get_settings())
        result = asyncio.run(agent.analyze(threats))
    assert result[0]["dread_score"] == 10
