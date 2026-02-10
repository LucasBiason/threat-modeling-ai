"""Base schema configuration for threat analysis payloads.

All request/response and domain schemas inherit from BaseSchema to ensure
consistent behaviour: ORM-friendly (from_attributes), alias support (populate_by_name),
and trimmed string fields.
"""

from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    """Base Pydantic model for all threat analysis schemas.

    Config enables:
    - from_attributes: allow creation from ORM/dict-like objects (e.g. DB models).
    - populate_by_name: accept both field name and alias (e.g. \"from\" for from_id).
    - str_strip_whitespace: strip leading/trailing spaces on string fields.
    """

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        str_strip_whitespace=True,
    )
