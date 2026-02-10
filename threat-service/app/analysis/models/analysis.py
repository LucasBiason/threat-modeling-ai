"""Analysis model - stores diagram images and analysis results."""

from __future__ import annotations

import enum
import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Enum, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class AnalysisStatus(str, enum.Enum):
    """Analysis processing status."""

    EM_ABERTO = "EM_ABERTO"
    PROCESSANDO = "PROCESSANDO"
    ANALISADO = "ANALISADO"
    FALHOU = "FALHOU"


class Analysis(Base):
    """Analysis entity - image upload and processing result."""

    __tablename__ = "analyses"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    code: Mapped[str] = mapped_column(nullable=False, unique=True, index=True)
    image_path: Mapped[str] = mapped_column(nullable=False)
    status: Mapped[AnalysisStatus] = mapped_column(
        Enum(AnalysisStatus),
        default=AnalysisStatus.EM_ABERTO,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    finished_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    result: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    processing_logs: Mapped[str | None] = mapped_column(Text, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    notifications: Mapped[list["Notification"]] = relationship(
        "Notification",
        back_populates="analysis",
        cascade="all, delete-orphan",
    )


    @property
    def is_open(self) -> bool:
        return self.status == AnalysisStatus.EM_ABERTO

    @property
    def is_processing(self) -> bool:
        return self.status == AnalysisStatus.PROCESSANDO

    @property
    def is_done(self) -> bool:
        return self.status == AnalysisStatus.ANALISADO

    @property
    def is_failed(self) -> bool:
        return self.status == AnalysisStatus.FALHOU