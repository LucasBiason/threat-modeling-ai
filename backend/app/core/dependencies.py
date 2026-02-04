"""FastAPI dependency injection utilities."""

from typing import Annotated

from fastapi import Depends

from .config import Settings, get_settings

# Type alias for dependency injection
SettingsDep = Annotated[Settings, Depends(get_settings)]
