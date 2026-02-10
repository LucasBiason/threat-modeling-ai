"""Unit tests for app.middlewares.exceptions_middleware."""

import logging
from unittest.mock import MagicMock

import pytest
from fastapi import FastAPI
from fastapi.exceptions import ResponseValidationError
from starlette.testclient import TestClient

from threat_modeling_shared.middleware import CatchExceptionsMiddleware


@pytest.fixture
def app_with_middleware():
    app = FastAPI()

    @app.get("/ok")
    async def ok():
        return {"status": "ok"}

    @app.get("/raise-validation")
    async def raise_validation():
        raise ResponseValidationError(errors=[{"msg": "validation error"}])

    @app.get("/raise-generic")
    async def raise_generic():
        raise ValueError("something went wrong")

    app.add_middleware(CatchExceptionsMiddleware, logger=logging.getLogger("test"))
    return app


class TestCatchExceptionsMiddleware:
    def test_normal_request_passes(self, app_with_middleware):
        client = TestClient(app_with_middleware)
        r = client.get("/ok")
        assert r.status_code == 200
        assert r.json() == {"status": "ok"}

    def test_catches_validation_error(self, app_with_middleware):
        client = TestClient(app_with_middleware)
        r = client.get("/raise-validation")
        assert r.status_code == 422
        assert "Validation Error" in str(r.json())

    def test_catches_generic_exception(self, app_with_middleware):
        client = TestClient(app_with_middleware)
        r = client.get("/raise-generic")
        assert r.status_code == 500
        assert "something went wrong" in str(r.json())

    def test_safe_serialize(self):
        mw = CatchExceptionsMiddleware(MagicMock(), logger=MagicMock())
        assert mw.safe_serialize({"a": 1}) == {"a": 1}
        assert mw.safe_serialize([1, 2]) == [1, 2]
        assert mw.safe_serialize("x") == "x"
