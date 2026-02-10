"""Unit tests for app.analysis.controllers.analysis_controller."""

import uuid
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

from app.analysis.controllers.analysis_controller import AnalysisController
from app.analysis.models import Analysis, AnalysisStatus
from app.analysis.schemas import AnalysisFilter


@pytest.fixture
def mock_db():
    """Mock SQLAlchemy session."""
    return MagicMock()


@pytest.fixture
def controller(mock_db):
    """AnalysisController with mocked repository."""
    return AnalysisController(mock_db)


@pytest.fixture
def sample_png():
    """Minimal valid PNG bytes."""
    return (
        b"\x89PNG\r\n\x1a\n"
        b"\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde"
        b"\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82"
    )


class TestAnalysisControllerCreate:
    """Tests for create_analysis."""

    def test_create_analysis_success(self, controller, mock_db, sample_png):
        """Create analysis returns response with id, code, status."""
        analysis = Analysis(
            id=uuid.uuid4(),
            code="TMA-001",
            image_path="x.png",
            status=AnalysisStatus.EM_ABERTO,
            created_at=datetime.now(timezone.utc),
        )
        with patch.object(controller._repository, "create", return_value=analysis):
            result = controller.create_analysis(sample_png, "diagram.png")
        assert result.id == str(analysis.id)
        assert result.code == "TMA-001"
        assert result.status.value == "EM_ABERTO"
        assert "/api/v1/analyses/" in result.image_url

    def test_create_analysis_invalid_content_type(self, controller):
        """Create with invalid content type raises 400."""
        with patch.object(
            controller, "_guess_content_type", return_value="application/pdf"
        ):
            with pytest.raises(HTTPException) as exc_info:
                controller.create_analysis(b"not an image", "foo.txt")
        assert exc_info.value.status_code == 400


class TestAnalysisControllerList:
    """Tests for list_analyses."""

    def test_list_analyses_empty(self, controller):
        """List returns empty list when no analyses."""
        with patch.object(controller._repository, "list_all", return_value=[]):
            result = controller.list_analyses(AnalysisFilter())
        assert result == []

    def test_list_analyses_with_items(self, controller):
        """List returns formatted responses."""
        a = Analysis(
            id=uuid.uuid4(),
            code="TMA-001",
            image_path="x.png",
            status=AnalysisStatus.EM_ABERTO,
            created_at=datetime.now(timezone.utc),
            result=None,
        )
        with patch.object(controller._repository, "list_all", return_value=[a]):
            result = controller.list_analyses(AnalysisFilter())
        assert len(result) == 1
        assert result[0].code == "TMA-001"


class TestAnalysisControllerGuessContentType:
    """Tests for _guess_content_type."""

    def test_guess_png(self, controller):
        """PNG magic bytes return image/png."""
        assert controller._guess_content_type(b"\x89PNG\r\n\x1a\nxxxx") == "image/png"

    def test_guess_jpeg(self, controller):
        """JPEG magic bytes return image/jpeg."""
        assert controller._guess_content_type(b"\xff\xd8\xff") == "image/jpeg"

    def test_guess_webp(self, controller):
        """WEBP magic bytes return image/webp."""
        data = b"xxxxxxxxWEBPxxxx"
        assert controller._guess_content_type(data) == "image/webp"

    def test_guess_default_png(self, controller):
        """Unknown format defaults to image/png."""
        assert controller._guess_content_type(b"??") == "image/png"


class TestAnalysisControllerGetAnalysis:
    """Tests for get_analysis and get_analysis_or_404."""

    def test_get_analysis_not_found(self, controller):
        """get_analysis returns None when not found."""
        with patch.object(controller._repository, "get_by_id", return_value=None):
            result = controller.get_analysis(uuid.uuid4())
        assert result is None

    def test_get_analysis_found(self, controller):
        """get_analysis returns detail when found."""
        aid = uuid.uuid4()
        a = Analysis(
            id=aid,
            code="TMA-001",
            image_path="x.png",
            status=AnalysisStatus.ANALISADO,
            created_at=datetime.now(timezone.utc),
            started_at=None,
            finished_at=None,
            result={"risk_level": "Médio"},
            processing_logs=None,
            error_message=None,
        )
        with patch.object(controller._repository, "get_by_id", return_value=a):
            result = controller.get_analysis(aid)
        assert result is not None
        assert result.code == "TMA-001"
        assert result.result == {"risk_level": "Médio"}

    def test_get_analysis_or_404_raises(self, controller):
        """get_analysis_or_404 raises 404 when not found."""
        with patch.object(controller._repository, "get_by_id", return_value=None):
            with pytest.raises(HTTPException) as exc_info:
                controller.get_analysis_or_404(uuid.uuid4())
        assert exc_info.value.status_code == 404


class TestAnalysisControllerImageAndLogs:
    """Tests for get_image_path and get_processing_logs."""

    def test_get_image_path_not_found(self, controller):
        """get_image_path returns None when not found."""
        with patch.object(controller._repository, "get_image_path", return_value=None):
            assert controller.get_image_path(uuid.uuid4()) is None

    def test_get_image_path_found(self, controller, tmp_path):
        """get_image_path returns path when found."""
        path = tmp_path / "x.png"
        path.write_bytes(b"\x89PNG")
        with patch.object(controller._repository, "get_image_path", return_value=path):
            result = controller.get_image_path(uuid.uuid4())
        assert result == path

    def test_get_image_path_and_media_type_not_found(self, controller):
        """get_image_path_and_media_type returns (None, None) when not found."""
        with patch.object(controller._repository, "get_image_path", return_value=None):
            path, media_type = controller.get_image_path_and_media_type(uuid.uuid4())
        assert path is None
        assert media_type is None

    def test_get_image_path_and_media_type_found(self, controller, tmp_path):
        """get_image_path_and_media_type returns (path, media_type) from suffix."""
        path = tmp_path / "x.png"
        path.write_bytes(b"\x89PNG")
        with patch.object(controller._repository, "get_image_path", return_value=path):
            p, mt = controller.get_image_path_and_media_type(uuid.uuid4())
        assert p == path
        assert mt == "image/png"
        path_jpg = tmp_path / "y.jpg"
        path_jpg.write_bytes(b"\xff\xd8")
        with patch.object(
            controller._repository, "get_image_path", return_value=path_jpg
        ):
            p2, mt2 = controller.get_image_path_and_media_type(uuid.uuid4())
        assert mt2 == "image/jpeg"

    def test_get_processing_logs_not_found(self, controller):
        """get_processing_logs returns None when analysis not found."""
        with patch.object(controller._repository, "get_by_id", return_value=None):
            assert controller.get_processing_logs(uuid.uuid4()) is None

    def test_get_processing_logs_found(self, controller):
        """get_processing_logs returns logs string."""
        a = MagicMock()
        a.processing_logs = "line1\nline2"
        with patch.object(controller._repository, "get_by_id", return_value=a):
            result = controller.get_processing_logs(uuid.uuid4())
        assert result == "line1\nline2"
