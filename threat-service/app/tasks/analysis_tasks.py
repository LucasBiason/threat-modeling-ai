"""Celery tasks for analysis processing (legacy module — delegates to app.analysis.tasks)."""

from __future__ import annotations

# Re-export so any code using app.tasks.analysis_tasks still works.
from app.analysis.tasks.analysis_tasks import (  # noqa: F401
    process_analysis,
    scan_pending_analyses,
)
