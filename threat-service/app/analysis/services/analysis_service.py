"""HTTP client for the threat-analyzer service — encapsulates all calls to the analysis API."""

from __future__ import annotations

from pathlib import Path

import httpx


class AnalysisServiceError(Exception):
    """Raised when a call to the threat-analyzer service fails (HTTP or network)."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class AnalysisService:
    """Encapsulates connection and calls to the threat-analyzer service endpoints."""

    def __init__(self, base_url: str, timeout: float = 300.0) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout

    @property
    def analyze_endpoint(self) -> str:
        return f"{self._base_url}/api/v1/threat-model/analyze"

    @staticmethod
    def _content_type_for_path(path: Path) -> str:
        ext = (path.suffix or ".png").lower()
        if ext == ".png":
            return "image/png"
        if ext == ".webp":
            return "image/webp"
        return "image/jpeg"

    def analyze(self, image_path: Path, image_filename: str) -> dict:
        """
        Send image to threat-analyzer and return the analysis result.

        Args:
            image_path: Full path to the image file.
            image_filename: Original filename for the multipart field.

        Returns:
            JSON result from the analyzer (e.g. threats, risk_level).

        Raises:
            AnalysisServiceError: On HTTP error or any request failure (with a documented message).
        """
        image_bytes = image_path.read_bytes()
        content_type = self._content_type_for_path(image_path)
        try:
            with httpx.Client(timeout=self._timeout) as client:
                response = client.post(
                    self.analyze_endpoint,
                    files={"file": (image_filename, image_bytes, content_type)},
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            detail = (e.response.text or "")[:500]
            raise AnalysisServiceError(
                f"threat-analyzer HTTP error: {e.response.status_code} - {detail}"
            ) from e
        except Exception as e:
            raise AnalysisServiceError(f"threat-analyzer request failed: {e!s}") from e
