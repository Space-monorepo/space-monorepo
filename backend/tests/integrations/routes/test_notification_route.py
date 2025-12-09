import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.api.notifications.model import Notification, NotificationTypeEnum
from app.api.users.model import User

@pytest.mark.integration
def test_get_notifications_unauthenticated(client_sql: TestClient):
    response = client_sql.get("/notifications/")
    assert response.status_code == 401

@pytest.mark.integration
def test_get_notifications_empty(authenticate_client: TestClient):
    response = authenticate_client.get("/notifications/")
    assert response.status_code == 200
    assert response.json() == []

@pytest.mark.integration
def test_get_notifications_with_data(
    authenticate_client: TestClient, test_notification: Notification
):
    response = authenticate_client.get("/notifications/")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == str(test_notification.id)
    assert data[0]["read"] is False

@pytest.mark.integration
def test_mark_one_notification_as_read(
    authenticate_client: TestClient,
    test_notification: Notification,
    session_sql: Session,
):
    response = authenticate_client.post(
        f"/notifications/{test_notification.id}/read"
    )
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == str(test_notification.id)
    assert data["read"] is True

    session_sql.refresh(test_notification)
    assert test_notification.read is True

@pytest.mark.integration
def test_mark_one_notification_as_read_not_found(
    authenticate_client: TestClient,
):
    random_id = uuid.uuid4()
    response = authenticate_client.post(f"/notifications/{random_id}/read")
    assert response.status_code == 404

@pytest.mark.integration
def test_mark_all_notifications_as_read(
    authenticate_client: TestClient,
    test_notification: Notification,
    test_notification_campaign: Notification,
    session_sql: Session,
):
    assert test_notification.read is False
    assert test_notification_campaign.read is False

    response = authenticate_client.post("/notifications/read-all")
    assert response.status_code == 200

    session_sql.refresh(test_notification)
    session_sql.refresh(test_notification_campaign)
    assert test_notification.read is True
    assert test_notification_campaign.read is True

# --- NOVOS TESTES ---

@pytest.mark.integration
def test_get_unread_count(
    authenticate_client: TestClient,
    test_notification: Notification,          # read=False
    test_notification_campaign: Notification,  # read=False
    test_notification_canceled: Notification,  # read=True (definido no conftest)
    test_notification_official: Notification,  # read=False
):
    """
    Testa se a rota retorna a contagem correta (apenas read=False).
    """
    response = authenticate_client.get("/notifications/unread-count")
    assert response.status_code == 200
    
    data = response.json()
    assert "count" in data
    # Deve contar apenas as que têm read=False:
    # 1. test_notification (Interação)
    # 2. test_notification_campaign (Campanha Aprovada)
    # 3. test_notification_official (Aviso Oficial)
    # A cancelada (test_notification_canceled) é True, não conta.
    assert data["count"] == 3

@pytest.mark.integration
def test_filter_notifications_by_type(
    authenticate_client: TestClient,
    test_notification_campaign: Notification,
    test_notification_official: Notification
):
    """
    Testa se o filtro ?type=... funciona na rota de listagem.
    """
    # 1. Filtrar por OFFICIAL_NOTICE
    response = authenticate_client.get(f"/notifications/?type={NotificationTypeEnum.OFFICIAL_NOTICE.value}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]['type'] == NotificationTypeEnum.OFFICIAL_NOTICE
    
    # 2. Filtrar por CAMPAIGN
    response = authenticate_client.get(f"/notifications/?type={NotificationTypeEnum.CAMPAIGN.value}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]['type'] == NotificationTypeEnum.CAMPAIGN