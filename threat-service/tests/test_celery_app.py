"""Tests for app.celery_app."""

from app.celery_app import celery_app


def test_celery_app_configured():
    """Celery app is configured with expected settings."""
    assert celery_app.conf.task_serializer == "json"
    assert celery_app.conf.accept_content == ["json"]
    assert celery_app.conf.result_serializer == "json"
    assert celery_app.conf.timezone == "UTC"
    assert celery_app.conf.enable_utc is True


def test_celery_beat_schedule():
    """Beat schedule includes scan-pending-analyses."""
    schedule = celery_app.conf.beat_schedule
    assert "scan-pending-analyses" in schedule
    assert schedule["scan-pending-analyses"]["task"] == "app.analysis.tasks.analysis_tasks.scan_pending_analyses"
    assert schedule["scan-pending-analyses"]["schedule"] is not None


def test_celery_includes_tasks():
    """Celery includes analysis tasks."""
    assert "app.analysis.tasks.analysis_tasks" in celery_app.conf.include
