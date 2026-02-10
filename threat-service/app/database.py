"""Database — thin wrapper over threat_modeling_shared.database.

Exposes Base, engine, SessionLocal and get_db for the app. When settings.database_url
is set, engine and SessionLocal are configured; otherwise they are None and get_db
must not be used (or will raise).
"""

from collections.abc import Generator

from threat_modeling_shared.database import (
    Base,
    get_engine,
    get_session_factory,
    get_db_generator,
)

from app.config import get_settings

_settings = get_settings()
engine = get_engine(_settings)
SessionLocal = get_session_factory(_settings)


def get_db() -> Generator:
    """FastAPI dependency: yield a DB session. Requires database_url to be set."""
    yield from get_db_generator(_settings)
