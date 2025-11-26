import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.notifications import schema
from app.api.notifications.model import NotificationTypeEnum
from app.api.notifications.service import NotificationService
from app.api.users.model import User
from app.auth.deps import get_current_user
from app.core.database import get_db
from app.core.transaction import TransactionManager

router = APIRouter(prefix='/notifications')


@router.get('/', response_model=List[schema.NotificationRead])
def get_user_notifications(
    type: NotificationTypeEnum | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    tm = TransactionManager(db)
    service = NotificationService(tm)
    return service.get_user_notifications(user=current_user, notification_type=type)


@router.get('/unread-count', response_model=schema.NotificationCount)
def get_unread_notifications_count(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    tm = TransactionManager(db)
    service = NotificationService(tm)
    return service.get_unread_count(user=current_user)


@router.post('/read-all', response_model=schema.NotificationMarkAllRead)
def mark_all_notifications_as_read(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    tm = TransactionManager(db)
    service = NotificationService(tm)
    return service.mark_all_as_read(user=current_user)


@router.post('/{notification_id}/read', response_model=schema.NotificationRead)
def mark_notification_as_read(
    notification_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    tm = TransactionManager(db)
    service = NotificationService(tm)
    notification = service.mark_as_read(
        notification_id=notification_id, user=current_user
    )

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Notification not found or you do not have permission to read it.',
        )
    return notification
