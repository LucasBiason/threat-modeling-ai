"""Routers - list of (router, options) for create_app."""

from app.routers.threat_model import router as threat_model_router

ROUTERS = [
    (
        threat_model_router,
        {"prefix": "/api/v1/threat-model", "tags": ["Threat Modeling"]},
    ),
]
