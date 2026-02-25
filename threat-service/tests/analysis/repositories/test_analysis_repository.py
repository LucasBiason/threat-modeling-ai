"""Unit tests for app.analysis.repositories.analysis_repository."""

import uuid
from datetime import date, datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from app.analysis.models import Analysis, AnalysisStatus
from app.analysis.repositories.analysis_repository import (
    AnalysisRepository,
    _generate_analysis_code,
)


@pytest.fixture
def mock_db():
    """Mock SQLAlchemy session."""
    return MagicMock()


@pytest.fixture
def repository(mock_db, tmp_path):
    """AnalysisRepository with mocked settings."""
    with patch("app.analysis.repositories.analysis_repository.get_settings") as m:
        s = MagicMock()
        s.upload_dir = tmp_path
        m.return_value = s
        repo = AnalysisRepository(mock_db)
        yield repo


class TestGenerateAnalysisCode:
    """Tests for _generate_analysis_code helper."""

    def test_default_format(self):
        code = _generate_analysis_code()
        assert code.startswith("TMA-")
        assert len(code) == 12
        assert code[4:].isdigit()

    def test_custom_prefix_and_length(self):
        code = _generate_analysis_code(prefix="TEST", length=4)
        assert code.startswith("TEST-")
        assert len(code.split("-")[1]) == 4


class TestAnalysisRepositoryNextCode:
    """Tests for _next_code."""

    def test_next_code_format(self, repository, mock_db):
        """Generated code has format TMA- + 8 digits."""
        mock_db.execute.return_value.scalars.return_value.first.return_value = None
        code = repository._next_code()
        assert code.startswith("TMA-")
        assert len(code) == len("TMA-") + 8
        assert code[4:].isdigit()

    def test_next_code_retries_on_collision(self, repository, mock_db):
        """When generated code exists, retries until unique."""
        existing = MagicMock()
        mock_db.execute.return_value.scalars.return_value.first.side_effect = [
            existing,
            None,
        ]
        code = repository._next_code()
        assert code.startswith("TMA-") and code[4:].isdigit()

    def test_next_code_raises_after_max_attempts(self, repository, mock_db):
        """Raises RuntimeError after 10 failed attempts."""
        mock_db.execute.return_value.scalars.return_value.first.return_value = MagicMock()
        with pytest.raises(RuntimeError, match="Could not generate unique"):
            repository._next_code()


class TestSaveImage:
    """Tests for _save_image."""

    def test_save_image_png(self, repository):
        """PNG bytes save with .png extension."""
        png = b"\x89PNG\r\n\x1a\n" + b"\x00" * 20
        aid = uuid.uuid4()
        name = repository._save_image(png, aid)
        assert name.endswith(".png")
        assert str(aid) in name
        assert (repository._upload_dir / name).exists()

    def test_save_image_jpeg(self, repository):
        """JPEG bytes save with .jpg extension."""
        jpeg = b"\xff\xd8\xff" + b"\x00" * 20
        aid = uuid.uuid4()
        name = repository._save_image(jpeg, aid)
        assert name.endswith(".jpg")

    def test_save_image_webp(self, repository):
        """WEBP bytes save with .webp extension."""
        webp = b"\x00" * 8 + b"WEBP" + b"\x00" * 20
        aid = uuid.uuid4()
        name = repository._save_image(webp, aid)
        assert name.endswith(".webp")

    def test_save_image_unknown_defaults_png(self, repository):
        """Unknown format defaults to .png."""
        aid = uuid.uuid4()
        name = repository._save_image(b"random bytes", aid)
        assert name.endswith(".png")

    def test_save_image_short_bytes_png(self, repository):
        """Very short byte sequences default to .png."""
        aid = uuid.uuid4()
        name = repository._save_image(b"x", aid)
        assert name.endswith(".png")


class TestCreate:
    """Tests for create method."""

    def test_create_success(self, repository, mock_db):
        """create saves image, adds to DB, commits, refreshes."""
        mock_db.execute.return_value.scalars.return_value.first.return_value = None
        png = b"\x89PNG\r\n\x1a\n" + b"\x00" * 20
        with patch.object(repository, "_next_code", return_value="TMA-99999999"):
            result = repository.create(png, "diagram.png")
        assert isinstance(result, Analysis)
        assert result.code == "TMA-99999999"
        assert result.status == AnalysisStatus.EM_ABERTO
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()


class TestGetById:
    """Tests for get_by_id."""

    def test_get_by_id_found(self, repository, mock_db):
        a = MagicMock()
        mock_db.get.return_value = a
        assert repository.get_by_id(uuid.uuid4()) is a

    def test_get_by_id_not_found(self, repository, mock_db):
        mock_db.get.return_value = None
        assert repository.get_by_id(uuid.uuid4()) is None


class TestGetPending:
    """Tests for get_pending."""

    def test_get_pending_returns_analysis(self, repository, mock_db):
        a = MagicMock()
        mock_db.execute.return_value.scalars.return_value.first.return_value = a
        assert repository.get_pending() is a

    def test_get_pending_returns_none(self, repository, mock_db):
        mock_db.execute.return_value.scalars.return_value.first.return_value = None
        assert repository.get_pending() is None


class TestListAll:
    """Tests for list_all."""

    def test_list_all_no_filters(self, repository, mock_db):
        mock_db.execute.return_value.scalars.return_value.all.return_value = []
        result = repository.list_all()
        assert result == []

    def test_list_all_with_status_filter(self, repository, mock_db):
        mock_db.execute.return_value.scalars.return_value.all.return_value = []
        result = repository.list_all(status=AnalysisStatus.EM_ABERTO)
        assert result == []

    def test_list_all_with_code_substring(self, repository, mock_db):
        mock_db.execute.return_value.scalars.return_value.all.return_value = []
        result = repository.list_all(code_substring="TMA")
        assert result == []

    def test_list_all_with_empty_code_substring(self, repository, mock_db):
        mock_db.execute.return_value.scalars.return_value.all.return_value = []
        result = repository.list_all(code_substring="   ")
        assert result == []

    def test_list_all_with_date_range(self, repository, mock_db):
        mock_db.execute.return_value.scalars.return_value.all.return_value = []
        result = repository.list_all(
            created_at_from=date(2024, 1, 1),
            created_at_to=date(2024, 12, 31),
        )
        assert result == []


class TestUpdateStatus:
    """Tests for update_status."""

    def test_update_status_success(self, repository, mock_db):
        a = MagicMock()
        mock_db.get.return_value = a
        aid = uuid.uuid4()
        now = datetime.now(timezone.utc)
        result = repository.update_status(
            aid,
            AnalysisStatus.PROCESSANDO,
            started_at=now,
        )
        assert result is a
        assert a.status == AnalysisStatus.PROCESSANDO
        assert a.started_at == now
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

    def test_update_status_not_found(self, repository, mock_db):
        mock_db.get.return_value = None
        result = repository.update_status(uuid.uuid4(), AnalysisStatus.PROCESSANDO)
        assert result is None

    def test_update_status_with_all_fields(self, repository, mock_db):
        a = MagicMock()
        mock_db.get.return_value = a
        now = datetime.now(timezone.utc)
        repository.update_status(
            uuid.uuid4(),
            AnalysisStatus.ANALISADO,
            started_at=now,
            finished_at=now,
            result={"key": "value"},
            processing_logs="log",
            error_message="err",
        )
        assert a.finished_at == now
        assert a.result == {"key": "value"}
        assert a.processing_logs == "log"
        assert a.error_message == "err"


class TestMarkMethods:
    """Tests for mark_processing, mark_failed, mark_analysed."""

    def test_mark_processing(self, repository, mock_db):
        a = MagicMock()
        mock_db.get.return_value = a
        now = datetime.now(timezone.utc)
        result = repository.mark_processing(uuid.uuid4(), started_at=now)
        assert result is a
        assert a.status == AnalysisStatus.PROCESSANDO

    def test_mark_failed(self, repository, mock_db):
        a = MagicMock()
        mock_db.get.return_value = a
        now = datetime.now(timezone.utc)
        result = repository.mark_failed(
            uuid.uuid4(), finished_at=now, error_message="boom"
        )
        assert result is a
        assert a.status == AnalysisStatus.FALHOU

    def test_mark_analysed(self, repository, mock_db):
        a = MagicMock()
        mock_db.get.return_value = a
        now = datetime.now(timezone.utc)
        result = repository.mark_analysed(
            uuid.uuid4(), finished_at=now, result={"threats": []}
        )
        assert result is a
        assert a.status == AnalysisStatus.ANALISADO


class TestAppendProcessingLog:
    """Tests for append_processing_log."""

    def test_append_to_empty(self, repository, mock_db):
        a = MagicMock()
        a.processing_logs = None
        mock_db.get.return_value = a
        assert repository.append_processing_log(uuid.uuid4(), "line1") is True
        assert a.processing_logs == "line1\n"
        mock_db.commit.assert_called_once()

    def test_append_to_existing(self, repository, mock_db):
        a = MagicMock()
        a.processing_logs = "line1\n"
        mock_db.get.return_value = a
        assert repository.append_processing_log(uuid.uuid4(), "line2") is True
        assert a.processing_logs == "line1\nline2\n"

    def test_append_not_found(self, repository, mock_db):
        mock_db.get.return_value = None
        assert repository.append_processing_log(uuid.uuid4(), "line") is False


class TestGetImagePath:
    """Tests for get_image_path."""

    def test_get_image_path_found(self, repository, mock_db):
        a = MagicMock()
        a.image_path = "test.png"
        mock_db.get.return_value = a
        img_file = repository._upload_dir / "test.png"
        img_file.write_bytes(b"png data")
        result = repository.get_image_path(uuid.uuid4())
        assert result == img_file

    def test_get_image_path_analysis_not_found(self, repository, mock_db):
        mock_db.get.return_value = None
        assert repository.get_image_path(uuid.uuid4()) is None

    def test_get_image_path_file_missing(self, repository, mock_db):
        a = MagicMock()
        a.image_path = "nonexistent.png"
        mock_db.get.return_value = a
        assert repository.get_image_path(uuid.uuid4()) is None
