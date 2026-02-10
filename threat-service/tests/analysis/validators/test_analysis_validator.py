"""Unit tests for app.analysis.validators.analysis_validator."""

from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

from app.analysis.validators.analysis_validator import (
    ALLOWED_IMAGE_TYPES,
    AnalysisValidator,
)


class TestAnalysisValidator:
    """Tests for AnalysisValidator."""

    def test_validate_upload_file_valid_png(self):
        """Valid PNG content type passes."""
        with patch("app.analysis.validators.analysis_validator.get_settings") as m:
            s = MagicMock()
            s.max_upload_size_bytes = 10 * 1024 * 1024
            m.return_value = s
            v = AnalysisValidator()
            v.validate_upload_file("image/png", 1000)

    def test_validate_upload_file_valid_jpeg(self):
        """Valid JPEG content type passes."""
        with patch("app.analysis.validators.analysis_validator.get_settings") as m:
            s = MagicMock()
            s.max_upload_size_bytes = 10 * 1024 * 1024
            m.return_value = s
            v = AnalysisValidator()
            v.validate_upload_file("image/jpeg", 500)

    def test_validate_upload_file_invalid_type(self):
        """Invalid content type raises 400."""
        with patch("app.analysis.validators.analysis_validator.get_settings") as m:
            m.return_value = MagicMock(max_upload_size_bytes=10 * 1024 * 1024)
            v = AnalysisValidator()
            with pytest.raises(HTTPException) as exc_info:
                v.validate_upload_file("application/pdf", 100)
            assert exc_info.value.status_code == 400

    def test_validate_upload_file_none_type(self):
        """None content type raises 400."""
        with patch("app.analysis.validators.analysis_validator.get_settings") as m:
            m.return_value = MagicMock(max_upload_size_bytes=10 * 1024 * 1024)
            v = AnalysisValidator()
            with pytest.raises(HTTPException) as exc_info:
                v.validate_upload_file(None, 100)
            assert exc_info.value.status_code == 400

    def test_validate_upload_file_too_large(self):
        """File exceeding max size raises 400."""
        with patch("app.analysis.validators.analysis_validator.get_settings") as m:
            s = MagicMock()
            s.max_upload_size_bytes = 100
            s.max_upload_size_mb = 0.0001
            m.return_value = s
            v = AnalysisValidator()
            with pytest.raises(HTTPException) as exc_info:
                v.validate_upload_file("image/png", 200)
            assert exc_info.value.status_code == 400

    def test_allowed_image_types(self):
        """ALLOWED_IMAGE_TYPES contains expected types."""
        assert "image/png" in ALLOWED_IMAGE_TYPES
        assert "image/jpeg" in ALLOWED_IMAGE_TYPES
        assert "image/webp" in ALLOWED_IMAGE_TYPES
