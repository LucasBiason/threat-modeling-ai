"""Health check router for Threat Modeling AI."""

import os
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Request

router = APIRouter(tags=["Health"])


def create_health_router(system_name: str = "Threat Modeling AI") -> APIRouter:
    """Create health router with standard endpoints."""
    r = APIRouter(tags=["Health"])

    async def health_check_handler(request: Request) -> dict[str, Any]:
        system_version = os.getenv("SYSTEM_VERSION", os.getenv("APP_VERSION", "1.0.0"))
        environment = os.getenv("ENVIRONMENT", "development")
        return {
            "status": "healthy",
            "system_name": system_name,
            "system_version": system_version,
            "environment": environment,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "database": "not_required",
            "endpoint": request.url.path,
        }

    r.add_api_route("/", health_check_handler, methods=["GET"], name="health-root")
    r.add_api_route("/health", health_check_handler, methods=["GET"], name="health")
    r.add_api_route("/health/", health_check_handler, methods=["GET"], name="health-slash")

    @r.get("/health/ready")
    async def readiness_check(request: Request) -> dict[str, Any]:
        return {
            "status": "ready",
            "system_name": system_name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "endpoint": "/health/ready",
        }

    @r.get("/health/live")
    async def liveness_check(request: Request) -> dict[str, Any]:
        return {
            "status": "alive",
            "system_name": system_name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "endpoint": "/health/live",
        }

    return r


health_router = create_health_router()
