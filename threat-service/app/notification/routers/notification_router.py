"""Notification router — rotas mínimas, delega para controller."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.notification.controllers.notification_controller import NotificationController
from app.notification.schemas import NotificationUnreadResponse

router = APIRouter(prefix="/notifications", tags=["Notifications"])


def get_controller(db: Annotated[Session, Depends(get_db)]) -> NotificationController:
    return NotificationController(db)


@router.get(
    "/unread",
    response_model=NotificationUnreadResponse,
    summary="Get unread notifications",
)
async def get_unread_notifications(
    limit: int = 20,
    controller: Annotated[NotificationController, Depends(get_controller)] = None,
):
    """Get list of unread notifications."""
    return controller.get_unread(limit=limit)


@router.post(
    "/{notification_id}/read",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Mark notification as read",
)
async def mark_notification_read(
    notification_id: uuid.UUID,
    controller: Annotated[NotificationController, Depends(get_controller)] = None,
):
    """Mark a notification as read."""
    ok = controller.mark_read(notification_id)
    if not ok:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )
