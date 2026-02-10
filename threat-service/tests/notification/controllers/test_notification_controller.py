"""Unit tests for app.notification.controllers.notification_controller."""

import uuid
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest

from app.notification.controllers.notification_controller import NotificationController


@pytest.fixture
def mock_db():
    return MagicMock()


@pytest.fixture
def controller(mock_db):
    return NotificationController(mock_db)


class TestNotificationController:
    """Tests for NotificationController."""

    def test_get_unread_empty(self, controller):
        """get_unread returns empty list when no notifications."""
        with patch.object(controller._repository, "list_unread", return_value=[]):
            result = controller.get_unread()
        assert result.unread_count == 0
        assert result.notifications == []

    def test_get_unread_with_items(self, controller):
        """get_unread returns notifications."""
        n = MagicMock()
        n.id = uuid.uuid4()
        n.analysis_id = uuid.uuid4()
        n.title = "Test"
        n.message = "Msg"
        n.is_read = False
        n.link = "/link"
        n.created_at = datetime.now(timezone.utc)
        with patch.object(controller._repository, "list_unread", return_value=[n]):
            result = controller.get_unread(limit=10)
        assert result.unread_count == 1
        assert len(result.notifications) == 1
        assert result.notifications[0].title == "Test"

    def test_mark_read_success(self, controller):
        """mark_read returns True when success."""
        with patch.object(controller._repository, "mark_read", return_value=True):
            assert controller.mark_read(uuid.uuid4()) is True

    def test_mark_read_not_found(self, controller):
        """mark_read returns False when notification not found."""
        with patch.object(controller._repository, "mark_read", return_value=False):
            assert controller.mark_read(uuid.uuid4()) is False
