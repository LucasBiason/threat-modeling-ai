"""Unit tests for app.database."""

from unittest.mock import MagicMock, patch


def test_get_db_yields_session():
    """get_db yields from get_db_generator."""
    mock_session = MagicMock()

    def fake_generator(settings):
        yield mock_session

    with patch("app.database.get_db_generator", fake_generator):
        from app.database import get_db

        gen = get_db()
        session = next(gen)
        assert session is mock_session
        try:
            next(gen)
        except StopIteration:
            pass
