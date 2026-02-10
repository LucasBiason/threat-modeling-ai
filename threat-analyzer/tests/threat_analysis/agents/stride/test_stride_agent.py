"""Unit tests for app.threat_analysis.agents.stride.agent."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from app.config import get_settings
from app.threat_analysis.agents.stride.agent import StrideAgent, _validate_stride_result


def test_validate_stride_result():
    assert _validate_stride_result([{}]) is True
    assert _validate_stride_result("x") is False


def test_rag_service_no_path_returns_none():
    """RAGService.get_retriever() returns None when knowledge base path does not exist."""
    from app.services.rag_service import RAGService

    settings = get_settings()
    with patch.object(settings, "knowledge_base_path", None):
        with patch("app.services.rag_service._DEFAULT_RAG_DATA_DIR") as mock_rag:
            mock_rag.exists.return_value = False
            svc = RAGService(settings)
            result = svc.get_retriever()
    assert result is None


def test_analyze_success_returns_threats():
    diagram_data = {
        "components": [{"id": "c1", "type": "Server", "name": "API"}],
        "connections": [],
        "boundaries": [],
    }
    threats = [
        {
            "component_id": "c1",
            "threat_type": "Spoofing",
            "description": "d",
            "mitigation": "m",
        }
    ]
    with (
        patch("app.threat_analysis.agents.stride.agent.LLMCacheService"),
        patch("app.threat_analysis.agents.stride.agent.RAGService") as mock_rag,
        patch(
            "app.threat_analysis.agents.stride.agent.run_text_with_fallback",
            new_callable=AsyncMock,
            return_value=threats,
        ),
    ):
        mock_rag.return_value.get_retriever.return_value = None
        agent = StrideAgent(get_settings())
        result = asyncio.run(agent.analyze(diagram_data))
    assert result == threats


def test_analyze_error_returns_empty_list():
    diagram_data = {"components": [], "connections": [], "boundaries": []}
    with (
        patch("app.threat_analysis.agents.stride.agent.LLMCacheService"),
        patch("app.threat_analysis.agents.stride.agent.RAGService") as mock_rag,
        patch(
            "app.threat_analysis.agents.stride.agent.run_text_with_fallback",
            new_callable=AsyncMock,
            return_value={"error": "All failed"},
        ),
    ):
        mock_rag.return_value.get_retriever.return_value = None
        agent = StrideAgent(get_settings())
        result = asyncio.run(agent.analyze(diagram_data))
    assert result == []


def test_analyze_with_retriever_uses_rag_context():
    diagram_data = {"components": [], "connections": [], "boundaries": []}
    mock_retriever = MagicMock()
    mock_retriever.get_relevant_documents.return_value = [
        MagicMock(page_content="Spoofing: identity verification"),
    ]
    with (
        patch("app.threat_analysis.agents.stride.agent.LLMCacheService"),
        patch("app.threat_analysis.agents.stride.agent.RAGService") as mock_rag,
        patch(
            "app.threat_analysis.agents.stride.agent.run_text_with_fallback",
            new_callable=AsyncMock,
            return_value=[],
        ),
    ):
        mock_rag.return_value.get_retriever.return_value = mock_retriever
        agent = StrideAgent(get_settings())
        asyncio.run(agent.analyze(diagram_data))
    mock_retriever.get_relevant_documents.assert_called_once()


def test_format_components():
    with (
        patch("app.threat_analysis.agents.stride.agent.LLMCacheService"),
        patch("app.threat_analysis.agents.stride.agent.RAGService") as mock_rag,
    ):
        mock_rag.return_value.get_retriever.return_value = None
        agent = StrideAgent(get_settings())
    out = agent._format_components([{"id": "c1", "type": "Server", "name": "API"}])
    assert "c1" in out and "Server" in out and "API" in out
    assert agent._format_components([]) == "None identified"


def test_format_connections():
    with (
        patch("app.threat_analysis.agents.stride.agent.LLMCacheService"),
        patch("app.threat_analysis.agents.stride.agent.RAGService") as mock_rag,
    ):
        mock_rag.return_value.get_retriever.return_value = None
        agent = StrideAgent(get_settings())
    out = agent._format_connections([{"from": "a", "to": "b", "protocol": "HTTPS"}])
    assert "a" in out and "b" in out
    assert agent._format_connections([]) == "None identified"
