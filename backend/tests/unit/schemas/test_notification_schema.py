import uuid
from datetime import datetime

import pytest
from pydantic import ValidationError

from app.api.notifications.model import Notification, NotificationTypeEnum
from app.api.notifications.schema import (
    NotificationBase,
    NotificationRead,
    NotificationMarkAllRead,
)


@pytest.mark.unit
def test_notification_base_schema():
    """
    Testa a criação bem-sucedida do schema NotificationBase.
    """
    # CORREÇÃO: NotificationBase só deve ter 'type' e 'data'
    data = {
        "type": NotificationTypeEnum.INTERACTION,
        "data": {"actor_name": "Test User"},
    }

    schema = NotificationBase(**data)

    assert schema.type == NotificationTypeEnum.INTERACTION
    assert schema.data == {"actor_name": "Test User"}
    # A linha 'assert schema.id' foi removida pois não pertence ao Base


@pytest.mark.unit
def test_notification_base_invalid_type():
    """
    Testa falha com um tipo de notificação inválido.
    """
    with pytest.raises(ValidationError):
        NotificationBase(type="INVALID_TYPE", data={})


@pytest.mark.unit
def test_notification_read_schema():
    """
    Testa a criação bem-sucedida do schema NotificationRead.
    """
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
def test_notification_schema_from_model():
    """
    Testa a criação do schema Read a partir de um objeto do modelo.
    """
    notif_id = uuid.uuid4()
    now = datetime.now()
    user_id = "user_uuid_as_string"  # Modelo User.id é as_uuid=False

    mock_model = Notification(
        id=notif_id,
        user_id=user_id,
        type=NotificationTypeEnum.INTERACTION,
        read=True,
        created_at=now,
        data={"interaction_type": "like", "actor_name": "Jane Doe"},
    )

    # CORREÇÃO: Validar contra NotificationRead, não NotificationBase
    schema_read = NotificationRead.model_validate(mock_model)

    assert schema_read.id == notif_id
    assert schema_read.read is True
    assert schema_read.type == NotificationTypeEnum.INTERACTION
    assert schema_read.data == {
        "interaction_type": "like",
        "actor_name": "Jane Doe",
    }


@pytest.mark.unit
def test_notification_mark_all_read_schema():
    """
    Testa o schema de resposta do 'read-all'.
    """
    data = {"message": "3 notificações marcadas como lidas."}
    schema = NotificationMarkAllRead(**data)
    assert schema.message == "3 notificações marcadas como lidas."