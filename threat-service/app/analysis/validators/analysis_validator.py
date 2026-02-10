"""Validações de entrada para analysis (além dos schemas Pydantic)."""

from fastapi import HTTPException, status

from app.config import get_settings

ALLOWED_IMAGE_TYPES = {"image/png", "image/jpeg", "image/jpg", "image/webp"}


class AnalysisValidator:
    """Validador de arquivos e parâmetros de analysis."""

    def __init__(self) -> None:
        self._settings = get_settings()

    def validate_upload_file(self, content_type: str | None, size: int) -> None:
        """Valida tipo e tamanho do arquivo de upload.
        Raises HTTPException se inválido.
        """
        if not content_type or content_type not in ALLOWED_IMAGE_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file type: {content_type}. Allowed: image/png, image/jpeg, image/webp",
            )
        max_bytes = self._settings.max_upload_size_bytes
        if size > max_bytes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File too large. Maximum: {self._settings.max_upload_size_mb}MB",
            )
