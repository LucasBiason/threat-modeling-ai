"""Unit tests for app.threat_analysis.controllers.threat_analysis_controller."""

import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.config import get_settings
from app.threat_analysis.controllers.threat_analysis_controller import (
    ThreatAnalysisController,
)
from app.threat_analysis.exceptions import ThreatModelingError
from app.threat_analysis.schemas import AnalysisResponse, RiskLevel
from app.threat_analysis.service import ThreatModelService


@pytest.fixture
def sample_png():
    return (
        b"\x89PNG\r\n\x1a\n"
        b"\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde"
        b"\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82"
    )


class TestThreatAnalysisController:
    def test_analyze_success(self, sample_png):
        """Service run_full_analysis is mocked to avoid LLM calls."""
        settings = get_settings()
        mock_response = AnalysisResponse(
            model_used="test",
            components=[],
            connections=[],
            threats=[],
            risk_score=0.0,
            risk_level=RiskLevel.LOW,
            processing_time=None,
        )
        service = MagicMock(spec=ThreatModelService)
        service.run_full_analysis = AsyncMock(return_value=mock_response)
        controller = ThreatAnalysisController(service, settings)
        result = asyncio.run(controller.analyze(sample_png))
        assert result.model_used == "test"
        assert result.risk_level is not None

    def test_analyze_empty_raises(self):
        import asyncio

        settings = get_settings()
        service = MagicMock(spec=ThreatModelService)
        controller = ThreatAnalysisController(service, settings)
        with pytest.raises(ThreatModelingError) as exc_info:
            asyncio.run(controller.analyze(b""))
        assert "Empty" in str(exc_info.value)

    def test_analyze_too_large_raises(self, sample_png):
        import asyncio

        settings = get_settings()
        settings = type(settings)(**{**settings.model_dump(), "max_upload_size_mb": 0})
        service = MagicMock(spec=ThreatModelService)
        controller = ThreatAnalysisController(service, settings)
        large = sample_png * 1000
        with pytest.raises(ThreatModelingError):
            asyncio.run(controller.analyze(large))
