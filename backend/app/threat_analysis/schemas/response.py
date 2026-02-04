"""API response schemas."""

from enum import Enum

from pydantic import Field, computed_field

from .base import BaseSchema
from .component import Component, Connection
from .threat import Threat


class RiskLevel(str, Enum):
    """Risk level classification."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

    @classmethod
    def from_score(cls, score: float) -> "RiskLevel":
        """Determine risk level from score."""
        if score < 3:
            return cls.LOW
        if score < 6:
            return cls.MEDIUM
        if score < 8:
            return cls.HIGH
        return cls.CRITICAL


class AnalysisResponse(BaseSchema):
    """Complete threat analysis response."""

    model_used: str = Field(..., description="Model used for diagram analysis")
    components: list[Component] = Field(
        default_factory=list,
        description="Detected architecture components",
    )
    connections: list[Connection] = Field(
        default_factory=list,
        description="Detected connections between components",
    )
    threats: list[Threat] = Field(
        default_factory=list,
        description="Identified threats with STRIDE/DREAD analysis",
    )
    risk_score: float = Field(
        ...,
        ge=0,
        le=10,
        description="Overall risk score (0-10)",
    )
    risk_level: RiskLevel = Field(..., description="Risk level classification")
    processing_time: float | None = Field(
        default=None,
        description="Analysis processing time in seconds",
    )

    @computed_field
    @property
    def threat_count(self) -> int:
        """Total number of threats identified."""
        return len(self.threats)

    @computed_field
    @property
    def component_count(self) -> int:
        """Total number of components identified."""
        return len(self.components)
