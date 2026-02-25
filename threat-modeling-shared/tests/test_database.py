"""Tests for database module."""

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from threat_modeling_shared.database import (  # pragma: allowlist secret
    Base,
    db_check,
    get_db_generator,
    get_engine,
    get_session_factory,
)


class TestGetEngine:
    @patch("threat_modeling_shared.database.create_engine")  # pragma: allowlist secret
    def test_returns_engine_when_url_set(self, mock_create_engine):
        mock_engine = MagicMock()
        mock_create_engine.return_value = mock_engine
        settings = SimpleNamespace(database_url="postgresql://localhost/testdb", debug=False)  # pragma: allowlist secret

        result = get_engine(settings)

        mock_create_engine.assert_called_once_with(
            "postgresql://localhost/testdb",  # pragma: allowlist secret
            pool_pre_ping=True,
            echo=False,
        )
        assert result is mock_engine

    def test_returns_none_when_url_empty(self):
        settings = SimpleNamespace(database_url="")
        assert get_engine(settings) is None

    def test_returns_none_when_url_whitespace(self):
        settings = SimpleNamespace(database_url="   ")
        assert get_engine(settings) is None

    def test_returns_none_when_no_database_url_attr(self):
        settings = SimpleNamespace()
        assert get_engine(settings) is None

    @patch("threat_modeling_shared.database.create_engine")  # pragma: allowlist secret
    def test_echo_from_debug_true(self, mock_create_engine):
        settings = SimpleNamespace(database_url="postgresql://localhost/db", debug=True)  # pragma: allowlist secret
        get_engine(settings)
        mock_create_engine.assert_called_once_with(
            "postgresql://localhost/db",  # pragma: allowlist secret
            pool_pre_ping=True,
            echo=True,
        )

    @patch("threat_modeling_shared.database.create_engine")  # pragma: allowlist secret
    def test_debug_defaults_false_when_missing(self, mock_create_engine):
        settings = SimpleNamespace(database_url="postgresql://localhost/db")  # pragma: allowlist secret
        get_engine(settings)
        mock_create_engine.assert_called_once_with(
            "postgresql://localhost/db",  # pragma: allowlist secret
            pool_pre_ping=True,
            echo=False,
        )

    def test_returns_none_when_url_is_none(self):
        settings = SimpleNamespace(database_url=None)
        assert get_engine(settings) is None


class TestGetSessionFactory:
    @patch("threat_modeling_shared.database.get_engine")  # pragma: allowlist secret
    @patch("threat_modeling_shared.database.sessionmaker")  # pragma: allowlist secret
    def test_returns_sessionmaker_when_engine_exists(self, mock_sessionmaker, mock_get_engine):
        mock_engine = MagicMock()
        mock_get_engine.return_value = mock_engine
        mock_factory = MagicMock()
        mock_sessionmaker.return_value = mock_factory
        settings = SimpleNamespace(database_url="postgresql://localhost/db")  # pragma: allowlist secret

        result = get_session_factory(settings)

        mock_sessionmaker.assert_called_once_with(
            autocommit=False, autoflush=False, bind=mock_engine
        )
        assert result is mock_factory

    @patch("threat_modeling_shared.database.get_engine")  # pragma: allowlist secret
    def test_returns_none_when_no_engine(self, mock_get_engine):
        mock_get_engine.return_value = None
        settings = SimpleNamespace(database_url="")

        result = get_session_factory(settings)

        assert result is None


class TestGetDbGenerator:
    @patch("threat_modeling_shared.database.get_session_factory")  # pragma: allowlist secret
    def test_yields_session(self, mock_get_factory):
        mock_session = MagicMock()
        mock_factory = MagicMock(return_value=mock_session)
        mock_get_factory.return_value = mock_factory
        settings = SimpleNamespace(database_url="postgresql://localhost/db")  # pragma: allowlist secret

        gen = get_db_generator(settings)
        session = next(gen)
        assert session is mock_session

        try:
            next(gen)
        except StopIteration:
            pass

        mock_session.close.assert_called_once()

    @patch("threat_modeling_shared.database.get_session_factory")  # pragma: allowlist secret
    def test_returns_nothing_when_no_factory(self, mock_get_factory):
        mock_get_factory.return_value = None
        settings = SimpleNamespace(database_url="")

        gen = get_db_generator(settings)
        results = list(gen)
        assert results == []

    @patch("threat_modeling_shared.database.get_session_factory")  # pragma: allowlist secret
    def test_closes_session_on_exception(self, mock_get_factory):
        mock_session = MagicMock()
        mock_factory = MagicMock(return_value=mock_session)
        mock_get_factory.return_value = mock_factory
        settings = SimpleNamespace(database_url="postgresql://localhost/db")  # pragma: allowlist secret

        gen = get_db_generator(settings)
        next(gen)
        try:
            gen.throw(ValueError("test error"))
        except ValueError:
            pass

        mock_session.close.assert_called_once()


class TestDbCheck:
    @patch("threat_modeling_shared.database.get_session_factory")  # pragma: allowlist secret
    def test_returns_true_when_no_factory(self, mock_get_factory):
        mock_get_factory.return_value = None
        settings = SimpleNamespace(database_url="")

        assert db_check(settings) is True

    @patch("threat_modeling_shared.database.get_session_factory")  # pragma: allowlist secret
    def test_returns_true_on_success(self, mock_get_factory):
        mock_session = MagicMock()
        mock_factory = MagicMock(return_value=mock_session)
        mock_get_factory.return_value = mock_factory
        settings = SimpleNamespace(database_url="postgresql://localhost/db")  # pragma: allowlist secret

        result = db_check(settings)

        assert result is True
        mock_session.execute.assert_called_once()
        mock_session.close.assert_called_once()

    @patch("threat_modeling_shared.database.get_session_factory")  # pragma: allowlist secret
    def test_returns_false_on_exception(self, mock_get_factory):
        mock_session = MagicMock()
        mock_session.execute.side_effect = Exception("connection failed")
        mock_factory = MagicMock(return_value=mock_session)
        mock_get_factory.return_value = mock_factory
        settings = SimpleNamespace(database_url="postgresql://localhost/db")  # pragma: allowlist secret

        result = db_check(settings)

        assert result is False
        mock_session.close.assert_called_once()


class TestBase:
    def test_base_is_declarative(self):
        from sqlalchemy.orm import DeclarativeBase
        assert issubclass(Base, DeclarativeBase)
