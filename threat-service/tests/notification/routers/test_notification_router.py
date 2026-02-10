"""Unit tests for app.notification.routers.notification_router."""

import uuid
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.notification.controllers.notification_controller import NotificationController
from app.notification.routers.notification_router import get_controller
from app.notification.schemas import NotificationUnreadResponse


@pytest.fixture
def mock_notif_controller():
    """Mock NotificationController."""
    return MagicMock(spec=NotificationController)


@pytest.fixture
def client_notif_mocked(mock_notif_controller, client_no_db):
    """Test client with mocked notification controller (no PostgreSQL)."""
    def override():
        return mock_notif_controller

    app.dependency_overrides[get_controller] = override
    try:
        yield client_no_db
    finally:
        app.dependency_overrides.pop(get_controller, None)


class TestNotificationRouterUnit:
    """Unit tests with mocked controller."""

    def test_router_module_imports(self):
        """Notification router can be imported."""
        from app.notification.routers.notification_router import router

        assert router.prefix == "/notifications"

    def test_get_unread(self, client_notif_mocked, mock_notif_controller):
        """GET /notifications/unread delegates to controller."""
        mock_notif_controller.get_unread.return_value = NotificationUnreadResponse(
            unread_count=0, notifications=[]
        )
        response = client_notif_mocked.get("/api/v1/notifications/unread")
        assert response.status_code == 200
        assert response.json()["unread_count"] == 0

    def test_mark_read_success(self, client_notif_mocked, mock_notif_controller):
        """POST /notifications/{id}/read returns 204 when success."""
        mock_notif_controller.mark_read.return_value = True
        response = client_notif_mocked.post(
            f"/api/v1/notifications/{uuid.uuid4()}/read"
        )
        assert response.status_code == 204

    def test_mark_read_not_found(self, client_notif_mocked, mock_notif_controller):
        """POST /notifications/{id}/read returns 404 when not found."""
        mock_notif_controller.mark_read.return_value = False
        response = client_notif_mocked.post(
            f"/api/v1/notifications/{uuid.uuid4()}/read"
        )
        assert response.status_code == 404
