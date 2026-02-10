"""Unit tests for app.middlewares.logging_middleware."""

from fastapi import FastAPI
from starlette.testclient import TestClient

from threat_modeling_shared.middleware import LoggingMiddleware


def test_logging_middleware_passes_request():
    app = FastAPI()

    @app.get("/ping")
    async def ping():
        return {"pong": True}

    app.add_middleware(LoggingMiddleware)
    client = TestClient(app)
    r = client.get("/ping")
    assert r.status_code == 200
    assert r.json() == {"pong": True}
