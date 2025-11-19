import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.api.notifications.model import Notification
from app.api.users.model import User

@pytest.mark.integration
def test_get_notifications_unauthenticated(client_sql: TestClient):
    """
    Testa se um usuário não autenticado recebe 401.
    (Usa 'client_sql' que é o cliente não autenticado)
    """
    response = client_sql.get("/notifications/")
    assert response.status_code == 401

@pytest.mark.integration
def test_get_notifications_empty(authenticate_client: TestClient):
    """
    Testa se um usuário autenticado sem notificações recebe uma lista vazia.
    """
    response = authenticate_client.get("/notifications/")
    assert response.status_code == 200
    assert response.json() == []

@pytest.mark.integration
def test_get_notifications_with_data(
    authenticate_client: TestClient, test_notification: Notification
):
    """
    Testa se o endpoint retorna a notificação criada pela fixture.
    """
    response = authenticate_client.get("/notifications/")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == str(test_notification.id)
    assert data[0]["read"] is False
    assert data[0]["type"] == "INTERACTION"
    assert data[0]["message"] == "Test Actor curtiu seu post de teste."

@pytest.mark.integration
def test_get_notifications_with_type_filter(
    authenticate_client: TestClient,
    test_notification: Notification,
    test_notification_campaign: Notification,
):
    """
    Testa se o filtro de 'type' na query string funciona.
    """
    response_all = authenticate_client.get("/notifications/")
    assert response_all.status_code == 200
    assert len(response_all.json()) == 2

    response_filtered = authenticate_client.get("/notifications/?type=INTERACTION")
    assert response_filtered.status_code == 200

    data_filtered = response_filtered.json()
    assert len(data_filtered) == 1
    assert data_filtered[0]["id"] == str(test_notification.id)
    assert data_filtered[0]["type"] == "INTERACTION"

@pytest.mark.integration
def test_mark_one_notification_as_read(
    authenticate_client: TestClient,
    test_notification: Notification,
    session_sql: Session,
):
    """
    Testa se o endpoint para marcar uma notificação como lida funciona.
    """
    assert test_notification.read is False

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
    """
    Testa se marcar uma notificação inexistente retorna 404.
    """
    random_id = uuid.uuid4()
    response = authenticate_client.post(f"/notifications/{random_id}/read")
    assert response.status_code == 404
    assert "Notification not found" in response.json()["detail"]

@pytest.mark.integration
def test_mark_all_notifications_as_read(
    authenticate_client: TestClient,
    test_notification: Notification,
    test_notification_campaign: Notification,
    session_sql: Session,
):
    """
    Testa se o endpoint para marcar todas as notificações como lidas funciona.
    """
    assert test_notification.read is False
    assert test_notification_campaign.read is False

    response = authenticate_client.post("/notifications/read-all")
    assert response.status_code == 200

    assert response.json() == {"message": "2 notificações marcadas como lidas."}

    session_sql.refresh(test_notification)
    session_sql.refresh(test_notification_campaign)
    assert test_notification.read is True
    assert test_notification_campaign.read is True