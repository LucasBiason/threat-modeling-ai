"""Analysis schemas."""

from datetime import date, datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class AnalysisStatusEnum(str, Enum):
    """Analysis status values."""

    EM_ABERTO = "EM_ABERTO"
    PROCESSANDO = "PROCESSANDO"
    ANALISADO = "ANALISADO"
    FALHOU = "FALHOU"


class AnalysisFilter(BaseModel):
    """
    Filtros para listagem de análises (query params).
    Usado com Depends(AnalysisFilter) no router; paginação via fastapi-pagination Params.
    """

    code: str | None = Field(None, description="Parte do código (case insensitive)")
    status: AnalysisStatusEnum | None = Field(None, description="Status da análise")
    created_at_from: date | None = Field(
        None, description="Data inicial do range (inclusivo)"
    )
    created_at_to: date | None = Field(
        None, description="Data final do range (inclusivo)"
    )


class AnalysisCreateResponse(BaseModel):
    """Response when creating a new analysis."""

    id: str = Field(..., description="Analysis UUID")
    code: str = Field(..., description="Human-readable code (e.g. TMA-001)")
    status: AnalysisStatusEnum = Field(..., description="Current status")
    created_at: datetime = Field(..., description="Creation timestamp")
    image_url: str | None = Field(None, description="URL to access image preview")


class AnalysisListResponse(BaseModel):
    """Analysis item in list view."""

    id: str
    code: str
    status: AnalysisStatusEnum
    created_at: datetime
    image_url: str | None = None
    risk_level: str | None = None
    risk_score: float | None = None
    threat_count: int | None = None


class AnalysisDetailResponse(BaseModel):
    """Full analysis detail including result when ANALISADO."""

    id: str
    code: str
    status: AnalysisStatusEnum
    created_at: datetime
    started_at: datetime | None = None
    finished_at: datetime | None = None
    image_url: str | None = None
    processing_logs: str | None = None
    error_message: str | None = None
    result: dict[str, Any] | None = None
