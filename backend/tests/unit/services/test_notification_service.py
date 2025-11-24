import uuid
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from app.api.notifications.model import Notification, NotificationTypeEnum
from app.api.notifications.service import NotificationService
from app.api.users.model import User


# As fixtures (notification_service, mock_tm, mock_user, mock_actor)
# são carregadas automaticamente do conftest.py

@pytest.mark.unit
def test_create_notification(notification_service: NotificationService, mock_tm: MagicMock, mock_user: User):
    """
    Testa a criação de uma notificação genérica.
    """
    mock_repo = mock_tm.get_notification_repository()

    expected_user_id_str = str(mock_user.id)

    notif_data = {
        "user_id": expected_user_id_str,
        "type": NotificationTypeEnum.OFFICIAL_NOTICE,
        "data": {"title": "Teste"}
    }

    mock_repo.create.return_value = Notification(
        user_id=expected_user_id_str,
        type=NotificationTypeEnum.OFFICIAL_NOTICE,
        data={"title": "Teste"}
    )

    notification_service.create_notification(
        user_id=mock_user.id,
        type=NotificationTypeEnum.OFFICIAL_NOTICE,
        data={"title": "Teste"}
    )

    mock_repo.create.assert_called_once_with(obj_in=notif_data)


@pytest.mark.unit
def test_create_interaction_notification_like(notification_service: NotificationService, mock_user: User,
                                              mock_actor: User):
    """
    Testa o wrapper de criação de notificação de 'like'.
    """
    with patch.object(notification_service, 'create_notification') as mock_create:
        notification_service.create_interaction_notification(
            recipient=mock_user,
            actor=mock_actor,
            interaction_type="like",
            post_title="Meu Post Incrível"
        )

        expected_data = {
            "interaction_type": "like",
            "actor_id": str(mock_actor.id),
            "actor_name": mock_actor.name,
            "post_title": "Meu Post Incrível"
        }

        mock_create.assert_called_once_with(
            user_id=mock_user.id,
            type=NotificationTypeEnum.INTERACTION,
            data=expected_data
        )


@pytest.mark.unit
def test_create_interaction_notification_comment(notification_service: NotificationService, mock_user: User,
                                                 mock_actor: User):
    """
    Testa o wrapper de criação de notificação de 'comment'.
    """
    with patch.object(notification_service, 'create_notification') as mock_create:
        notification_service.create_interaction_notification(
            recipient=mock_user,
            actor=mock_actor,
            interaction_type="comment",
            post_title="Meu Post",
            comment_content="Que post legal!"
        )

        expected_data = {
            "interaction_type": "comment",
            "actor_id": str(mock_actor.id),
            "actor_name": mock_actor.name,
            "post_title": "Meu Post",
            "comment_content": "Que post legal!"
        }

        mock_create.assert_called_once_with(
            user_id=mock_user.id,
            type=NotificationTypeEnum.INTERACTION,
            data=expected_data
        )


@pytest.mark.unit
def test_create_connection_notification_request_received(notification_service: NotificationService, mock_user: User,
                                                       mock_actor: User):
    """
    Testa o wrapper de criação de notificação de pedido de conexão recebido.
    """
    with patch.object(notification_service, 'create_notification') as mock_create:
        notification_service.create_connection_notification(
            recipient=mock_user,
            actor=mock_actor,
            connection_type="request_received"
        )

        expected_data = {
            "connection_type": "request_received",
            "actor_id": str(mock_actor.id),
            "actor_name": mock_actor.name
        }

        mock_create.assert_called_once_with(
            user_id=mock_user.id,
            type=NotificationTypeEnum.CONNECTION,
            data=expected_data
        )


@pytest.mark.unit
def test_create_connection_notification_request_accepted(notification_service: NotificationService, mock_user: User,
                                                        mock_actor: User):
    """
    Testa o wrapper de criação de notificação de aceitação de conexão.
    """
    with patch.object(notification_service, 'create_notification') as mock_create:
        notification_service.create_connection_notification(
            recipient=mock_user,
            actor=mock_actor,
            connection_type="request_accepted"
        )

        expected_data = {
            "connection_type": "request_accepted",
            "actor_id": str(mock_actor.id),
            "actor_name": mock_actor.name
        }

        mock_create.assert_called_once_with(
            user_id=mock_user.id,
            type=NotificationTypeEnum.CONNECTION,
            data=expected_data
        )


@pytest.mark.unit
def test_get_user_notifications(notification_service: NotificationService, mock_tm: MagicMock, mock_user: User):
    """
    Testa a listagem de notificações e a formatação da mensagem.
    """
    mock_repo = mock_tm.get_notification_repository()

    mock_notif_model = Notification(
        id=uuid.uuid4(),
        user_id=str(mock_user.id),  # User ID é str
        type=NotificationTypeEnum.INTERACTION,
        read=False,
        created_at=datetime.now(),
        data={
            "interaction_type": "like",
            "actor_name": "Usuário Ator",
            "post_title": "meu post"
        }
    )
    mock_repo.get_by_user_id.return_value = [mock_notif_model]

    notifications_read = notification_service.get_user_notifications(user=mock_user)

    mock_repo.get_by_user_id.assert_called_once_with(
        user_id=mock_user.id,
        notification_type=None
    )

    assert len(notifications_read) == 1
    assert notifications_read[0].id == mock_notif_model.id
    assert notifications_read[0].message == "Usuário Ator curtiu meu post."


@pytest.mark.unit
def test_mark_as_read(notification_service: NotificationService, mock_tm: MagicMock, mock_user: User):
    """
    Testa marcar uma notificação como lida.
    """
    mock_repo = mock_tm.get_notification_repository()
    notif_id = uuid.uuid4()

    mock_notif_model = Notification(
        id=notif_id,
        user_id=str(mock_user.id),  # User ID é str
        type=NotificationTypeEnum.CAMPAIGN,
        read=True,
        created_at=datetime.now(),
        data={"community_name": "Comunidade Teste", "campaign_title": "Participe!", "campaign_status_type": "default"}
    )
    mock_repo.mark_as_read.return_value = mock_notif_model

    result = notification_service.mark_as_read(
        notification_id=notif_id,
        user=mock_user
    )

    mock_repo.mark_as_read.assert_called_once_with(
        notification_id=notif_id,
        user_id=mock_user.id
    )

    assert result.read is True
    assert result.message == "Nova campanha em Comunidade Teste: Participe!"


@pytest.mark.unit
def test_mark_all_as_read(notification_service: NotificationService, mock_tm: MagicMock, mock_user: User):
    """
    Testa marcar todas as notificações como lidas.
    """
    mock_repo = mock_tm.get_notification_repository()

    mock_repo.mark_all_as_read.return_value = 3

    result = notification_service.mark_all_as_read(user=mock_user)

    mock_repo.mark_all_as_read.assert_called_once_with(user_id=mock_user.id)

    assert result == {"message": "3 notificações marcadas como lidas."}


@pytest.mark.unit
@pytest.mark.parametrize("notif_type, data, expected_message", [
    # INTERAÇÕES
    (NotificationTypeEnum.INTERACTION, 
     {"interaction_type": "like", "actor_name": "Bob", "post_title": "seu post"},
     "Bob curtiu seu post."),
    (NotificationTypeEnum.INTERACTION,
     {"interaction_type": "comment", "actor_name": "Alice", "post_title": "sua foto", "comment_content": "Que legal!"},
     'Alice comentou em sua foto: "Que legal!"'),
    (NotificationTypeEnum.INTERACTION,
     {"interaction_type": "comment_like", "actor_name": "Carol", "comment_content": "Meu comentário"},
     'Carol curtiu seu comentário: "Meu comentário"'),

    # CONEXÕES (Novos formatos)
    (NotificationTypeEnum.CONNECTION,
     {"connection_type": "request_received", "actor_name": "David"},
     "David enviou um pedido de conexão."),
    (NotificationTypeEnum.CONNECTION,
     {"connection_type": "request_accepted", "actor_name": "Eve"},
     "Eve aceitou seu pedido de conexão."),
    (NotificationTypeEnum.CONNECTION,
     {"connection_type": "badge", "badge_name": "Super Star"},
     "Você recebeu um novo emblema: Super Star"),

    # CAMPANHAS (Todos os ciclos de vida)
    (NotificationTypeEnum.CAMPAIGN, 
     {"community_name": "Devs", "campaign_title": "Hackathon", "campaign_status_type": "default"},
     "Nova campanha em Devs: Hackathon"),
    
    (NotificationTypeEnum.CAMPAIGN, 
     {"community_name": "Devs", "campaign_title": "Hackathon", "campaign_status_type": "target_reached"},
     'A campanha "Hackathon" atingiu a meta! Agora está em análise.'),
    
    (NotificationTypeEnum.CAMPAIGN, 
     {"community_name": "Devs", "campaign_title": "Hackathon", "campaign_status_type": "in_progress"},
     'A campanha "Hackathon" entrou em progresso.'),

    (NotificationTypeEnum.CAMPAIGN, 
     {"community_name": "Devs", "campaign_title": "Hackathon", "campaign_status_type": "finished"},
     'A campanha "Hackathon" foi finalizada com sucesso!'),

    # APROVAÇÃO/REJEIÇÃO (Com e sem feedback)
    (NotificationTypeEnum.CAMPAIGN, 
     {"community_name": "Devs", "campaign_title": "Hackathon", "campaign_status_type": "approved"},
     'Boas notícias! A campanha "Hackathon" foi aprovada.'),
    
    (NotificationTypeEnum.CAMPAIGN, 
     {"community_name": "Devs", "campaign_title": "Hackathon", "campaign_status_type": "approved", "feedback_content": "Excelente iniciativa"},
     'Boas notícias! A campanha "Hackathon" foi aprovada: "Excelente iniciativa"'),

    (NotificationTypeEnum.CAMPAIGN, 
     {"community_name": "Devs", "campaign_title": "Hackathon", "campaign_status_type": "rejected"},
     'A campanha "Hackathon" não foi aprovada.'),

    (NotificationTypeEnum.CAMPAIGN, 
     {"community_name": "Devs", "campaign_title": "Hackathon", "campaign_status_type": "rejected", "feedback_content": "Fora do tema"},
     'A campanha "Hackathon" não foi aprovada: "Fora do tema"'),

    # OUTROS
    (NotificationTypeEnum.OFFICIAL_NOTICE, {"notice_title": "Manutenção"}, "Aviso: Manutenção"),
    ("INVALID_TYPE", {}, "Você tem uma nova notificação."),
])
def test_format_notification_message(notification_service: NotificationService, notif_type: NotificationTypeEnum,
                                     data: dict, expected_message: str):
    """
    Testa o helper '_format_notification_message' para todos os cenários, incluindo o ciclo de vida das campanhas.
    """
    mock_notif = Notification(
        id=uuid.uuid4(),
        user_id="user_uuid_as_string",
        type=notif_type,
        data=data,
        read=False,
        created_at=datetime.now()
    )

    message = notification_service._format_notification_message(mock_notif)
    assert message == expected_message