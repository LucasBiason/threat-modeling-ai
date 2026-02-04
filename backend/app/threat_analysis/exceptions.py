"""Custom exceptions for Threat Analysis module."""

from typing import Any


class ThreatModelingError(Exception):
    """Base exception for all threat modeling errors."""

    def __init__(
        self,
        message: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class InvalidFileTypeError(ThreatModelingError):
    """Raised when an uploaded file has an invalid type."""

    def __init__(self, content_type: str, allowed_types: list[str]) -> None:
        super().__init__(
            message=f"Invalid file type: {content_type}. Allowed types: {', '.join(allowed_types)}",
            details={"content_type": content_type, "allowed_types": allowed_types},
        )


class LLMProviderError(ThreatModelingError):
    """Raised when all LLM providers fail."""

    def __init__(self, provider: str, original_error: str) -> None:
        super().__init__(
            message=f"LLM provider '{provider}' failed: {original_error}",
            details={"provider": provider, "original_error": original_error},
        )


class AnalysisError(ThreatModelingError):
    """Raised when analysis fails."""

    def __init__(self, stage: str, reason: str) -> None:
        super().__init__(
            message=f"Analysis failed at stage '{stage}': {reason}",
            details={"stage": stage, "reason": reason},
        )


class JSONParsingError(ThreatModelingError):
    """Raised when JSON parsing from LLM response fails."""

    def __init__(self, raw_content: str, parse_error: str) -> None:
        super().__init__(
            message=f"Failed to parse JSON from LLM response: {parse_error}",
            details={"raw_content": raw_content[:500], "parse_error": parse_error},
        )
