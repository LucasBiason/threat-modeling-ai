"""Routers for FastAPI applications."""

from threat_modeling_shared.routers.health import create_health_router

__all__ = ["create_health_router"]
