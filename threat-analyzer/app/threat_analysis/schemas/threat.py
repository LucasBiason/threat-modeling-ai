"""Threat and risk scoring schemas (STRIDE and DREAD).

STRIDE classifies the kind of threat; DREAD scores impact and likelihood.
Together they support prioritised, consistent threat reporting.
"""

from enum import Enum

from pydantic import Field, field_validator

from .base import BaseSchema


class StrideCategory(str, Enum):
    """STRIDE threat categories (Microsoft threat modelling).

    Each value represents one of the six threat types used to classify
    and communicate security threats in the analysis.
    """

    SPOOFING = "Spoofing"
    TAMPERING = "Tampering"
    REPUDIATION = "Repudiation"
    INFORMATION_DISCLOSURE = "Information Disclosure"
    DENIAL_OF_SERVICE = "Denial of Service"
    ELEVATION_OF_PRIVILEGE = "Elevation of Privilege"


class DreadScore(BaseSchema):
    """Per-threat DREAD scoring: five dimensions, each 1–10.

    DREAD = Damage, Reproducibility, Exploitability, Affected users, Discoverability.
    The average of these gives the overall DREAD score for the threat.
    """

    damage: int = Field(
        ...,
        ge=1,
        le=10,
        description="Damage potential (1–10): impact if the threat is realised.",
    )
    reproducibility: int = Field(
        ...,
        ge=1,
        le=10,
        description="Reproducibility (1–10): how easy it is to reproduce the attack.",
    )
    exploitability: int = Field(
        ...,
        ge=1,
        le=10,
        description="Exploitability (1–10): effort required to exploit the weakness.",
    )
    affected_users: int = Field(
        ...,
        ge=1,
        le=10,
        description="Affected users (1–10): how many users/systems are impacted.",
    )
    discoverability: int = Field(
        ...,
        ge=1,
        le=10,
        description="Discoverability (1–10): how easy it is to find the vulnerability.",
    )

    @property
    def average(self) -> float:
        """Arithmetic mean of the five DREAD dimensions (1–10)."""
        return (
            self.damage
            + self.reproducibility
            + self.exploitability
            + self.affected_users
            + self.discoverability
        ) / 5


class Threat(BaseSchema):
    """A single identified threat: STRIDE type, description, mitigation, and DREAD.

    Links to a component via component_id. threat_type is a STRIDE category;
    dread_score is the average DREAD (or from dread_details), and dread_details
    holds the full per-dimension scores when available.
    """

    component_id: str = Field(
        ...,
        description="Id of the architecture component this threat applies to.",
    )
    threat_type: str = Field(
        ...,
        description="STRIDE category (e.g. Spoofing, Information Disclosure).",
    )
    description: str = Field(
        ...,
        description="Human-readable description of the threat and attack scenario.",
    )
    mitigation: str = Field(
        ...,
        description="Recommended mitigation or control to reduce the threat.",
    )
    dread_score: float | None = Field(
        default=None,
        ge=0,
        le=10,
        description="Overall DREAD score (0–10), usually the average of dread_details.",
    )
    dread_details: DreadScore | None = Field(
        default=None,
        description="Per-dimension DREAD scores (Damage, Reproducibility, etc.) when available.",
    )

    @field_validator("dread_score", mode="before")
    @classmethod
    def round_dread_score(cls, v: float | None) -> float | None:
        """Round the aggregate DREAD score to two decimal places."""
        if v is not None:
            return round(v, 2)
        return v
