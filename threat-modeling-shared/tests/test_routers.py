"""Tests for routers.health module."""

from unittest.mock import MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from threat_modeling_shared.routers.health import create_health_router  # pragma: allowlist secret


def _app_with_health_router(**kwargs):
    app = FastAPI()
    router = create_health_router(**kwargs)
    app.include_router(router)
    return TestClient(app)


class TestHealthCheckHandler:
    def test_root_endpoint(self):
        client = _app_with_health_router(system_name="TestService")
        resp = client.get("/")
        assert resp.status_code == 200
        body = resp.json()
        assert body["system_name"] == "TestService"
        assert body["status"] == "healthy"
        assert body["database"] == "not_required"
        assert "timestamp" in body

    def test_health_endpoint(self):
        client = _app_with_health_router(system_name="TestService")
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["system_name"] == "TestService"

    def test_health_slash_endpoint(self):
        client = _app_with_health_router(system_name="TestService")
        resp = client.get("/health/")
        assert resp.status_code == 200

    @patch.dict("os.environ", {"SYSTEM_VERSION": "2.0.0", "ENVIRONMENT": "production"})
    def test_env_vars_in_response(self):
        client = _app_with_health_router(system_name="TestService")
        resp = client.get("/health")
        body = resp.json()
        assert body["system_version"] == "2.0.0"
        assert body["environment"] == "production"

    def test_with_db_check_healthy(self):
        mock_db = MagicMock(return_value=True)
        client = _app_with_health_router(
            system_name="TestService",
            check_database=True,
            db_check=mock_db,
        )
        resp = client.get("/health")
        body = resp.json()
        assert body["database"] == "healthy"
        assert body["status"] == "healthy"
        mock_db.assert_called()

    def test_with_db_check_unhealthy(self):
        mock_db = MagicMock(side_effect=Exception("connection refused"))
        client = _app_with_health_router(
            system_name="TestService",
            check_database=True,
            db_check=mock_db,
        )
        resp = client.get("/health")
        body = resp.json()
        assert "unhealthy" in body["database"]
        assert body["status"] == "degraded"

    def test_check_database_false_no_db_check(self):
        client = _app_with_health_router(
            system_name="TestService",
            check_database=False,
        )
        resp = client.get("/health")
        assert resp.json()["database"] == "not_required"

    def test_check_database_true_no_db_check_callable(self):
        client = _app_with_health_router(
            system_name="TestService",
            check_database=True,
            db_check=None,
        )
        resp = client.get("/health")
        assert resp.json()["database"] == "not_required"


class TestReadinessCheck:
    def test_ready_no_db(self):
        client = _app_with_health_router(system_name="TestService")
        resp = client.get("/health/ready")
        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "ready"
        assert body["endpoint"] == "/health/ready"

    def test_ready_with_healthy_db(self):
        mock_db = MagicMock(return_value=True)
        client = _app_with_health_router(
            system_name="TestService",
            check_database=True,
            db_check=mock_db,
        )
        resp = client.get("/health/ready")
        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "ready"
        assert body["system_name"] == "TestService"

    def test_ready_with_unhealthy_db(self):
        mock_db = MagicMock(side_effect=Exception("db down"))
        client = _app_with_health_router(
            system_name="TestService",
            check_database=True,
            db_check=mock_db,
        )
        resp = client.get("/health/ready")
        assert resp.status_code == 503
        body = resp.json()
        assert body["status"] == "not_ready"
        assert "db down" in body["error"]


class TestLivenessCheck:
    def test_live(self):
        client = _app_with_health_router(system_name="TestService")
        resp = client.get("/health/live")
        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "alive"
        assert body["endpoint"] == "/health/live"
        assert body["system_name"] == "TestService"
