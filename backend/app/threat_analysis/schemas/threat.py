"""Threat and scoring schemas."""

from enum import Enum

from pydantic import Field, field_validator

from .base import BaseSchema


class StrideCategory(str, Enum):
    """STRIDE threat categories."""

    SPOOFING = "Spoofing"
    TAMPERING = "Tampering"
    REPUDIATION = "Repudiation"
    INFORMATION_DISCLOSURE = "Information Disclosure"
    DENIAL_OF_SERVICE = "Denial of Service"
    ELEVATION_OF_PRIVILEGE = "Elevation of Privilege"


class DreadScore(BaseSchema):
    """DREAD risk scoring details."""

    damage: int = Field(..., ge=1, le=10, description="Damage potential (1-10)")
    reproducibility: int = Field(..., ge=1, le=10, description="Reproducibility (1-10)")
    exploitability: int = Field(..., ge=1, le=10, description="Exploitability (1-10)")
    affected_users: int = Field(..., ge=1, le=10, description="Affected users (1-10)")
    discoverability: int = Field(..., ge=1, le=10, description="Discoverability (1-10)")

    @property
    def average(self) -> float:
        """Calculate the average DREAD score."""
        return (
            self.damage
            + self.reproducibility
            + self.exploitability
            + self.affected_users
            + self.discoverability
        ) / 5


class Threat(BaseSchema):
    """A detected threat with STRIDE classification and DREAD scoring."""

    component_id: str = Field(..., description="ID of the affected component")
    threat_type: str = Field(..., description="STRIDE category")
    description: str = Field(..., description="Threat description")
    mitigation: str = Field(..., description="Recommended mitigation")
    dread_score: float | None = Field(
        default=None,
        ge=0,
        le=10,
        description="Average DREAD score (1-10)",
    )
    dread_details: DreadScore | None = Field(
        default=None,
        description="Detailed DREAD scores",
    )

    @field_validator("dread_score", mode="before")
    @classmethod
    def round_dread_score(cls, v: float | None) -> float | None:
        """Round DREAD score to 2 decimal places."""
        if v is not None:
            return round(v, 2)
        return v
