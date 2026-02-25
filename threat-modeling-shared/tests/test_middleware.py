"""Tests for middleware.exceptions module."""

import json
import sys
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI, Request
from fastapi.exceptions import ResponseValidationError
from fastapi.testclient import TestClient

from threat_modeling_shared.middleware.exceptions import CatchExceptionsMiddleware  # pragma: allowlist secret


def _build_app_with_middleware(pass_through=None):
    """Build a minimal FastAPI app with CatchExceptionsMiddleware."""
    app = FastAPI()
    logger = MagicMock()
    app.add_middleware(CatchExceptionsMiddleware, logger=logger, pass_through=pass_through)
    return app, logger


class TestCatchExceptionsMiddlewareInit:
    def test_default_logger(self):
        app = FastAPI()
        mw = CatchExceptionsMiddleware(app)
        assert mw.logger is not None

    def test_custom_logger(self):
        app = FastAPI()
        custom_logger = MagicMock()
        mw = CatchExceptionsMiddleware(app, logger=custom_logger)
        assert mw.logger is custom_logger

    def test_default_pass_through(self):
        app = FastAPI()
        mw = CatchExceptionsMiddleware(app, logger=MagicMock())
        assert mw.pass_through == ()

    def test_custom_pass_through(self):
        app = FastAPI()
        pt = ((ValueError, 400, lambda e: {"error": str(e)}),)
        mw = CatchExceptionsMiddleware(app, logger=MagicMock(), pass_through=pt)
        assert mw.pass_through is pt


class TestSafeSerialize:
    def setup_method(self):
        app = FastAPI()
        self.mw = CatchExceptionsMiddleware(app, logger=MagicMock())

    def test_json_serializable_value(self):
        assert self.mw.safe_serialize("hello") == "hello"
        assert self.mw.safe_serialize(42) == 42
        assert self.mw.safe_serialize(True) is True
        assert self.mw.safe_serialize(None) is None

    def test_dict(self):
        result = self.mw.safe_serialize({"key": "value", "num": 1})
        assert result == {"key": "value", "num": 1}

    def test_list(self):
        result = self.mw.safe_serialize(["a", 1, None])
        assert result == ["a", 1, None]

    def test_tuple(self):
        result = self.mw.safe_serialize(("a", "b"))
        assert result == ["a", "b"]

    def test_object_with_dict(self):
        obj = MagicMock()
        obj.__dict__ = {"x": 1, "y": "two"}
        result = self.mw.safe_serialize(obj)
        assert result == {"x": 1, "y": "two"}

    def test_non_serializable_falls_to_str(self):
        result = self.mw.safe_serialize(set([1, 2]))
        assert isinstance(result, str)

    def test_object_dict_iteration_error_falls_to_str(self):
        class BrokenDict(dict):
            def items(self):
                raise ValueError("broken iteration")
        class BadDictObj:
            __slots__ = ()
            @property
            def __dict__(self):
                return BrokenDict()
        obj = BadDictObj()
        result = self.mw.safe_serialize(obj)
        assert isinstance(result, str)

    def test_nested_structure(self):
        data = {"items": [{"val": 42}]}
        assert self.mw.safe_serialize(data) == {"items": [{"val": 42}]}


class TestDispatch:
    def test_normal_response_passes_through(self):
        app, logger = _build_app_with_middleware()

        @app.get("/ok")
        async def ok():
            return {"status": "ok"}

        client = TestClient(app, raise_server_exceptions=False)
        resp = client.get("/ok")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}

    def test_response_validation_error(self):
        app, logger = _build_app_with_middleware()

        @app.get("/bad-response", response_model=dict)
        async def bad_response():
            raise ResponseValidationError(errors=[{"msg": "bad field"}])

        client = TestClient(app, raise_server_exceptions=False)
        resp = client.get("/bad-response")
        assert resp.status_code == 422
        body = resp.json()
        assert body["detail"] == "Validation Error"
        assert "errors" in body
        assert "timestamp" in body
        assert resp.headers.get("Access-Control-Allow-Origin") == "*"

    def test_generic_exception_returns_500(self):
        app, logger = _build_app_with_middleware()

        @app.get("/crash")
        async def crash():
            raise RuntimeError("something broke")

        client = TestClient(app, raise_server_exceptions=False)
        resp = client.get("/crash")
        assert resp.status_code == 500
        body = resp.json()
        assert "error" in body
        assert "traceback" in body
        assert "timestamp" in body
        assert body["request_path"] == "/crash"
        assert body["request_method"] == "GET"
        assert resp.headers.get("Access-Control-Allow-Origin") == "*"

    def test_pass_through_exception(self):
        class CustomError(Exception):
            pass

        pt = ((CustomError, 418, lambda e: {"tea": str(e)}),)
        app, logger = _build_app_with_middleware(pass_through=pt)

        @app.get("/custom")
        async def custom():
            raise CustomError("I am a teapot")

        client = TestClient(app, raise_server_exceptions=False)
        resp = client.get("/custom")
        assert resp.status_code == 418
        assert resp.json() == {"tea": "I am a teapot"}
        assert resp.headers.get("Access-Control-Allow-Origin") == "*"

    def test_pass_through_non_matching_falls_to_500(self):
        class OtherError(Exception):
            pass

        pt = ((ValueError, 400, lambda e: {"err": str(e)}),)
        app, logger = _build_app_with_middleware(pass_through=pt)

        @app.get("/other")
        async def other():
            raise OtherError("not matched")

        client = TestClient(app, raise_server_exceptions=False)
        resp = client.get("/other")
        assert resp.status_code == 500


class TestCorsHeaders:
    def test_error_response_has_cors_headers(self):
        app, logger = _build_app_with_middleware()

        @app.get("/err")
        async def err():
            raise RuntimeError("fail")

        client = TestClient(app, raise_server_exceptions=False)
        resp = client.get("/err")
        assert resp.headers["Access-Control-Allow-Origin"] == "*"
        assert "GET" in resp.headers["Access-Control-Allow-Methods"]
        assert resp.headers["Access-Control-Allow-Credentials"] == "true"
        assert resp.headers["Access-Control-Max-Age"] == "86400"
