"""Health check router for microservices."""

import os
from collections.abc import Callable
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse


def create_health_router(
    system_name: str,
    check_database: bool = False,
    db_check: Callable[[], bool] | None = None,
) -> APIRouter:
    """Create health router with standard endpoints.

    Args:
        system_name: Name of the service (e.g. "Threat Modeling AI")
        check_database: Whether to check database connectivity
        db_check: Callable that returns True if DB is OK. Required if check_database=True.

    Returns:
        APIRouter with /, /health, /health/ready, /health/live
    """
    router = APIRouter(tags=["Health"])

    async def health_check_handler(request: Request) -> dict[str, Any]:
        if check_database and db_check is not None:
            try:
                db_check()
                db_status = "healthy"
            except Exception as e:
                db_status = f"unhealthy: {str(e)}"
        else:
            db_status = "not_required"

        system_version = os.getenv("SYSTEM_VERSION", os.getenv("APP_VERSION", "1.0.0"))
        environment = os.getenv("ENVIRONMENT", "development")

        health_data = {
            "status": "healthy" if "unhealthy" not in db_status else "degraded",
            "system_name": system_name,
            "system_version": system_version,
            "environment": environment,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "database": db_status,
            "endpoint": request.url.path,
        }
        return health_data

    router.add_api_route("/", health_check_handler, methods=["GET"], name="health-root")
    router.add_api_route(
        "/health", health_check_handler, methods=["GET"], name="health"
    )
    router.add_api_route(
        "/health/", health_check_handler, methods=["GET"], name="health-slash"
    )

    @router.get("/health/ready", response_model=None)
    async def readiness_check(request: Request):
        if check_database and db_check is not None:
            try:
                db_check()
                return {
                    "status": "ready",
                    "system_name": system_name,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "endpoint": "/health/ready",
                }
            except Exception as e:
                return JSONResponse(
                    status_code=503,
                    content={
                        "status": "not_ready",
                        "system_name": system_name,
                        "error": str(e),
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "endpoint": "/health/ready",
                    },
                )
        return {
            "status": "ready",
            "system_name": system_name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "endpoint": "/health/ready",
        }

    @router.get("/health/live")
    async def liveness_check(request: Request) -> dict[str, Any]:
        return {
            "status": "alive",
            "system_name": system_name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "endpoint": "/health/live",
        }

    return router
