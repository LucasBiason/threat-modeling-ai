"""Unit tests for threat analysis router (app.routers.threat_model)."""

from io import BytesIO
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from app.config import get_settings
from app.main import app
from app.threat_analysis.schemas import AnalysisResponse, RiskLevel
from app.threat_analysis.service import ThreatModelService, get_threat_model_service


@pytest.fixture(autouse=True)
def override_service_with_mock():
    """Override dependency with a service whose run_full_analysis returns a fixed response (no LLM)."""
    mock_response = AnalysisResponse(
        model_used="test",
        components=[],
        connections=[],
        threats=[],
        risk_score=0.0,
        risk_level=RiskLevel.LOW,
        processing_time=None,
    )
    mock_service = ThreatModelService(get_settings())
    mock_service.run_full_analysis = AsyncMock(return_value=mock_response)

    def _get_service():
        return mock_service

    app.dependency_overrides[get_threat_model_service] = _get_service
    yield
    app.dependency_overrides.pop(get_threat_model_service, None)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def sample_png():
    return (
        b"\x89PNG\r\n\x1a\n"
        b"\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde"
        b"\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82"
    )


class TestAnalyzeEndpoint:
    def test_analyze_success(self, client, sample_png):
        r = client.post(
            "/api/v1/threat-model/analyze",
            files={"file": ("diagram.png", BytesIO(sample_png), "image/png")},
        )
        assert r.status_code == 200
        data = r.json()
        assert "components" in data
        assert "threats" in data
        assert "risk_level" in data

    def test_analyze_invalid_content_type(self, client, sample_png):
        r = client.post(
            "/api/v1/threat-model/analyze",
            files={"file": ("x.pdf", BytesIO(sample_png), "application/pdf")},
        )
        assert r.status_code == 400
        assert "Invalid file type" in r.json()["detail"]

    def test_analyze_empty_file_raises(self, client):
        r = client.post(
            "/api/v1/threat-model/analyze",
            files={"file": ("empty.png", BytesIO(b""), "image/png")},
        )
        assert r.status_code == 400
        data = r.json()
        assert "Empty" in data.get("detail", "")
