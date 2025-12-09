import uuid
from datetime import datetime

import pytest
from pydantic import ValidationError

from app.api.notifications.model import Notification, NotificationTypeEnum
from app.api.notifications.schema import (
    NotificationBase,
    NotificationRead,
    NotificationCount,
)

@pytest.mark.unit
def test_notification_base_schema():
    data = {
        "type": NotificationTypeEnum.INTERACTION,
        "data": {"actor_name": "Test User"},
    }
    schema = NotificationBase(**data)
    assert schema.type == NotificationTypeEnum.INTERACTION
    assert schema.data == {"actor_name": "Test User"}

@pytest.mark.unit
def test_notification_read_schema():
    notif_id = uuid.uuid4()
    now = datetime.now()
    data = {
        "id": notif_id,
        "type": NotificationTypeEnum.CAMPAIGN,
        "read": False,
        "created_at": now,
        "data": {"campaign_title": "Nova Campanha"},
        "message": "Nova campanha!",
    }

    schema = NotificationRead(**data)
    assert schema.id == notif_id
    assert schema.read is False
    assert schema.message == "Nova campanha!"

@pytest.mark.unit
def test_notification_count_schema():
    """Testa o novo schema de contagem."""
    data = {"count": 10}
    schema = NotificationCount(**data)
    assert schema.count == 10

    with pytest.raises(ValidationError):
        NotificationCount(count="texto") # Deve falhar se não for int