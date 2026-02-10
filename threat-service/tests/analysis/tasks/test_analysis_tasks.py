"""Unit tests for app.analysis.tasks.analysis_tasks."""

import uuid
from unittest.mock import MagicMock, patch

from app.analysis.tasks.analysis_tasks import process_analysis, scan_pending_analyses


class TestScanPendingAnalyses:
    """Tests for scan_pending_analyses task."""

    def test_scan_pending_returns_none_when_no_pending(self):
        """Returns None when no EM_ABERTO analysis."""
        with patch("app.analysis.tasks.analysis_tasks.SessionLocal") as mock_session:
            db = MagicMock()
            mock_session.return_value = db
            with patch(
                "app.analysis.tasks.analysis_tasks.AnalysisRepository"
            ) as mock_repo_cls:
                repo = MagicMock()
                repo.get_pending.return_value = None
                mock_repo_cls.return_value = repo
                result = scan_pending_analyses()
        assert result is None


class TestProcessAnalysis:
    """Tests for process_analysis task (delegates to AnalysisProcessingService)."""

    def test_process_analysis_not_found(self):
        """Returns error dict when service returns not found."""
        aid = str(uuid.uuid4())
        with patch("app.analysis.tasks.analysis_tasks.SessionLocal") as mock_session:
            db = MagicMock()
            mock_session.return_value = db
            with patch(
                "app.analysis.tasks.analysis_tasks.AnalysisProcessingService"
            ) as mock_svc_cls:
                mock_svc = MagicMock()
                mock_svc.process.return_value = {
                    "error": "Analysis not found",
                    "analysis_id": aid,
                }
                mock_svc_cls.return_value = mock_svc
                result = process_analysis(aid)
        assert "error" in result
        assert "not found" in result["error"].lower()
        mock_svc.process.assert_called_once_with(uuid.UUID(aid))

    def test_process_analysis_already_done(self):
        """Returns skipped when service returns already done."""
        aid = str(uuid.uuid4())
        with patch("app.analysis.tasks.analysis_tasks.SessionLocal") as mock_session:
            db = MagicMock()
            mock_session.return_value = db
            with patch(
                "app.analysis.tasks.analysis_tasks.AnalysisProcessingService"
            ) as mock_svc_cls:
                mock_svc = MagicMock()
                mock_svc.process.return_value = {
                    "skipped": "Already done",
                    "analysis_id": aid,
                }
                mock_svc_cls.return_value = mock_svc
                result = process_analysis(aid)
        assert "skipped" in result
