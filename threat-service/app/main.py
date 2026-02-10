"""Threat Modeling API - Orchestrator for async analysis."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from threat_modeling_shared import create_app

# Import models so they are registered with Base
from app.analysis.models import Analysis  # noqa: F401
from app.analysis.routers import router as analyses_router
from app.config import get_settings
from app.database import Base, engine
from app.notification.models import Notification  # noqa: F401
from app.notification.routers import router as notifications_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create tables on startup when database is configured; dispose engine on shutdown."""
    if engine is not None:
        Base.metadata.create_all(bind=engine)
    yield
    if engine is not None:
        engine.dispose()


_settings = get_settings()

app = create_app(
    title=_settings.app_name,
    description="Orchestrator API for threat modeling - upload analyses, track status, receive notifications.",
    version=_settings.app_version,
    routers=[
        (analyses_router, {"prefix": "/api/v1"}),
        (notifications_router, {"prefix": "/api/v1"}),
    ],
    settings=_settings,
    lifespan=lifespan,
    health_system_name=_settings.app_name,
    check_database=None,
    db_check=None,
)
