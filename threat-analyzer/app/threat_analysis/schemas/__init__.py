"""Threat Analysis schemas.

This package defines:
- base: BaseSchema and Pydantic config shared by all schemas.
- component: Diagram structure (Component, Connection, TrustBoundary, DiagramData).
- request: AnalysisRequest and get_analysis_request for the /analyze endpoint.
- response: AnalysisResponse and RiskLevel for the API response.
- threat: STRIDE categories, DreadScore, and Threat for threat modelling output.
"""

from .base import BaseSchema
from .component import Component, Connection, DiagramData, TrustBoundary
from .request import AnalysisRequest, get_analysis_request
from .response import AnalysisResponse, RiskLevel
from .threat import (
    DreadScore,
    StrideCategory,
    Threat,
)

__all__ = [
    "AnalysisRequest",
    "AnalysisResponse",
    "BaseSchema",
    "Component",
    "Connection",
    "DiagramData",
    "DreadScore",
    "RiskLevel",
    "StrideCategory",
    "Threat",
    "TrustBoundary",
    "get_analysis_request",
]
