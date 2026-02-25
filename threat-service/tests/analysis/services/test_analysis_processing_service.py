"""Unit tests for app.analysis.services.analysis_processing_service."""

import uuid
from unittest.mock import MagicMock, patch

import pytest

from app.analysis.services.analysis_processing_service import (
    AnalysisProcessingService,
    _append_log,
    _fail_analysis,
)
from app.analysis.services.analysis_service import AnalysisServiceError


@pytest.fixture
def mock_db():
    return MagicMock()


@pytest.fixture
def service(mock_db):
    with patch(
        "app.analysis.services.analysis_processing_service.AnalysisRepository"
    ), patch(
        "app.analysis.services.analysis_processing_service.NotificationRepository"
    ):
        svc = AnalysisProcessingService(mock_db)
        yield svc


class TestHelpers:
    """Tests for module-level helper functions."""

    def test_append_log(self):
        """_append_log delegates to repo."""
        repo = MagicMock()
        aid = uuid.uuid4()
        _append_log(repo, aid, "hello")
        repo.append_processing_log.assert_called_once_with(aid, "hello")

    def test_fail_analysis(self):
        """_fail_analysis logs, marks failed, returns error dict."""
        repo = MagicMock()
        aid = uuid.uuid4()
        result = _fail_analysis(repo, aid, str(aid), "some error")
        assert result == {"error": "some error", "analysis_id": str(aid)}
        repo.append_processing_log.assert_called_once()
        repo.mark_failed.assert_called_once()

    def test_fail_analysis_with_log_message(self):
        """_fail_analysis uses log_message when provided."""
        repo = MagicMock()
        aid = uuid.uuid4()
        _fail_analysis(repo, aid, str(aid), "error", log_message="custom log")
        repo.append_processing_log.assert_called_once_with(aid, "custom log")


class TestAnalysisProcessingService:
    """Tests for AnalysisProcessingService.process."""

    def test_process_analysis_not_found(self, service):
        """Returns error dict when analysis not found."""
        service._analysis_repo.get_by_id.return_value = None
        result = service.process(uuid.uuid4())
        assert "error" in result
        assert "not found" in result["error"].lower()

    def test_process_analysis_already_done(self, service):
        """Returns skipped when analysis already ANALISADO."""
        a = MagicMock()
        a.is_done = True
        a.is_failed = False
        service._analysis_repo.get_by_id.return_value = a
        result = service.process(uuid.uuid4())
        assert "skipped" in result

    def test_process_analysis_already_failed(self, service):
        """Returns skipped when analysis already FALHOU."""
        a = MagicMock()
        a.is_done = False
        a.is_failed = True
        service._analysis_repo.get_by_id.return_value = a
        result = service.process(uuid.uuid4())
        assert "skipped" in result

    def test_process_image_not_found(self, service):
        """Returns error when image file not found."""
        a = MagicMock()
        a.is_done = False
        a.is_failed = False
        a.is_open = True
        a.image_path = "x.png"
        service._analysis_repo.get_by_id.return_value = a
        service._analysis_repo.get_image_path.return_value = None
        result = service.process(uuid.uuid4())
        assert "error" in result
        assert "image" in result["error"].lower()

    def test_process_image_path_not_exists(self, service):
        """Returns error when image path exists but file doesn't."""
        a = MagicMock()
        a.is_done = False
        a.is_failed = False
        a.is_open = True
        a.image_path = "x.png"
        service._analysis_repo.get_by_id.return_value = a
        img_path = MagicMock()
        img_path.exists.return_value = False
        service._analysis_repo.get_image_path.return_value = img_path
        result = service.process(uuid.uuid4())
        assert "error" in result

    def test_process_success(self, service):
        """Returns success dict when threat-analyzer responds OK."""
        aid = uuid.uuid4()
        a = MagicMock()
        a.id = aid
        a.is_done = False
        a.is_failed = False
        a.is_open = True
        a.code = "TMA-001"
        a.image_path = "x.png"
        img_path = MagicMock()
        img_path.exists.return_value = True
        service._analysis_repo.get_by_id.return_value = a
        service._analysis_repo.get_image_path.return_value = img_path

        analyzer_result = {"threats": [{"name": "t1"}], "risk_level": "Médio"}
        with patch(
            "app.analysis.services.analysis_processing_service.AnalysisService"
        ) as mock_analysis_svc:
            mock_svc_instance = MagicMock()
            mock_svc_instance.analyze.return_value = analyzer_result
            mock_analysis_svc.return_value = mock_svc_instance
            result = service.process(aid)

        assert result["status"] == "ANALISADO"
        assert result["threat_count"] == 1
        assert result["risk_level"] == "Médio"
        service._analysis_repo.mark_analysed.assert_called_once()
        service._notification_repo.create.assert_called_once()

    def test_process_marks_processing_when_open(self, service):
        """Marks analysis as PROCESSANDO when status is EM_ABERTO."""
        aid = uuid.uuid4()
        a = MagicMock()
        a.id = aid
        a.is_done = False
        a.is_failed = False
        a.is_open = True
        a.code = "TMA-002"
        a.image_path = "y.png"
        img_path = MagicMock()
        img_path.exists.return_value = True
        service._analysis_repo.get_by_id.return_value = a
        service._analysis_repo.get_image_path.return_value = img_path

        with patch(
            "app.analysis.services.analysis_processing_service.AnalysisService"
        ) as mock_analysis_svc:
            mock_svc_instance = MagicMock()
            mock_svc_instance.analyze.return_value = {"threats": [], "risk_level": "Low"}
            mock_analysis_svc.return_value = mock_svc_instance
            service.process(aid)

        service._analysis_repo.mark_processing.assert_called_once()

    def test_process_skips_mark_processing_when_already_processing(self, service):
        """Does not mark processing if already PROCESSANDO."""
        aid = uuid.uuid4()
        a = MagicMock()
        a.id = aid
        a.is_done = False
        a.is_failed = False
        a.is_open = False
        a.code = "TMA-003"
        a.image_path = "z.png"
        img_path = MagicMock()
        img_path.exists.return_value = True
        service._analysis_repo.get_by_id.return_value = a
        service._analysis_repo.get_image_path.return_value = img_path

        with patch(
            "app.analysis.services.analysis_processing_service.AnalysisService"
        ) as mock_analysis_svc:
            mock_svc_instance = MagicMock()
            mock_svc_instance.analyze.return_value = {"threats": [], "risk_level": "Low"}
            mock_analysis_svc.return_value = mock_svc_instance
            service.process(aid)

        service._analysis_repo.mark_processing.assert_not_called()

    def test_process_analysis_service_error(self, service):
        """Returns error when AnalysisService raises AnalysisServiceError."""
        aid = uuid.uuid4()
        a = MagicMock()
        a.id = aid
        a.is_done = False
        a.is_failed = False
        a.is_open = True
        a.image_path = "x.png"
        img_path = MagicMock()
        img_path.exists.return_value = True
        service._analysis_repo.get_by_id.return_value = a
        service._analysis_repo.get_image_path.return_value = img_path

        with patch(
            "app.analysis.services.analysis_processing_service.AnalysisService"
        ) as mock_analysis_svc:
            mock_svc_instance = MagicMock()
            mock_svc_instance.analyze.side_effect = AnalysisServiceError("HTTP 500")
            mock_analysis_svc.return_value = mock_svc_instance
            result = service.process(aid)

        assert "error" in result
        service._analysis_repo.mark_failed.assert_called_once()

    def test_process_creates_notification_on_success(self, service):
        """Creates notification with analysis code and risk info on success."""
        aid = uuid.uuid4()
        a = MagicMock()
        a.id = aid
        a.is_done = False
        a.is_failed = False
        a.is_open = True
        a.code = "TMA-100"
        a.image_path = "img.png"
        img_path = MagicMock()
        img_path.exists.return_value = True
        service._analysis_repo.get_by_id.return_value = a
        service._analysis_repo.get_image_path.return_value = img_path

        with patch(
            "app.analysis.services.analysis_processing_service.AnalysisService"
        ) as mock_analysis_svc:
            mock_svc_instance = MagicMock()
            mock_svc_instance.analyze.return_value = {
                "threats": [{"a": 1}, {"b": 2}],
                "risk_level": "Alto",
            }
            mock_analysis_svc.return_value = mock_svc_instance
            result = service.process(aid)

        call_args = service._notification_repo.create.call_args
        assert "TMA-100" in call_args[1].get("message", "") or "TMA-100" in str(call_args)
        assert result["threat_count"] == 2
