"""Factory for creating standardized FastAPI applications."""

from collections.abc import AsyncGenerator, Callable
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from threat_modeling_shared.logging import get_logger, setup_logging
from threat_modeling_shared.middleware import (
    CatchExceptionsMiddleware,
    LoggingMiddleware,
)
from threat_modeling_shared.routers import create_health_router


def create_app(
    *,
    title: str,
    description: str = "",
    version: str = "1.0.0",
    routers: list[Any],
    settings: Any,
    lifespan: Callable[[FastAPI], AsyncGenerator[None, None]] | None = None,
    health_system_name: str | None = None,
    check_database: bool | None = None,
    db_check: Callable[[], bool] | None = None,
    exception_handlers: list[tuple[type[Exception], Callable]] | None = None,
    custom_error_handler: tuple[type[Exception], str] | None = None,
    exception_pass_through: (
        tuple[tuple[type[Exception], int, Callable[[Exception], dict]], ...]
        | None
    ) = None,
) -> FastAPI:
    """Create and configure a FastAPI application with standard middleware and health.

    Args:
        title: Application title
        description: OpenAPI description
        version: Application version
        routers: List of APIRouter instances
        settings: Settings object with: debug, log_level, cors_origins, cors_allow_credentials,
                  cors_allow_methods, cors_allow_headers
        lifespan: Optional lifespan context manager
        health_system_name: Name for health endpoints (default: title)
        check_database: Whether health checks database
        db_check: Callable for DB check (required if check_database=True)
        exception_handlers: Optional list of (exception_class, handler) for app.exception_handler
        custom_error_handler: Optional (exception_class, log_title) for a built-in handler that logs
            "log_title exc.message" and returns JSONResponse(500, {"error": exc.message, "details": exc.details}).
            The exception type must have .message and .details attributes.

    Returns:
        Configured FastAPI application
    """
    logger = get_logger("main")

    if check_database is None:
        check_database = bool(getattr(settings, "database_url", "") or "")
    if check_database and db_check is None:
        from threat_modeling_shared.database import db_check as _db_check_sync
        db_check = lambda: _db_check_sync(settings)

    @asynccontextmanager
    async def default_lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
        log_level = getattr(settings, "log_level", "INFO")
        setup_logging(log_level)
        app_name = getattr(settings, "app_name", title)
        app_version = getattr(settings, "app_version", version)
        logger.info("Starting %s v%s", app_name, app_version)
        yield
        logger.info("Shutting down %s", app_name)

    app_lifespan = lifespan or default_lifespan

    app = FastAPI(
        title=title,
        description=description,
        version=version,
        lifespan=app_lifespan,
        docs_url="/docs" if getattr(settings, "debug", False) else None,
        redoc_url="/redoc" if getattr(settings, "debug", False) else None,
    )

    # Middleware order: last added = first executed (CORS -> Exceptions -> Logging)
    app.add_middleware(LoggingMiddleware, logger=logger)
    app.add_middleware(
        CatchExceptionsMiddleware,
        logger=logger,
        pass_through=exception_pass_through or (),
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=getattr(settings, "cors_origins", ["*"]),
        allow_credentials=getattr(settings, "cors_allow_credentials", True),
        allow_methods=getattr(settings, "cors_allow_methods", ["*"]),
        allow_headers=getattr(settings, "cors_allow_headers", ["*"]),
    )

    # Built-in handler for exceptions with .message and .details (e.g. ThreatModelingError)
    if custom_error_handler:
        exc_cls, log_title = custom_error_handler

        async def _custom_error_handler(
            request: Request, exc: Exception
        ) -> JSONResponse:
            logger.error("%s %s", log_title, getattr(exc, "message", str(exc)))
            return JSONResponse(
                status_code=500,
                content={
                    "error": getattr(exc, "message", str(exc)),
                    "details": getattr(exc, "details", {}),
                },
            )

        app.add_exception_handler(exc_cls, _custom_error_handler)

    # Custom exception handlers: (ExceptionClass, async handler(request, exc))
    if exception_handlers:
        for exc_cls, handler in exception_handlers:
            app.add_exception_handler(exc_cls, handler)

    # Health router
    health_name = health_system_name or title
    app.include_router(
        create_health_router(
            health_name, check_database=check_database, db_check=db_check
        )
    )

    # Application routers: (router, {prefix, tags}) or router
    for item in routers:
        if isinstance(item, tuple):
            router, opts = item
            app.include_router(router, **opts)
        else:
            app.include_router(item)

    return app
