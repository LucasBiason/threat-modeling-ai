"""Tests for app.main."""

import asyncio
from unittest.mock import MagicMock, patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.main import app, lifespan


def test_app_is_fastapi_instance():
    """app is a FastAPI instance."""
    assert isinstance(app, FastAPI)


def test_health_endpoint_responds_200():
    """GET /health returns 200."""
    with patch("app.main.engine", None):
        with TestClient(app) as client:
            response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data.get("status") in ("healthy", "degraded")


def test_lifespan_creates_tables_and_disposes():
    """lifespan context manager creates tables on startup and disposes engine on shutdown."""
    mock_engine = MagicMock()
    mock_create_all = MagicMock()

    async def run():
        with patch("app.main.engine", mock_engine):
            with patch("app.main.Base") as mock_base:
                mock_base.metadata.create_all = mock_create_all
                async with lifespan(MagicMock()):
                    pass
                mock_create_all.assert_called_once_with(bind=mock_engine)
                mock_engine.dispose.assert_called_once()

    asyncio.run(run())


def test_lifespan_skips_when_engine_is_none():
    """lifespan does nothing when engine is None (no DB configured)."""

    async def run():
        with patch("app.main.engine", None):
            with patch("app.main.Base") as mock_base:
                async with lifespan(MagicMock()):
                    pass
                mock_base.metadata.create_all.assert_not_called()

    asyncio.run(run())


def test_app_includes_routers():
    """App includes analysis and notification routers."""
    routes = [r.path for r in app.routes]
    assert any("/analyses" in r for r in routes)
    assert any("/notifications" in r for r in routes)
