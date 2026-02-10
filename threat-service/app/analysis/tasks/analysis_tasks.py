"""Celery tasks for analysis processing."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from app.analysis.repositories.analysis_repository import AnalysisRepository
from app.analysis.services.analysis_processing_service import AnalysisProcessingService
from app.celery_app import celery_app
from app.database import SessionLocal


@celery_app.task(name="app.analysis.tasks.analysis_tasks.scan_pending_analyses")
def scan_pending_analyses() -> str | None:
    """Scan for open analyses and trigger process_analysis for the first one."""
    db = SessionLocal()
    try:
        repo = AnalysisRepository(db)
        analysis = repo.get_pending()
        if not analysis:
            return None
        repo.mark_processing(analysis.id, started_at=datetime.now(timezone.utc))
        process_analysis.delay(str(analysis.id))
        return str(analysis.id)
    finally:
        db.close()


@celery_app.task(name="app.analysis.tasks.analysis_tasks.process_analysis", bind=True)
def process_analysis(self, analysis_id: str) -> dict:
    """Process a single analysis via AnalysisProcessingService (threat-analyzer, status, notification)."""
    db = SessionLocal()
    try:
        service = AnalysisProcessingService(db)
        return service.process(uuid.UUID(analysis_id))
    finally:
        db.close()
