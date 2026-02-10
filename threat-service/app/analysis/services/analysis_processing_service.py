"""Orchestration service for analysis processing."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.config import get_settings
from app.analysis.repositories.analysis_repository import AnalysisRepository
from app.analysis.services.analysis_service import AnalysisService, AnalysisServiceError
from app.notification.repositories.notification_repository import NotificationRepository


def _append_log(repo: AnalysisRepository, analysis_id: uuid.UUID, msg: str) -> None:
    """Append log line to analysis."""
    repo.append_processing_log(analysis_id, msg)


def _fail_analysis(
    repo: AnalysisRepository,
    analysis_id: uuid.UUID,
    analysis_id_str: str,
    error_message: str,
    log_message: str | None = None,
) -> dict[str, Any]:
    """Log error, mark analysis as failed, and return standard error response."""
    _append_log(repo, analysis_id, log_message or error_message)
    repo.mark_failed(
        analysis_id,
        finished_at=datetime.now(timezone.utc),
        error_message=error_message,
    )
    return {"error": error_message, "analysis_id": analysis_id_str}


class AnalysisProcessingService:
    """Service responsible for orchestrating analysis processing (threat-analyzer call, status updates, notification)."""

    def __init__(self, db: Session) -> None:
        self._db = db
        self._analysis_repo = AnalysisRepository(db)
        self._notification_repo = NotificationRepository(db)

    def process(self, analysis_id: uuid.UUID) -> dict[str, Any]:
        """
        Process a single analysis: call threat-analyzer, save result, create notification.

        Returns:
            Dict with keys: analysis_id, status (or error/skipped), threat_count, risk_level when successful.
        """
        analysis = self._analysis_repo.get_by_id(analysis_id)
        if not analysis:
            return {"error": "Analysis not found", "analysis_id": str(analysis_id)}
        if analysis.is_done or analysis.is_failed:
            return {"skipped": "Already done", "analysis_id": str(analysis_id)}

        if analysis.is_open:
            self._analysis_repo.mark_processing(
                analysis_id, started_at=datetime.now(timezone.utc)
            )
        _append_log(
            self._analysis_repo,
            analysis_id,
            f"[{datetime.now(timezone.utc).isoformat()}] Processamento iniciado",
        )

        image_path = self._analysis_repo.get_image_path(analysis_id)
        if not image_path or not image_path.exists():
            return _fail_analysis(
                self._analysis_repo, analysis_id, str(analysis_id), "Image file not found"
            )

        settings = get_settings()
        analysis_service = AnalysisService(settings.analyzer_url)
        _append_log(
            self._analysis_repo,
            analysis_id,
            f"Chamando threat-analyzer em {analysis_service.analyze_endpoint}",
        )

        try:
            result = analysis_service.analyze(image_path, analysis.image_path)
        except AnalysisServiceError as e:
            return _fail_analysis(
                self._analysis_repo,
                analysis_id,
                str(analysis_id),
                e.message,
                log_message=e.message,
            )

        _append_log(
            self._analysis_repo,
            analysis_id,
            f"Análise concluída: {len(result.get('threats', []))} ameaças",
        )

        self._analysis_repo.mark_analysed(
            analysis_id,
            finished_at=datetime.now(timezone.utc),
            result=result,
        )

        risk_level = result.get("risk_level", "N/A")
        threat_count = len(result.get("threats", []))
        self._notification_repo.create(
            analysis_id,
            title="Análise Concluída",
            message=f"Análise {analysis.code} concluída. Risco: {risk_level}. {threat_count} ameaças identificadas.",
            link=f"/analyses/{analysis_id}",
        )

        return {
            "analysis_id": str(analysis_id),
            "status": "ANALISADO",
            "threat_count": threat_count,
            "risk_level": risk_level,
        }
