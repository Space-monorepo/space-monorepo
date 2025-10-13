import pytest
from fastapi import status
from fastapi.websockets import WebSocketDisconnect


@pytest.mark.integration
def test_connection_websocket_success(authenticated_websocket_client):
    """
    Testa se a conexão WebSocket é estabelecida com sucesso quando autenticado.
    """
    url = f"/chat/ws?token={authenticated_websocket_client.token}"

    with authenticated_websocket_client.websocket_connect(url) as websocket:
        assert websocket is not None


@pytest.mark.integration
def test_connection_websocket_authentication_error(websocket_client):
    """
    Testa se a conexão WebSocket é rejeitada quando não há autenticação.
    """
    with pytest.raises(WebSocketDisconnect) as exc_info:
        with websocket_client.websocket_connect("/chat/ws"):
            pass

    assert exc_info.value.code == status.WS_1008_POLICY_VIOLATION


@pytest.mark.integration
def test_connection_websocket_invalid_token_error(websocket_client):
    """
    Testa se a conexão WebSocket é rejeitada com token inválido.
    """
    with pytest.raises(WebSocketDisconnect) as exc_info:
        with websocket_client.websocket_connect("/chat/ws?token=invalid_token"):
            pass

    assert exc_info.value.code == status.WS_1008_POLICY_VIOLATION


@pytest.mark.integration
def test_connection_websocket_with_conversation_context_success(authenticated_websocket_client, sample_conversation_id):
    """
    Testa se a conexão WebSocket funciona com parâmetro de conversa.
    """
    url = f"/chat/ws?token={authenticated_websocket_client.token}&conversation_id={str(sample_conversation_id)}"

    with authenticated_websocket_client.websocket_connect(url) as websocket:
        assert websocket is not None


@pytest.mark.integration
def test_connection_websocket_lifecycle_success(authenticated_websocket_client):
    """
    Testa o ciclo completo de vida da conexão WebSocket.
    """
    url = f"/chat/ws?token={authenticated_websocket_client.token}"

    with authenticated_websocket_client.websocket_connect(url) as websocket:
        # Verifica se a conexão foi estabelecida
        assert websocket is not None

        # Recebe mensagem de boas-vindas
        welcome_response = websocket.receive_json()
        assert welcome_response["type"] == "welcome"

        # Testa ping/pong para verificar estabilidade da conexão
        ping_data = {
            "type": "ping",
            "request_id": "lifecycle_ping",
            "timestamp": 1703001600.0
        }

        websocket.send_json(ping_data)
        response = websocket.receive_json()

        # Deve receber resposta pong
        assert response["type"] == "pong"
        assert response["request_id"] == "lifecycle_ping"

    # A conexão deve fechar sem erros


@pytest.mark.integration
def test_connection_websocket_error_handling_success(authenticated_websocket_client):
    """
    Testa se a conexão WebSocket trata erros adequadamente.
    """
    url = f"/chat/ws?token={authenticated_websocket_client.token}"

    with authenticated_websocket_client.websocket_connect(url) as websocket:
        # Recebe mensagem de boas-vindas
        welcome_response = websocket.receive_json()
        assert welcome_response["type"] == "welcome"

        # Envia dados malformados para testar tratamento de erro
        try:
            websocket.send_text("invalid json data")

            # Se a conexão permanecer aberta, deve receber erro
            try:
                response = websocket.receive_json()
                if "type" in response:
                    assert response["type"] == "error"
            except WebSocketDisconnect:
                # A conexão pode fechar com dados malformados - isso é aceitável
                pass

        except WebSocketDisconnect as e:
            # A conexão pode fechar imediatamente com dados malformados
            assert e.code in [status.WS_1003_UNSUPPORTED_DATA, status.WS_1011_INTERNAL_ERROR]


@pytest.mark.integration
def test_connection_websocket_with_login_token_success(websocket_client, user_on_db):
    """
    Testa se a conexão WebSocket funciona com token obtido via login.
    """
    # Obtém token de autenticação
    response = websocket_client.post(
        '/users/login',
        data={'username': user_on_db.email, 'password': 'hashed_password'}
    )
    token = response.json().get('access_token')

    # Conecta com token na URL
    with websocket_client.websocket_connect(f"/chat/ws?token={token}") as websocket:
        assert websocket is not None


@pytest.mark.integration
def test_connection_websocket_multiple_cycles_success(authenticated_websocket_client):
    """
    Testa múltiplos ciclos de conexão/desconexão para verificar limpeza adequada.
    """
    url = f"/chat/ws?token={authenticated_websocket_client.token}"

    # Múltiplos ciclos de conexão para testar limpeza
    for i in range(3):
        with authenticated_websocket_client.websocket_connect(url) as websocket:
            # Recebe mensagem de boas-vindas
            welcome_response = websocket.receive_json()
            assert welcome_response["type"] == "welcome"

            # Operação básica para garantir que a conexão funciona
            ping_data = {
                "type": "ping",
                "request_id": f"cleanup_ping_{i}",
                "timestamp": 1703001600.0 + i
            }

            websocket.send_json(ping_data)
            response = websocket.receive_json()
            assert response["type"] == "pong"

        # Cada conexão deve fechar adequadamente
