"""Unit tests for app.routes.health."""

from fastapi.testclient import TestClient

from threat_modeling_shared.routers import create_health_router


class TestHealthRouter:
    def test_create_health_router(self):
        from fastapi import FastAPI

        router = create_health_router("TestSystem")
        app = FastAPI()
        app.include_router(router)
        client = TestClient(app)
        r = client.get("/")
        assert r.status_code == 200
        assert r.json()["system_name"] == "TestSystem"
        assert r.json()["status"] == "healthy"

    def test_health_ready(self):
        from fastapi import FastAPI

        router = create_health_router("Test")
        app = FastAPI()
        app.include_router(router)
        client = TestClient(app)
        r = client.get("/health/ready")
        assert r.status_code == 200
        assert r.json()["status"] == "ready"

    def test_health_live(self):
        from fastapi import FastAPI

        router = create_health_router("Test")
        app = FastAPI()
        app.include_router(router)
        client = TestClient(app)
        r = client.get("/health/live")
        assert r.status_code == 200
        assert r.json()["status"] == "alive"
