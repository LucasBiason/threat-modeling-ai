"""Database configuration and session — shared by services that use PostgreSQL.

When settings.database_url is set (non-empty), the service uses the database:
lifespan can create tables and dispose engine; health can check connectivity.
When database_url is empty, get_engine and get_session_factory return None.
"""

from collections.abc import Generator
from typing import Any

from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


class Base(DeclarativeBase):
    """Base class for ORM models. Services import this for their entities."""
    pass


def get_engine(settings: Any):
    """Create engine from settings.database_url. Returns None if database_url is empty."""
    url = getattr(settings, "database_url", "") or ""
    if not url.strip():
        return None
    return create_engine(
        url,
        pool_pre_ping=True,
        echo=getattr(settings, "debug", False),
    )


def get_session_factory(settings: Any):
    """Return sessionmaker(bind=engine) or None if database is not configured."""
    engine = get_engine(settings)
    if engine is None:
        return None
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db_generator(settings: Any) -> Generator[Session, None, None]:
    """Yield a database session. Yields nothing if database is not configured."""
    factory = get_session_factory(settings)
    if factory is None:
        return
    db = factory()
    try:
        yield db
    finally:
        db.close()


def db_check(settings: Any) -> bool:
    """Check database connectivity. Returns True if OK or if database is not configured."""
    factory = get_session_factory(settings)
    if factory is None:
        return True
    db = factory()
    try:
        db.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
    finally:
        db.close()
