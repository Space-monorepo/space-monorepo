import uuid
from unittest.mock import MagicMock

import pytest
from app.api.notifications.model import Notification, NotificationTypeEnum
from app.api.notifications.service import NotificationService
from app.api.users.model import User

# --- TESTES DE FORMATAÇÃO DE MENSAGEM ---

@pytest.mark.unit
@pytest.mark.parametrize("notif_type, data, expected_partial", [
    # 1. INTERAÇÃO
    (NotificationTypeEnum.INTERACTION, 
     {"interaction_type": "like", "actor_name": "João", "post_title": "Meu Post"},
     "João curtiu Meu Post."),
    
    # 2. CONEXÃO
    (NotificationTypeEnum.CONNECTION, 
     {"connection_type": "follow_request", "actor_name": "Maria"},
     "Maria quer te seguir."),

    # 3. CAMPANHA - NOVA (Default)
    (NotificationTypeEnum.CAMPAIGN, 
     {"community_name": "Devs", "campaign_title": "Hackathon", "campaign_status_type": "default"},
     'Nova campanha em Devs: Hackathon'),

    # 4. CAMPANHA - APROVADA
    (NotificationTypeEnum.CAMPAIGN, 
     {"community_name": "Devs", "campaign_title": "Hackathon", "campaign_status_type": "approved"},
     'Sua campanha "Hackathon" foi aprovada!'),

    # 5. CAMPANHA - REJEITADA
    (NotificationTypeEnum.CAMPAIGN, 
     {"community_name": "Devs", "campaign_title": "Hackathon", "campaign_status_type": "rejected"},
     'Sua campanha "Hackathon" não foi aprovada.'),

    # 6. CAMPANHA - FINALIZADA
    (NotificationTypeEnum.CAMPAIGN, 
     {"community_name": "Devs", "campaign_title": "Hackathon", "campaign_status_type": "finished"},
     'A campanha "Hackathon" foi finalizada.'),

    # 7. CAMPANHA - CANCELADA
    (NotificationTypeEnum.CAMPAIGN, 
     {"community_name": "Devs", "campaign_title": "Hackathon", "campaign_status_type": "canceled"},
     'A campanha "Hackathon" foi cancelada.'),

    # 8. CAMPANHA - META ATINGIDA
    (NotificationTypeEnum.CAMPAIGN, 
     {"community_name": "Devs", "campaign_title": "Hackathon", "campaign_status_type": "target_reached"},
     'A campanha "Hackathon" atingiu a meta!'),

    # 9. AVISO OFICIAL
    (NotificationTypeEnum.OFFICIAL_NOTICE, 
     {"notice_title": "Regras Novas", "community_name": "Space Geral"}, 
     "Aviso do Space: Regras Novas"),

    # 10. CASO DE ERRO/DEFAULT
    ("INVALID_TYPE", {}, "Você tem uma nova notificação."),
])
def test_format_notification_message(notification_service: NotificationService, notif_type: NotificationTypeEnum,
                                     data: dict, expected_partial: str):
    """
    Testa se a mensagem formatada contém o trecho esperado para todos os cenários.
    """
    mock_notif = Notification(
        id=uuid.uuid4(),
        user_id="user_id_str",
        type=notif_type,
        read=False,
        data=data
    )
    
    message = notification_service._format_notification_message(mock_notif)
    # Verificamos se a frase esperada está contida na mensagem gerada
    assert expected_partial in message

# --- TESTES DE UNREAD COUNT ---

@pytest.mark.unit
def test_get_unread_count(notification_service: NotificationService, mock_tm: MagicMock, mock_user: User):
    """
    Testa se o serviço chama o repositório corretamente para contar não lidas.
    """
    mock_repo = mock_tm.get_notification_repository()
    # Simula que o repositório retornou 5
    mock_repo.count_unread.return_value = 5

    result = notification_service.get_unread_count(user=mock_user)

    assert result == {'count': 5}
    mock_repo.count_unread.assert_called_once_with(user_id=mock_user.id)

# --- TESTES GERAIS (CRUD) ---

@pytest.mark.unit
def test_create_notification(notification_service: NotificationService, mock_tm: MagicMock, mock_user: User):
    mock_repo = mock_tm.get_notification_repository()
    expected_user_id_str = str(mock_user.id)

    notification_service.create_notification(
        user_id=mock_user.id,
        type=NotificationTypeEnum.OFFICIAL_NOTICE,
        data={"title": "Teste"}
    )
    
    # Verifica se converteu user_id para string antes de chamar o repo
    mock_repo.create.assert_called_once()
    call_args = mock_repo.create.call_args[1]['obj_in']
    assert call_args['user_id'] == expected_user_id_str