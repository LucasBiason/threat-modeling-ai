"""Unit tests for app.notification.repositories.notification_repository."""

import uuid
from unittest.mock import MagicMock

import pytest

from app.notification.models import Notification
from app.notification.repositories.notification_repository import NotificationRepository


@pytest.fixture
def mock_db():
    return MagicMock()


@pytest.fixture
def repo(mock_db):
    return NotificationRepository(mock_db)


class TestNotificationRepository:
    """Tests for NotificationRepository (mocked DB)."""

    def test_create(self, repo, mock_db):
        """create adds notification and commits."""
        mock_db.refresh = MagicMock(side_effect=lambda n: setattr(n, "id", uuid.uuid4()))
        result = repo.create(
            analysis_id=uuid.uuid4(),
            title="T",
            message="M",
            link="/link",
        )
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        assert isinstance(result, Notification)
        assert result.title == "T"

    def test_get_by_id_not_found(self, repo, mock_db):
        """get_by_id returns None when not found."""
        mock_db.get.return_value = None
        assert repo.get_by_id(uuid.uuid4()) is None

    def test_list_unread(self, repo, mock_db):
        """list_unread returns list from query."""
        mock_db.execute.return_value.scalars().all.return_value = []
        result = repo.list_unread(limit=5)
        assert result == []

    def test_mark_read_success(self, repo, mock_db):
        """mark_read returns True and commits."""
        n = MagicMock()
        mock_db.get.return_value = n
        assert repo.mark_read(uuid.uuid4()) is True
        assert n.is_read is True
        mock_db.commit.assert_called()

    def test_mark_read_not_found(self, repo, mock_db):
        """mark_read returns False when not found."""
        mock_db.get.return_value = None
        assert repo.mark_read(uuid.uuid4()) is False
