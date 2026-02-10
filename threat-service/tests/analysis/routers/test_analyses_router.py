"""Unit tests for app.analysis.routers.analysis_router."""

import io
import uuid
from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest

from app.analysis.controllers.analysis_controller import AnalysisController
from app.analysis.routers.analysis_router import get_controller
from app.analysis.schemas import (
    AnalysisCreateResponse,
    AnalysisDetailResponse,
    AnalysisListResponse,
    AnalysisStatusEnum,
)
from app.main import app

SAMPLE_PNG = (
    b"\x89PNG\r\n\x1a\n"
    b"\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde"
    b"\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82"
)


@pytest.fixture
def mock_controller():
    """Mock AnalysisController for unit tests (no DB needed)."""
    ctrl = MagicMock(spec=AnalysisController)
    return ctrl


@pytest.fixture
def client_mocked(mock_controller, client_no_db):
    """Test client with mocked controller dependency (no PostgreSQL)."""

    def override_get_controller():
        return mock_controller

    app.dependency_overrides[get_controller] = override_get_controller
    try:
        yield client_no_db
    finally:
        app.dependency_overrides.pop(get_controller, None)


class TestAnalysesRouterUnit:
    """Unit tests with mocked controller (no PostgreSQL)."""

    def test_create_analysis(self, client_mocked, mock_controller):
        """POST /analyses delegates to controller and returns 201."""
        mock_controller.create_analysis.return_value = AnalysisCreateResponse(
            id=str(uuid.uuid4()),
            code="TMA-001",
            status=AnalysisStatusEnum.EM_ABERTO,
            created_at=datetime.now(timezone.utc),
            image_url="/api/v1/analyses/abc/image",
        )
        response = client_mocked.post(
            "/api/v1/analyses",
            files={"file": ("diagram.png", io.BytesIO(SAMPLE_PNG), "image/png")},
        )
        assert response.status_code == 201
        mock_controller.create_analysis.assert_called_once()
        data = response.json()
        assert data["code"] == "TMA-001"
        assert data["status"] == "EM_ABERTO"

    def test_list_analyses_empty(self, client_mocked, mock_controller):
        """GET /analyses returns paginated response (Page) with empty items."""
        mock_controller.list_analyses.return_value = []
        response = client_mocked.get("/api/v1/analyses")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert data["items"] == []
        assert data["total"] == 0

    def test_list_analyses_with_filter(self, client_mocked, mock_controller):
        """GET /analyses with status filter returns paginated Page."""
        mock_controller.list_analyses.return_value = [
            AnalysisListResponse(
                id=str(uuid.uuid4()),
                code="TMA-001",
                status=AnalysisStatusEnum.EM_ABERTO,
                created_at=datetime.now(timezone.utc),
                image_url=None,
            )
        ]
        response = client_mocked.get("/api/v1/analyses?status=EM_ABERTO")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert len(data["items"]) == 1
        assert data["items"][0]["code"] == "TMA-001"
        assert data["total"] == 1

    def test_get_analysis_detail(self, client_mocked, mock_controller):
        """GET /analyses/{id} returns detail."""
        aid = uuid.uuid4()
        mock_controller.get_analysis_or_404.return_value = AnalysisDetailResponse(
            id=str(aid),
            code="TMA-001",
            status=AnalysisStatusEnum.ANALISADO,
            created_at=datetime.now(timezone.utc),
            result={"risk_level": "Médio"},
        )
        response = client_mocked.get(f"/api/v1/analyses/{aid}")
        assert response.status_code == 200
        assert response.json()["code"] == "TMA-001"

    def test_get_analysis_image_404(self, client_mocked, mock_controller):
        """GET /analyses/{id}/image returns 404 when not found."""
        mock_controller.get_image_path_and_media_type.return_value = (None, None)
        response = client_mocked.get(f"/api/v1/analyses/{uuid.uuid4()}/image")
        assert response.status_code == 404

    def test_get_analysis_image_success(self, client_mocked, mock_controller, tmp_path):
        """GET /analyses/{id}/image returns file when exists."""
        img = tmp_path / "x.png"
        img.write_bytes(SAMPLE_PNG)
        mock_controller.get_image_path_and_media_type.return_value = (img, "image/png")
        response = client_mocked.get(f"/api/v1/analyses/{uuid.uuid4()}/image")
        assert response.status_code == 200
        assert response.headers["content-type"] == "image/png"

    def test_get_analysis_logs_404(self, client_mocked, mock_controller):
        """GET /analyses/{id}/logs returns 404 when analysis not found."""
        mock_controller.get_processing_logs.return_value = None
        response = client_mocked.get(f"/api/v1/analyses/{uuid.uuid4()}/logs")
        assert response.status_code == 404

    def test_get_analysis_logs_success(self, client_mocked, mock_controller):
        """GET /analyses/{id}/logs returns logs JSON."""
        mock_controller.get_processing_logs.return_value = "log line 1\nlog line 2"
        response = client_mocked.get(f"/api/v1/analyses/{uuid.uuid4()}/logs")
        assert response.status_code == 200
        assert response.json()["logs"] == "log line 1\nlog line 2"


class TestAnalysesRouterIntegration:
    """Integration tests (require PostgreSQL + client fixture)."""

    def test_create_analysis(self, client):
        """POST /analyses creates analysis and returns 201."""
        response = client.post(
            "/api/v1/analyses",
            files={"file": ("diagram.png", io.BytesIO(SAMPLE_PNG), "image/png")},
        )
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert "code" in data
        assert data["status"] == "EM_ABERTO"

    def test_list_analyses_empty(self, client):
        """GET /analyses returns paginated Page (items may be empty)."""
        response = client.get("/api/v1/analyses")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert isinstance(data["items"], list)
