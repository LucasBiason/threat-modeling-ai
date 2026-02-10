"""Unit tests for app.config."""


from app.config import Settings, get_settings


def _clear_settings_cache():
    get_settings.cache_clear()


class TestSettings:
    def test_defaults(self):
        _clear_settings_cache()
        s = Settings()
        assert s.app_name == "Threat Modeling AI"
        assert s.log_level == "INFO"

    def test_cors_origins_single(self, monkeypatch):
        _clear_settings_cache()
        monkeypatch.setenv("CORS_ORIGINS", "https://example.com")
        s = Settings()
        assert s.cors_origins == ["https://example.com"]

    def test_cors_origins_multiple(self, monkeypatch):
        _clear_settings_cache()
        monkeypatch.setenv("CORS_ORIGINS", "a.com, b.com")
        s = Settings()
        assert s.cors_origins == ["a.com", "b.com"]

    def test_max_upload_size_bytes(self):
        s = Settings(max_upload_size_mb=5)
        assert s.max_upload_size_bytes == 5 * 1024 * 1024

    def test_parse_knowledge_base_path_none(self):
        """When None, validator defaults to app/rag_data if it exists, else None."""
        s = Settings(knowledge_base_path=None)
        assert s.knowledge_base_path is None or (
            s.knowledge_base_path is not None
            and s.knowledge_base_path.name == "rag_data"
        )

    def test_parse_knowledge_base_path_missing(self):
        s = Settings(knowledge_base_path="/nonexistent/path")
        assert s.knowledge_base_path is None


def test_get_settings_cached():
    _clear_settings_cache()
    a = get_settings()
    b = get_settings()
    assert a is b
