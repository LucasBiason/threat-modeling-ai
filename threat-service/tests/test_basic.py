"""Basic smoke tests for Threat Modeling API."""

from fastapi.testclient import TestClient

from app.main import app


def test_app_imports():
    """Test that the app can be imported without errors."""
    from app.analysis.controllers import AnalysisController
    from app.notification.controllers import NotificationController

    assert app is not None
    assert AnalysisController is not None
    assert NotificationController is not None


def test_health_endpoint():
    """GET /health returns 200 with status healthy or degraded (DB may be unavailable)."""
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data.get("status") in ("healthy", "degraded")
    assert "threat" in data.get("system_name", "").lower()
