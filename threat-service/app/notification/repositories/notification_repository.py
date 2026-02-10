"""Notification repository — encapsula chamadas ao ORM."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.notification.models import Notification


class NotificationRepository:
    """Repository para operações de Notification no banco."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def create(
        self,
        analysis_id: uuid.UUID,
        title: str,
        message: str,
        link: str,
    ) -> Notification:
        """Cria nova notification."""
        notification = Notification(
            analysis_id=analysis_id,
            title=title,
            message=message,
            link=link,
        )
        self._db.add(notification)
        self._db.commit()
        self._db.refresh(notification)
        return notification

    def get_by_id(self, notification_id: uuid.UUID) -> Notification | None:
        """Busca notification por ID."""
        return self._db.get(Notification, notification_id)

    def list_unread(self, limit: int = 20) -> list[Notification]:
        """Lista notifications não lidas."""
        result = self._db.execute(
            select(Notification)
            .where(Notification.is_read == False)  # noqa: E712
            .order_by(Notification.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    def mark_read(self, notification_id: uuid.UUID) -> bool:
        """Marca notification como lida. Retorna False se não existir."""
        notification = self._db.get(Notification, notification_id)
        if not notification:
            return False
        notification.is_read = True
        self._db.commit()
        return True
