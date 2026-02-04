"""Threat Modeling AI - FastAPI Application."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.logging import get_logger, setup_logging
from app.middlewares import CatchExceptionsMiddleware, LoggingMiddleware
from app.routes.health import health_router
from app.threat_analysis.router import router as threat_router
from app.threat_analysis.exceptions import ThreatModelingError

logger = get_logger("main")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan handler for startup/shutdown events."""
    settings = get_settings()
    setup_logging(settings.log_level)
    logger.info("Starting %s v%s", settings.app_name, settings.app_version)
    yield
    logger.info("Shutting down %s", settings.app_name)


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        description="API for automated threat modeling using STRIDE/DREAD methodologies.",
        version=settings.app_version,
        lifespan=lifespan,
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
    )

    # Logging layer
    app.add_middleware(LoggingMiddleware, logger=logger)
    # Exception handling
    app.add_middleware(CatchExceptionsMiddleware, logger=logger)
    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=settings.cors_allow_methods,
        allow_headers=settings.cors_allow_headers,
    )

    # Custom exception handler for ThreatModelingError
    from fastapi import Request
    from fastapi.responses import JSONResponse

    @app.exception_handler(ThreatModelingError)
    async def threat_modeling_exception_handler(
        request: Request,
        exc: ThreatModelingError,
    ) -> JSONResponse:
        logger.error("ThreatModelingError: %s", exc.message)
        return JSONResponse(
            status_code=500,
            content={"error": exc.message, "details": exc.details},
        )

    # Routers
    app.include_router(health_router)
    app.include_router(
        threat_router,
        prefix="/api/v1/threat-model",
        tags=["Threat Modeling"],
    )

    return app


app = create_app()
