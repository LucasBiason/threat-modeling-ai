"""Notification schemas — Response e documentação da API."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class NotificationResponse(BaseModel):
    """Schema de resposta para uma notificação (ORM → response)."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    analysis_id: str
    title: str
    message: str
    is_read: bool
    link: str
    created_at: datetime

    @field_validator("id", "analysis_id", mode="before")
    @classmethod
    def coerce_uuid_to_str(cls, v):
        """ORM retorna UUID; resposta exige str."""
        return str(v) if v is not None else v


class NotificationUnreadResponse(BaseModel):
    """Response para lista de notificações não lidas."""

    unread_count: int = Field(..., description="Número de não lidas")
    notifications: list[NotificationResponse] = Field(
        default_factory=list,
        description="Lista de notificações não lidas",
    )

    @field_validator("notifications", mode="before")
    @classmethod
    def orm_list_to_responses(cls, v):
        """Aceita lista de ORM e converte para list[NotificationResponse]."""
        if not v:
            return []
        return [NotificationResponse.model_validate(x) for x in v]
