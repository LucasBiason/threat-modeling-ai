"""Unit tests for app.analysis.models.analysis — model properties."""

from unittest.mock import MagicMock

from app.analysis.models import Analysis, AnalysisStatus


class TestAnalysisProperties:
    """Tests for computed boolean properties."""

    def _make(self, status: AnalysisStatus) -> MagicMock:
        a = MagicMock(spec=Analysis)
        a.status = status
        a.is_open = Analysis.is_open.fget(a)
        a.is_processing = Analysis.is_processing.fget(a)
        a.is_done = Analysis.is_done.fget(a)
        a.is_failed = Analysis.is_failed.fget(a)
        return a

    def test_is_open_true(self):
        a = self._make(AnalysisStatus.EM_ABERTO)
        assert a.is_open is True

    def test_is_open_false(self):
        a = self._make(AnalysisStatus.PROCESSANDO)
        assert a.is_open is False

    def test_is_processing_true(self):
        a = self._make(AnalysisStatus.PROCESSANDO)
        assert a.is_processing is True

    def test_is_processing_false(self):
        a = self._make(AnalysisStatus.EM_ABERTO)
        assert a.is_processing is False

    def test_is_done_true(self):
        a = self._make(AnalysisStatus.ANALISADO)
        assert a.is_done is True

    def test_is_done_false(self):
        a = self._make(AnalysisStatus.PROCESSANDO)
        assert a.is_done is False

    def test_is_failed_true(self):
        a = self._make(AnalysisStatus.FALHOU)
        assert a.is_failed is True

    def test_is_failed_false(self):
        a = self._make(AnalysisStatus.EM_ABERTO)
        assert a.is_failed is False


class TestAnalysisStatusEnum:
    """Tests for AnalysisStatus enum."""

    def test_all_values(self):
        assert AnalysisStatus.EM_ABERTO.value == "EM_ABERTO"
        assert AnalysisStatus.PROCESSANDO.value == "PROCESSANDO"
        assert AnalysisStatus.ANALISADO.value == "ANALISADO"
        assert AnalysisStatus.FALHOU.value == "FALHOU"
