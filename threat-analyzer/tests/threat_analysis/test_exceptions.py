"""Unit tests for app.threat_analysis.exceptions."""

import pytest

from app.threat_analysis.exceptions import (
    AnalysisError,
    InvalidFileTypeError,
    JSONParsingError,
    LLMProviderError,
    ThreatModelingError,
)


class TestThreatModelingError:
    def test_base(self):
        e = ThreatModelingError("msg")
        assert e.message == "msg"
        assert e.details == {}
        assert str(e) == "msg"

    def test_with_details(self):
        e = ThreatModelingError("msg", details={"key": "value"})
        assert e.details == {"key": "value"}


class TestInvalidFileTypeError:
    def test_init(self):
        e = InvalidFileTypeError("application/pdf", ["image/png"])
        assert "application/pdf" in e.message
        assert "image/png" in e.message
        assert e.details["content_type"] == "application/pdf"


class TestLLMProviderError:
    def test_init(self):
        e = LLMProviderError("Gemini", "Connection refused")
        assert "Gemini" in e.message
        assert "Connection refused" in e.message


class TestAnalysisError:
    def test_init(self):
        e = AnalysisError("stage1", "timeout")
        assert "stage1" in e.message
        assert "timeout" in e.message


class TestJSONParsingError:
    def test_init(self):
        e = JSONParsingError("raw content here", "expecting value")
        assert "expecting value" in e.message
        assert len(e.details["raw_content"]) <= 500
