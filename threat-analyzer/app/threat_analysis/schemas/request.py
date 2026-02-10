"""Request schemas for the threat analysis API.

The analyze endpoint expects multipart/form-data: a required image file (the
architecture diagram) and optional form fields for future detection parameters.
"""

from typing import Annotated

from fastapi import File, Form, UploadFile
from pydantic import ConfigDict, Field

from .base import BaseSchema


class AnalysisRequest(BaseSchema):
    """Request payload for POST /analyze (diagram threat analysis).

    The client sends an image of an architecture diagram (PNG, JPEG, WebP, or GIF).
    Optional fields confidence and iou are reserved for future use (e.g. when
    adding object-detection or diagram-element detection with configurable thresholds).
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    file: Annotated[
        UploadFile,
        Field(
            description=(
                "Image file of the architecture diagram. Accepted types: image/png, "
                "image/jpeg, image/webp, image/gif. Content is used for diagram extraction "
                "and STRIDE/DREAD threat analysis."
            ),
        ),
    ]
    confidence: Annotated[
        float | None,
        Field(
            default=None,
            description=(
                "Optional confidence threshold (0.1–0.9) for detection. Reserved for "
                "future use (e.g. minimum confidence for diagram element detection)."
            ),
            examples=[0.5],
        ),
    ] = None
    iou: Annotated[
        float | None,
        Field(
            default=None,
            description=(
                "Optional Intersection over Union (IoU) threshold (0.1–0.9). Reserved for "
                "future use (e.g. overlap threshold for bounding boxes in detection)."
            ),
            examples=[0.5],
        ),
    ] = None


def get_analysis_request(
    file: UploadFile = File(
        ...,
        description=(
            "Architecture diagram image. Accepted: image/png, image/jpeg, image/webp, image/gif."
        ),
    ),
    confidence: float | None = Form(
        None,
        description="Optional confidence threshold (0.1–0.9). Reserved for future use.",
    ),
    iou: float | None = Form(
        None,
        description="Optional IoU threshold (0.1–0.9). Reserved for future use.",
    ),
) -> AnalysisRequest:
    """Build AnalysisRequest from multipart file and form fields (FastAPI dependency)."""
    return AnalysisRequest(file=file, confidence=confidence, iou=iou)
