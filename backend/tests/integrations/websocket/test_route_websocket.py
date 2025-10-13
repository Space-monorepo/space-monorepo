import pytest
from fastapi import status
from fastapi.websockets import WebSocketDisconnect


@pytest.mark.integration
def test_connection_websocket_success(authenticated_websocket_client):
    """
    Testa se a conexão WebSocket é estabelecida com sucesso quando autenticado.
    """
    url = f'/chat/ws?token={authenticated_websocket_client.token}'

    with authenticated_websocket_client.websocket_connect(url) as websocket:
        assert websocket is not None


@pytest.mark.integration
def test_connection_websocket_without_token_error(websocket_client):
    """
    Testa se a conexão WebSocket é rejeitada quando não há token de autenticação.
    """
    with pytest.raises(WebSocketDisconnect) as exc_info:
        with websocket_client.websocket_connect('/chat/ws'):
            pass

    assert exc_info.value.code == status.WS_1008_POLICY_VIOLATION


@pytest.mark.integration
def test_connection_websocket_invalid_token_error(websocket_client):
    """
    Testa se a conexão WebSocket é rejeitada com token inválido.
    """
    with pytest.raises(WebSocketDisconnect) as exc_info:
        with websocket_client.websocket_connect('/chat/ws?token=invalid_token'):
            pass

    assert exc_info.value.code == status.WS_1008_POLICY_VIOLATION


@pytest.mark.integration
def test_welcome_message_websocket_success(authenticated_websocket_client):
    """
    Testa se a mensagem de boas-vindas é enviada após conexão estabelecida.
    """
    url = f'/chat/ws?token={authenticated_websocket_client.token}'

    with authenticated_websocket_client.websocket_connect(url) as websocket:
        welcome_response = websocket.receive_json()

        assert welcome_response['type'] == 'welcome'


@pytest.mark.integration
def test_ping_pong_websocket_success(authenticated_websocket_client):
    """
    Testa se o sistema responde corretamente a eventos ping com pong.
    """
    url = f'/chat/ws?token={authenticated_websocket_client.token}'

    with authenticated_websocket_client.websocket_connect(url) as websocket:
        # Recebe mensagem de boas-vindas
        welcome_response = websocket.receive_json()
        assert welcome_response['type'] == 'welcome'

        # Envia ping
        ping_event = {
            'type': 'ping',
            'request_id': 'test_ping_123',
            'timestamp': 1703001600.0,
        }
        websocket.send_json(ping_event)

        # Recebe pong
        response = websocket.receive_json()
        assert response['type'] == 'pong'
        assert response['request_id'] == 'test_ping_123'


@pytest.mark.integration
def test_send_message_websocket_success(authenticated_websocket_client, sample_conversation_id):
    """
    Testa se mensagens são enviadas corretamente através do WebSocket.
    """
    url = f'/chat/ws?token={authenticated_websocket_client.token}'

    with authenticated_websocket_client.websocket_connect(url) as websocket:
        # Recebe mensagem de boas-vindas
        welcome_response = websocket.receive_json()
        assert welcome_response['type'] == 'welcome'

        # Envia mensagem
        message_event = {
            'type': 'send_message',
            'conversation_id': str(sample_conversation_id),
            'content': 'Test message content',
            'request_id': 'test_msg_123',
            'timestamp': 1703001600.0,
        }
        websocket.send_json(message_event)

        # Verifica resposta
        response = websocket.receive_json()
        assert response['request_id'] == 'test_msg_123'
        assert response.get('success') is True or response.get('type') == 'message_sent'


@pytest.mark.integration
def test_join_conversation_websocket_success(authenticated_websocket_client, sample_conversation_id):
    """
    Testa se é possível entrar em uma conversa através do WebSocket.
    """
    url = f'/chat/ws?token={authenticated_websocket_client.token}'

    with authenticated_websocket_client.websocket_connect(url) as websocket:
        # Recebe mensagem de boas-vindas
        welcome_response = websocket.receive_json()
        assert welcome_response['type'] == 'welcome'

        # Entra na conversa
        join_event = {
            'type': 'join_conversation',
            'conversation_id': str(sample_conversation_id),
            'request_id': 'test_join_123',
            'timestamp': 1703001600.0,
        }
        websocket.send_json(join_event)

        # Verifica resposta
        response = websocket.receive_json()
        assert response['request_id'] == 'test_join_123'
        assert (
            response.get('success') is True
            or response.get('type') == 'conversation_joined'
        )


@pytest.mark.integration
def test_event_websocket_invalid_type_error(authenticated_websocket_client):
    """
    Testa se eventos com tipo inválido são tratados adequadamente.
    """
    url = f'/chat/ws?token={authenticated_websocket_client.token}'

    with authenticated_websocket_client.websocket_connect(url) as websocket:
        # Recebe mensagem de boas-vindas
        welcome_response = websocket.receive_json()
        assert welcome_response['type'] == 'welcome'

        # Envia evento inválido
        invalid_event = {'type': 'invalid_event_type', 'request_id': 'test_invalid_123'}
        websocket.send_json(invalid_event)

        # Verifica resposta de erro
        response = websocket.receive_json()
        assert response['request_id'] == 'test_invalid_123'
        assert response.get('type') == 'error'
        assert response.get('success') is False or response.get('type') == 'error'


@pytest.mark.integration
def test_health_endpoint_websocket_success(client_sql):
    """
    Testa se o endpoint de saúde do WebSocket retorna informações corretas.
    """
    response = client_sql.get('/chat/ws/health')

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data['status'] == 'healthy'
    assert data['service'] == 'chat_websocket'
    assert 'chat_connections' in data
    assert 'total_connections' in data
    assert 'supported_events' in data


@pytest.mark.integration
def test_stats_endpoint_websocket_success(client_sql):
    """
    Testa se o endpoint de estatísticas do WebSocket retorna dados válidos.
    """
    response = client_sql.get('/chat/ws/stats')

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    # Deve retornar estatísticas ou erro, mas não deve falhar
    if 'error' not in data:
        assert 'general' in data
        assert 'chat' in data
        assert 'timestamp' in data
