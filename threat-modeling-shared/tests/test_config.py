"""Tests for threat_modeling_shared.config module."""  # pragma: allowlist secret

from threat_modeling_shared.config import BaseSettings, parse_cors_origins  # pragma: allowlist secret


class TestParseCorsOrigins:
    def test_none_returns_wildcard(self):
        assert parse_cors_origins(None) == ["*"]

    def test_list_returned_as_is(self):
        origins = ["http://localhost:3000", "http://example.com"]
        assert parse_cors_origins(origins) == origins

    def test_single_origin_string(self):
        assert parse_cors_origins("http://localhost:3000") == ["http://localhost:3000"]

    def test_multiple_comma_separated(self):
        result = parse_cors_origins("http://a.com, http://b.com , http://c.com")
        assert result == ["http://a.com", "http://b.com", "http://c.com"]

    def test_empty_string_returns_wildcard(self):
        assert parse_cors_origins("") == ["*"]

    def test_whitespace_only_returns_wildcard(self):
        assert parse_cors_origins("  ,  , ") == ["*"]

    def test_wildcard_string(self):
        assert parse_cors_origins("*") == ["*"]

    def test_trailing_comma(self):
        result = parse_cors_origins("http://a.com,")
        assert result == ["http://a.com"]

    def test_empty_list(self):
        assert parse_cors_origins([]) == []


class TestBaseSettings:
    def test_default_values(self):
        settings = BaseSettings(
            redis_url="redis://localhost:6379/0",
            database_url="",
            cors_origins="*",
        )
        assert settings.app_name == "Threat Modeling AI"
        assert settings.app_version == "1.0.0"
        assert settings.debug is False
        assert settings.log_level == "INFO"
        assert settings.redis_url == "redis://localhost:6379/0"
        assert settings.database_url == ""

    def test_cors_origins_property_default(self):
        settings = BaseSettings(cors_origins="*")
        assert settings.cors_origins == ["*"]

    def test_cors_origins_property_custom(self):
        settings = BaseSettings(cors_origins="http://a.com,http://b.com")
        assert settings.cors_origins == ["http://a.com", "http://b.com"]

    def test_cors_defaults(self):
        settings = BaseSettings()
        assert settings.cors_allow_credentials is True
        assert settings.cors_allow_methods == ["*"]
        assert settings.cors_allow_headers == ["*"]
