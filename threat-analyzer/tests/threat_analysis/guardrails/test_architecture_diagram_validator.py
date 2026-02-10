"""Unit tests for app.threat_analysis.guardrails.architecture_diagram_validator."""

import asyncio
from unittest.mock import AsyncMock, patch

import pytest

from app.threat_analysis.exceptions import ArchitectureDiagramValidationError
from app.threat_analysis.guardrails.architecture_diagram_validator import (
    _validate_guardrail_result,
    validate_architecture_diagram,
)


class TestValidateGuardrailResult:
    def test_valid_true(self):
        assert (
            _validate_guardrail_result(
                {"is_architecture_diagram": True, "reason": "ok"}
            )
            is True
        )

    def test_valid_false(self):
        assert (
            _validate_guardrail_result(
                {"is_architecture_diagram": False, "reason": "nope"}
            )
            is True
        )

    def test_missing_is_architecture_diagram(self):
        assert _validate_guardrail_result({"reason": "ok"}) is False

    def test_contains_error(self):
        assert _validate_guardrail_result({"error": "failed"}) is False

    def test_not_dict(self):
        assert _validate_guardrail_result("invalid") is False


class TestValidateArchitectureDiagram:
    def test_rejects_non_architecture(self):
        mock_result = {
            "is_architecture_diagram": False,
            "reason": "This is a sequence diagram",
        }
        with patch(
            "app.threat_analysis.guardrails.architecture_diagram_validator.run_vision_with_fallback",
            new_callable=AsyncMock,
            return_value=mock_result,
        ):
            from app.config import get_settings

            settings = get_settings()
            with pytest.raises(ArchitectureDiagramValidationError) as exc_info:
                asyncio.run(validate_architecture_diagram(b"fake_image", settings))
            assert (
                "sequence" in str(exc_info.value.reason).lower()
                or "diagram" in str(exc_info.value.reason).lower()
            )

    def test_accepts_valid_architecture(self):
        mock_result = {
            "is_architecture_diagram": True,
            "reason": "Diagram shows servers and database",
        }
        with patch(
            "app.threat_analysis.guardrails.architecture_diagram_validator.run_vision_with_fallback",
            new_callable=AsyncMock,
            return_value=mock_result,
        ):
            from app.config import get_settings

            settings = get_settings()
            asyncio.run(validate_architecture_diagram(b"fake_image", settings))

    def test_llm_error_allows_through_and_returns(self, caplog):
        """When LLM returns {'error': '...'}, guardrail logs and returns without raising (lines 87-92)."""
        mock_result = {"error": "timeout"}
        with patch(
            "app.threat_analysis.guardrails.architecture_diagram_validator.run_vision_with_fallback",
            new_callable=AsyncMock,
            return_value=mock_result,
        ):
            from app.config import get_settings

            settings = get_settings()
            asyncio.run(validate_architecture_diagram(b"fake_image", settings))
        assert "LLM validation failed" in caplog.text or "timeout" in caplog.text
