"""Tests for app.main."""

from unittest.mock import MagicMock, patch

import pytest

from app.main import _db_check, lifespan


def test_db_check_success():
    """_db_check returns True when DB responds."""
    mock_db = MagicMock()

    def fake_get_db():
        try:
            yield mock_db
        finally:
            pass

    with patch("app.main.get_db", fake_get_db):
        result = _db_check()
    assert result is True
    mock_db.execute.assert_called_once()
    mock_db.close.assert_called_once()


def test_lifespan():
    """lifespan context manager creates tables and disposes engine."""
    import asyncio

    mock_app = MagicMock()

    async def run():
        with patch("app.main.Base.metadata.create_all") as create_all:
            with patch("app.main.engine") as engine:
                async with lifespan(mock_app):
                    pass
                create_all.assert_called_once_with(bind=engine)
                engine.dispose.assert_called_once()

    asyncio.run(run())
