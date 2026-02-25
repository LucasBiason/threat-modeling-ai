"""Unit tests for app.analysis.services.analysis_service."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import httpx
import pytest

from app.analysis.services.analysis_service import (
    AnalysisService,
    AnalysisServiceError,
)


class TestAnalysisServiceInit:
    """Tests for AnalysisService construction."""

    def test_base_url_strips_trailing_slash(self):
        svc = AnalysisService("http://host:8000/")
        assert svc._base_url == "http://host:8000"

    def test_default_timeout(self):
        svc = AnalysisService("http://host:8000")
        assert svc._timeout == 300.0

    def test_custom_timeout(self):
        svc = AnalysisService("http://host:8000", timeout=60.0)
        assert svc._timeout == 60.0


class TestAnalyzeEndpoint:
    """Tests for analyze_endpoint property."""

    def test_analyze_endpoint(self):
        svc = AnalysisService("http://analyzer:8000")
        assert svc.analyze_endpoint == "http://analyzer:8000/api/v1/threat-model/analyze"


class TestContentTypeForPath:
    """Tests for _content_type_for_path static method."""

    def test_png(self):
        assert AnalysisService._content_type_for_path(Path("img.png")) == "image/png"

    def test_PNG_uppercase(self):
        assert AnalysisService._content_type_for_path(Path("img.PNG")) == "image/png"

    def test_webp(self):
        assert AnalysisService._content_type_for_path(Path("img.webp")) == "image/webp"

    def test_jpg(self):
        assert AnalysisService._content_type_for_path(Path("img.jpg")) == "image/jpeg"

    def test_jpeg(self):
        assert AnalysisService._content_type_for_path(Path("img.jpeg")) == "image/jpeg"

    def test_no_suffix_defaults_png(self):
        assert AnalysisService._content_type_for_path(Path("img")) == "image/png"


class TestAnalyze:
    """Tests for analyze method."""

    def test_analyze_success(self, tmp_path):
        """Successful analysis returns JSON result."""
        img = tmp_path / "test.png"
        img.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 20)

        svc = AnalysisService("http://analyzer:8000")
        mock_response = MagicMock()
        mock_response.json.return_value = {"threats": [], "risk_level": "Low"}
        mock_response.raise_for_status = MagicMock()

        mock_client = MagicMock()
        mock_client.post.return_value = mock_response

        with patch("app.analysis.services.analysis_service.httpx.Client") as MockClient:
            MockClient.return_value.__enter__ = MagicMock(return_value=mock_client)
            MockClient.return_value.__exit__ = MagicMock(return_value=False)
            result = svc.analyze(img, "diagram.png")

        assert result == {"threats": [], "risk_level": "Low"}
        mock_client.post.assert_called_once()

    def test_analyze_http_status_error(self, tmp_path):
        """HTTP error from analyzer raises AnalysisServiceError."""
        img = tmp_path / "test.png"
        img.write_bytes(b"\x89PNG" + b"\x00" * 20)

        svc = AnalysisService("http://analyzer:8000")
        mock_resp = MagicMock()
        mock_resp.status_code = 500
        mock_resp.text = "Internal Server Error"
        http_error = httpx.HTTPStatusError(
            "500", request=MagicMock(), response=mock_resp
        )
        mock_resp.raise_for_status.side_effect = http_error

        mock_client = MagicMock()
        mock_client.post.return_value = mock_resp

        with patch("app.analysis.services.analysis_service.httpx.Client") as MockClient:
            MockClient.return_value.__enter__ = MagicMock(return_value=mock_client)
            MockClient.return_value.__exit__ = MagicMock(return_value=False)
            with pytest.raises(AnalysisServiceError) as exc_info:
                svc.analyze(img, "diagram.png")

        assert "500" in exc_info.value.message

    def test_analyze_generic_exception(self, tmp_path):
        """Generic exception raises AnalysisServiceError."""
        img = tmp_path / "test.png"
        img.write_bytes(b"\x89PNG" + b"\x00" * 20)

        svc = AnalysisService("http://analyzer:8000")
        mock_client = MagicMock()
        mock_client.post.side_effect = OSError("Connection refused")

        with patch("app.analysis.services.analysis_service.httpx.Client") as MockClient:
            MockClient.return_value.__enter__ = MagicMock(return_value=mock_client)
            MockClient.return_value.__exit__ = MagicMock(return_value=False)
            with pytest.raises(AnalysisServiceError) as exc_info:
                svc.analyze(img, "diagram.png")

        assert "Connection refused" in exc_info.value.message


class TestAnalysisServiceError:
    """Tests for AnalysisServiceError exception."""

    def test_message_attribute(self):
        err = AnalysisServiceError("test error")
        assert err.message == "test error"
        assert str(err) == "test error"
