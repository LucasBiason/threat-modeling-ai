"""Threat Modeling AI - FastAPI Application."""

from collections.abc import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from threat_modeling_shared import create_app
from threat_modeling_shared.logging import get_logger, setup_logging

from app.config import get_settings
from app.routers import ROUTERS
from app.services.rag_service import RAGService
from app.threat_analysis.exceptions import (
    ArchitectureDiagramValidationError,
    InvalidFileTypeError,
    ThreatModelingError,
)

_settings = get_settings()
logger = get_logger("main")


async def _lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Startup: logging, warm RAG cache. Shutdown: log."""
    setup_logging(_settings.log_level)
    logger.info("Starting %s v%s", _settings.app_name, _settings.app_version)
    RAGService(_settings).get_retriever()
    yield
    logger.info("Shutting down %s", _settings.app_name)


async def _handle_exception(_request: Request, exc: Exception) -> JSONResponse:
    """Generic handler: map exception type to status and detail."""
    if isinstance(exc, ArchitectureDiagramValidationError):
        return JSONResponse(status_code=400, content={"detail": exc.reason})
    if isinstance(exc, InvalidFileTypeError):
        return JSONResponse(status_code=400, content={"detail": exc.message})
    if isinstance(exc, ThreatModelingError):
        return JSONResponse(
            status_code=400,
            content={"detail": exc.message, "details": exc.details},
        )
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)},
    )


app = create_app(
    title=_settings.app_name,
    description="API for automated threat modeling using STRIDE/DREAD methodologies.",
    version=_settings.app_version,
    routers=ROUTERS,
    settings=_settings,
    health_system_name=_settings.app_name,
    check_database=False,
    exception_handlers=[(Exception, _handle_exception)],
    exception_pass_through=(
        (ArchitectureDiagramValidationError, 400, lambda e: {"detail": e.reason}),
        (InvalidFileTypeError, 400, lambda e: {"detail": e.message}),
        (
            ThreatModelingError,
            400,
            lambda e: {"detail": e.message, "details": e.details},
        ),
    ),
)
