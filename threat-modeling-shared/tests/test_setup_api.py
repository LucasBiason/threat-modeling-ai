"""Tests for setup_api module."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from fastapi import APIRouter, FastAPI
from fastapi.testclient import TestClient

from threat_modeling_shared.setup_api import create_app  # pragma: allowlist secret


def _make_settings(**overrides):
    defaults = dict(
        app_name="TestApp",
        app_version="0.1.0",
        debug=False,
        log_level="INFO",
        database_url="",
        cors_origins=["*"],
        cors_allow_credentials=True,
        cors_allow_methods=["*"],
        cors_allow_headers=["*"],
    )
    defaults.update(overrides)
    return SimpleNamespace(**defaults)


def _make_router(path="/test", response=None):
    router = APIRouter()

    @router.get(path)
    async def handler():
        return response or {"msg": "ok"}

    return router


class TestCreateAppBasic:
    def test_creates_fastapi_app(self):
        settings = _make_settings()
        app = create_app(
            title="TestApp",
            routers=[],
            settings=settings,
        )
        assert isinstance(app, FastAPI)
        assert app.title == "TestApp"

    def test_includes_custom_routers(self):
        settings = _make_settings()
        router = _make_router("/hello", {"greeting": "hi"})
        app = create_app(
            title="TestApp",
            routers=[router],
            settings=settings,
        )
        client = TestClient(app)
        resp = client.get("/hello")
        assert resp.status_code == 200
        assert resp.json() == {"greeting": "hi"}

    def test_includes_tuple_routers(self):
        settings = _make_settings()
        router = _make_router("/endpoint", {"data": 1})
        app = create_app(
            title="TestApp",
            routers=[(router, {"prefix": "/api"})],
            settings=settings,
        )
        client = TestClient(app)
        resp = client.get("/api/endpoint")
        assert resp.status_code == 200
        assert resp.json() == {"data": 1}

    def test_health_endpoint_present(self):
        settings = _make_settings()
        app = create_app(
            title="TestApp",
            routers=[],
            settings=settings,
        )
        client = TestClient(app)
        resp = client.get("/health")
        assert resp.status_code == 200
        body = resp.json()
        assert body["system_name"] == "TestApp"

    def test_custom_health_system_name(self):
        settings = _make_settings()
        app = create_app(
            title="TestApp",
            routers=[],
            settings=settings,
            health_system_name="CustomName",
        )
        client = TestClient(app)
        resp = client.get("/health")
        assert resp.json()["system_name"] == "CustomName"


class TestCreateAppDescription:
    def test_default_description(self):
        settings = _make_settings()
        app = create_app(
            title="TestApp",
            routers=[],
            settings=settings,
        )
        assert app.description == ""

    def test_custom_description(self):
        settings = _make_settings()
        app = create_app(
            title="TestApp",
            description="A test application",
            routers=[],
            settings=settings,
        )
        assert app.description == "A test application"


class TestCreateAppDebugDocs:
    def test_docs_disabled_when_not_debug(self):
        settings = _make_settings(debug=False)
        app = create_app(title="T", routers=[], settings=settings)
        assert app.docs_url is None
        assert app.redoc_url is None

    def test_docs_enabled_when_debug(self):
        settings = _make_settings(debug=True)
        app = create_app(title="T", routers=[], settings=settings)
        assert app.docs_url == "/docs"
        assert app.redoc_url == "/redoc"


class TestCreateAppLifespan:
    def test_default_lifespan(self):
        settings = _make_settings()
        app = create_app(title="TestApp", routers=[], settings=settings)
        with TestClient(app) as client:
            resp = client.get("/health")
            assert resp.status_code == 200

    def test_custom_lifespan(self):
        started = []

        @asynccontextmanager
        async def custom_lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
            started.append(True)
            yield

        settings = _make_settings()
        app = create_app(
            title="TestApp",
            routers=[],
            settings=settings,
            lifespan=custom_lifespan,
        )
        with TestClient(app) as client:
            resp = client.get("/health")
            assert resp.status_code == 200
            assert started == [True]


class TestCreateAppCheckDatabase:
    def test_check_database_auto_detect_empty_url(self):
        settings = _make_settings(database_url="")
        app = create_app(title="T", routers=[], settings=settings)
        client = TestClient(app)
        resp = client.get("/health")
        assert resp.json()["database"] == "not_required"

    @patch("threat_modeling_shared.setup_api.create_health_router")  # pragma: allowlist secret
    def test_check_database_auto_detect_with_url(self, mock_health_router):
        mock_router = APIRouter()
        mock_health_router.return_value = mock_router
        settings = _make_settings(database_url="postgresql://localhost/db")  # pragma: allowlist secret

        app = create_app(title="T", routers=[], settings=settings)

        call_kwargs = mock_health_router.call_args
        assert call_kwargs[1]["check_database"] is True
        assert call_kwargs[1]["db_check"] is not None

    def test_check_database_explicit_false(self):
        settings = _make_settings(database_url="postgresql://localhost/db")  # pragma: allowlist secret
        app = create_app(
            title="T", routers=[], settings=settings, check_database=False
        )
        client = TestClient(app)
        resp = client.get("/health")
        assert resp.json()["database"] == "not_required"

    def test_check_database_explicit_with_custom_db_check(self):
        mock_db_check = MagicMock(return_value=True)
        settings = _make_settings()
        app = create_app(
            title="T",
            routers=[],
            settings=settings,
            check_database=True,
            db_check=mock_db_check,
        )
        client = TestClient(app)
        resp = client.get("/health")
        body = resp.json()
        assert body["database"] == "healthy"

    @patch("threat_modeling_shared.setup_api.create_health_router")  # pragma: allowlist secret
    def test_auto_imports_db_check_when_needed(self, mock_health_router):
        mock_router = APIRouter()
        mock_health_router.return_value = mock_router
        settings = _make_settings(database_url="postgresql://localhost/db")  # pragma: allowlist secret

        app = create_app(
            title="T",
            routers=[],
            settings=settings,
            check_database=True,
            db_check=None,
        )

        call_kwargs = mock_health_router.call_args
        assert call_kwargs[1]["db_check"] is not None


class TestCreateAppExceptionHandlers:
    def test_custom_error_handler(self):
        class MyError(Exception):
            def __init__(self, message, details=None):
                self.message = message
                self.details = details or {}

        settings = _make_settings()
        router = APIRouter()

        @router.get("/fail")
        async def fail():
            raise MyError("something failed", {"key": "val"})

        app = create_app(
            title="T",
            routers=[router],
            settings=settings,
            custom_error_handler=(MyError, "MyError:"),
        )
        client = TestClient(app, raise_server_exceptions=False)
        resp = client.get("/fail")
        assert resp.status_code == 500
        body = resp.json()
        assert body["error"] == "something failed"
        assert body["details"] == {"key": "val"}

    def test_exception_handlers_list(self):
        from fastapi.responses import JSONResponse

        class SpecialError(Exception):
            pass

        async def special_handler(request, exc):
            return JSONResponse(status_code=409, content={"conflict": str(exc)})

        settings = _make_settings()
        router = APIRouter()

        @router.get("/special")
        async def special():
            raise SpecialError("conflict!")

        app = create_app(
            title="T",
            routers=[router],
            settings=settings,
            exception_handlers=[(SpecialError, special_handler)],
        )
        client = TestClient(app, raise_server_exceptions=False)
        resp = client.get("/special")
        assert resp.status_code == 409
        assert resp.json() == {"conflict": "conflict!"}


class TestCreateAppExceptionPassThrough:
    def test_pass_through_to_middleware(self):
        class TeapotError(Exception):
            pass

        pt = ((TeapotError, 418, lambda e: {"msg": str(e)}),)
        settings = _make_settings()
        router = APIRouter()

        @router.get("/teapot")
        async def teapot():
            raise TeapotError("I am a teapot")

        app = create_app(
            title="T",
            routers=[router],
            settings=settings,
            exception_pass_through=pt,
        )
        client = TestClient(app, raise_server_exceptions=False)
        resp = client.get("/teapot")
        assert resp.status_code == 418
        assert resp.json() == {"msg": "I am a teapot"}
