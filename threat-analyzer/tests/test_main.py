"""Tests for app.main (lifespan and exception handler)."""

import asyncio
import json
from unittest.mock import MagicMock, patch

from app.main import _handle_exception, _lifespan
from app.threat_analysis.exceptions import (
    ArchitectureDiagramValidationError,
    InvalidFileTypeError,
    ThreatModelingError,
)


async def _consume_lifespan(app):
    gen = _lifespan(app)
    await gen.__anext__()
    try:
        await gen.__anext__()
    except StopAsyncIteration:
        pass


class TestLifespan:
    """Test lifespan startup/shutdown."""

    def test_lifespan_startup_and_shutdown(self):
        app = MagicMock()
        with (
            patch("app.main.setup_logging") as setup_logging,
            patch("app.main.logger") as logger,
            patch("app.main.RAGService") as RAGService,
        ):
            asyncio.run(_consume_lifespan(app))
            setup_logging.assert_called_once()
            logger.info.assert_called()
            RAGService.assert_called_once()
            assert logger.info.call_count >= 2


class TestHandleException:
    """Test generic exception handler mapping."""

    def test_architecture_diagram_validation_error_400(self):
        req = MagicMock()
        exc = ArchitectureDiagramValidationError(reason="Not an architecture diagram")
        resp = asyncio.run(_handle_exception(req, exc))
        assert resp.status_code == 400
        body = json.loads(resp.body.decode())
        assert body["detail"] == "Not an architecture diagram"

    def test_invalid_file_type_error_400(self):
        req = MagicMock()
        exc = InvalidFileTypeError(
            content_type="image/jpeg", allowed_types=["image/png"]
        )
        resp = asyncio.run(_handle_exception(req, exc))
        assert resp.status_code == 400
        body = json.loads(resp.body.decode())
        assert "image/jpeg" in body["detail"] and "image/png" in body["detail"]

    def test_threat_modeling_error_400_with_details(self):
        req = MagicMock()
        exc = ThreatModelingError(message="Analysis failed", details={"step": "stride"})
        resp = asyncio.run(_handle_exception(req, exc))
        assert resp.status_code == 400
        body = json.loads(resp.body.decode())
        assert body["detail"] == "Analysis failed"
        assert body["details"] == {"step": "stride"}

    def test_generic_exception_500(self):
        req = MagicMock()
        exc = RuntimeError("Unexpected failure")
        resp = asyncio.run(_handle_exception(req, exc))
        assert resp.status_code == 500
        body = json.loads(resp.body.decode())
        assert body["detail"] == "Unexpected failure"
