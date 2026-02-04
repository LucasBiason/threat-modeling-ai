"""Threat Analysis Controller - business logic for diagram analysis."""

from app.core.config import Settings
from app.core.logging import get_logger
from app.threat_analysis.exceptions import ThreatModelingError
from app.threat_analysis.schemas import AnalysisResponse
from app.threat_analysis.service import ThreatModelService

logger = get_logger("controller")


class ThreatAnalysisController:
    """Controller for threat analysis operations."""

    def __init__(self, service: ThreatModelService, settings: Settings) -> None:
        self._service = service
        self._settings = settings

    async def analyze(
        self,
        image_bytes: bytes,
        confidence: float | None = None,
        iou: float | None = None,
    ) -> AnalysisResponse:
        """Execute full threat analysis on an architecture diagram.

        Args:
            image_bytes: Raw image content.
            confidence: Optional detection confidence threshold (for future YOLO).
            iou: Optional IoU threshold (for future YOLO).

        Returns:
            Complete analysis response with components, threats, and risk.

        Raises:
            ThreatModelingError: If analysis fails.
        """
        self._validate_input(image_bytes)

        logger.info(
            "Running analysis: size=%d bytes, confidence=%s, iou=%s",
            len(image_bytes),
            confidence,
            iou,
        )

        result = await self._service.run_full_analysis(image_bytes)
        return result

    def _validate_input(self, image_bytes: bytes) -> None:
        """Validate input before analysis."""
        if not image_bytes or len(image_bytes) == 0:
            raise ThreatModelingError("Empty image content", details={})

        if len(image_bytes) > self._settings.max_upload_size_bytes:
            raise ThreatModelingError(
                f"File too large. Maximum size: {self._settings.max_upload_size_mb}MB",
                details={"max_bytes": self._settings.max_upload_size_bytes},
            )
