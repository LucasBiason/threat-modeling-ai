"""Threat Analysis API router - views only, delegates to controller."""

from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status

from app.core.config import get_settings
from app.core.dependencies import SettingsDep
from app.core.logging import get_logger
from app.threat_analysis.controllers import ThreatAnalysisController
from app.threat_analysis.exceptions import ThreatModelingError
from app.threat_analysis.schemas import AnalysisResponse
from app.threat_analysis.service import ThreatModelService, get_threat_model_service

logger = get_logger("router")

router = APIRouter()

ServiceDep = Annotated[ThreatModelService, Depends(get_threat_model_service)]


def get_controller(
    settings: SettingsDep,
    service: ServiceDep,
) -> ThreatAnalysisController:
    """Dependency to get ThreatAnalysisController."""
    return ThreatAnalysisController(service, settings)


@router.post(
    "/analyze",
    response_model=AnalysisResponse,
    summary="Analyze Architecture Diagram",
    description="Upload an architecture diagram image to receive STRIDE/DREAD threat analysis.",
)
async def analyze_diagram(
    settings: SettingsDep,
    controller: Annotated[ThreatAnalysisController, Depends(get_controller)],
    file: UploadFile = File(..., description="Architecture diagram image"),
    confidence: float | None = Form(None, description="Confidence threshold (0.1-0.9)"),
    iou: float | None = Form(None, description="IoU threshold (0.1-0.9)"),
) -> AnalysisResponse:
    """Analyze an architecture diagram for security threats."""
    if file.content_type not in settings.allowed_image_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type: {file.content_type}. Allowed: {', '.join(settings.allowed_image_types)}",
        )

    contents = await file.read()

    try:
        return await controller.analyze(contents, confidence=confidence, iou=iou)
    except ThreatModelingError as e:
        logger.error("Analysis failed: %s", e.message)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=e.message,
        ) from e
