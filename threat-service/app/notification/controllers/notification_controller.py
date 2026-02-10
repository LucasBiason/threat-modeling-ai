"""Notification controller — orquestração."""

from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from app.notification.repositories.notification_repository import NotificationRepository
from app.notification.schemas import NotificationUnreadResponse


class NotificationController:
    """Controller para operações de notification."""

    def __init__(self, db: Session) -> None:
        self._repository = NotificationRepository(db)

    def get_unread(self, limit: int = 20) -> NotificationUnreadResponse:
        """Retorna lista de notifications não lidas."""
        notifications = self._repository.list_unread(limit=limit)
        return NotificationUnreadResponse(
            unread_count=len(notifications),
            notifications=notifications,
        )

    def mark_read(self, notification_id: uuid.UUID) -> bool:
        """Marca notification como lida."""
        return self._repository.mark_read(notification_id)
