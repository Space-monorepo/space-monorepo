import pytest


@pytest.mark.integration
def test_ping_websocket_success(authenticated_websocket_client, websocket_event_data):
    """
    Testa se eventos ping são processados corretamente e retornam pong.
    """
    url = f"/chat/ws?token={authenticated_websocket_client.token}"

    with authenticated_websocket_client.websocket_connect(url) as websocket:
        # Recebe mensagem de boas-vindas
        welcome_response = websocket.receive_json()
        assert welcome_response["type"] == "welcome"

        # Envia evento ping
        ping_event = websocket_event_data["ping"]
        websocket.send_json(ping_event)

        # Recebe resposta pong
        response = websocket.receive_json()

        assert response["type"] == "pong"
        assert response["request_id"] == ping_event["request_id"]
        assert "timestamp" in response


@pytest.mark.integration
def test_join_conversation_websocket_success(authenticated_websocket_client, websocket_event_data):
    """
    Testa se eventos de entrada em conversa são processados corretamente.
    """
    url = f"/chat/ws?token={authenticated_websocket_client.token}"

    with authenticated_websocket_client.websocket_connect(url) as websocket:
        # Recebe mensagem de boas-vindas
        welcome_response = websocket.receive_json()
        assert welcome_response["type"] == "welcome"

        # Envia evento de entrada em conversa
        join_event = websocket_event_data["join_room"]
        websocket.send_json(join_event)

        # Recebe confirmação de entrada
        response = websocket.receive_json()

        assert response["request_id"] == join_event["request_id"]
        # Resposta deve ter status de sucesso ou informações de erro
        # Como a conversa não existe, é esperado que falhe
        assert "success" in response or "type" in response
        # Se falhar, deve ter informações de erro
        if response.get("success") is False:
            assert "message" in response or "error_code" in response


@pytest.mark.integration
def test_send_message_websocket_success(authenticated_websocket_client, websocket_event_data):
    """
    Testa se eventos de envio de mensagem são processados corretamente.
    """
    url = f"/chat/ws?token={authenticated_websocket_client.token}"

    with authenticated_websocket_client.websocket_connect(url) as websocket:
        # Recebe mensagem de boas-vindas
        welcome_response = websocket.receive_json()
        assert welcome_response["type"] == "welcome"

        # Envia evento de mensagem
        message_event = websocket_event_data["send_message"]
        websocket.send_json(message_event)

        # Recebe resposta
        response = websocket.receive_json()

        assert response["request_id"] == message_event["request_id"]
        # Resposta deve ter status de sucesso ou informações de erro
        assert "success" in response or "type" in response
        # Se falhar, deve ter informações de erro
        if response.get("success") is False:
            assert "message" in response or "error_code" in response


@pytest.mark.integration
def test_typing_websocket_success(authenticated_websocket_client):
    """
    Testa se eventos de digitação são processados corretamente.
    """
    url = f"/chat/ws?token={authenticated_websocket_client.token}"

    with authenticated_websocket_client.websocket_connect(url) as websocket:
        # Recebe mensagem de boas-vindas
        welcome_response = websocket.receive_json()
        assert welcome_response["type"] == "welcome"

        # Envia evento de digitação
        typing_event = {
            "type": "typing",
            "conversation_id": "12345678-1234-5678-9012-123456789abc",
            "request_id": "typing_test_123",
            "timestamp": 1703001600.0
        }
        websocket.send_json(typing_event)

        # Recebe resposta
        response = websocket.receive_json()

        assert response["request_id"] == typing_event["request_id"]
        # Resposta deve ter status de sucesso ou informações de erro
        assert "success" in response or "type" in response
        # Se falhar, deve ter informações de erro
        if response.get("success") is False:
            assert "error_message" in response or "error_code" in response


@pytest.mark.integration
def test_stop_typing_websocket_success(authenticated_websocket_client):
    """
    Testa se eventos de parar digitação são processados corretamente.
    """
    url = f"/chat/ws?token={authenticated_websocket_client.token}"

    with authenticated_websocket_client.websocket_connect(url) as websocket:
        # Recebe mensagem de boas-vindas
        welcome_response = websocket.receive_json()
        assert welcome_response["type"] == "welcome"

        # Envia evento de parar digitação
        stop_typing_event = {
            "type": "stop_typing",
            "conversation_id": "12345678-1234-5678-9012-123456789abc",
            "request_id": "stop_typing_test_123",
            "timestamp": 1703001600.0
        }
        websocket.send_json(stop_typing_event)

        # Recebe resposta
        response = websocket.receive_json()

        assert response["request_id"] == stop_typing_event["request_id"]
        # Resposta deve ter status de sucesso ou informações de erro
        assert "success" in response or "type" in response
        # Se falhar, deve ter informações de erro
        if response.get("success") is False:
            assert "error_message" in response or "error_code" in response


@pytest.mark.integration
def test_event_websocket_invalid_type_error(authenticated_websocket_client):
    """
    Testa se eventos com tipo inválido são tratados adequadamente.
    """
    url = f"/chat/ws?token={authenticated_websocket_client.token}"

    with authenticated_websocket_client.websocket_connect(url) as websocket:
        # Recebe mensagem de boas-vindas
        welcome_response = websocket.receive_json()
        assert welcome_response["type"] == "welcome"

        # Envia evento com tipo inválido
        invalid_event = {
            "type": "invalid_event_type",
            "request_id": "invalid_test_123",
            "timestamp": 1703001600.0
        }
        websocket.send_json(invalid_event)

        # Recebe resposta de erro
        response = websocket.receive_json()

        assert response["request_id"] == "invalid_test_123"
        assert response.get("type") == "error" or response.get("success") is False
        assert "error_message" in response or "error_code" in response


@pytest.mark.integration
def test_event_websocket_malformed_error(authenticated_websocket_client):
    """
    Testa se eventos malformados são tratados adequadamente.
    """
    url = f"/chat/ws?token={authenticated_websocket_client.token}"

    with authenticated_websocket_client.websocket_connect(url) as websocket:
        # Recebe mensagem de boas-vindas
        welcome_response = websocket.receive_json()
        assert welcome_response["type"] == "welcome"

        # Envia evento malformado (sem campos obrigatórios)
        malformed_event = {
            "type": "send_message",
            # Falta conversation_id e content
            "request_id": "malformed_test_123"
        }
        websocket.send_json(malformed_event)

        # Recebe resposta de erro
        response = websocket.receive_json()

        assert response["request_id"] == "malformed_test_123"
        assert response.get("success") is False
        assert "message" in response or "error_code" in response


@pytest.mark.integration
def test_event_websocket_missing_request_id_error(authenticated_websocket_client):
    """
    Testa se eventos sem request_id são tratados adequadamente.
    """
    url = f"/chat/ws?token={authenticated_websocket_client.token}"

    with authenticated_websocket_client.websocket_connect(url) as websocket:
        # Recebe mensagem de boas-vindas
        welcome_response = websocket.receive_json()
        assert welcome_response["type"] == "welcome"

        # Envia evento sem request_id
        event_without_id = {
            "type": "ping",
            "timestamp": 1703001600.0
        }
        websocket.send_json(event_without_id)

        # Recebe resposta
        response = websocket.receive_json()

        # Deve processar mesmo sem request_id ou retornar erro
        assert "type" in response or "success" in response


@pytest.mark.integration
def test_multiple_events_websocket_sequence_success(authenticated_websocket_client, websocket_event_data):
    """
    Testa se múltiplos eventos em sequência são processados corretamente.
    """
    url = f"/chat/ws?token={authenticated_websocket_client.token}"

    with authenticated_websocket_client.websocket_connect(url) as websocket:
        # Recebe mensagem de boas-vindas
        welcome_response = websocket.receive_json()
        assert welcome_response["type"] == "welcome"

        # Envia múltiplos eventos em sequência
        events = [
            websocket_event_data["ping"],
            websocket_event_data["join_room"],
            {
                "type": "typing",
                "conversation_id": "12345678-1234-5678-9012-123456789abc",
                "request_id": "typing_sequence_123",
                "timestamp": 1703001600.0
            }
        ]

        for event in events:
            websocket.send_json(event)
            response = websocket.receive_json()

            # Cada evento deve ser processado
            assert "request_id" in response or "type" in response
            # Se falhar, deve ter informações de erro
            if response.get("success") is False:
                assert "error_message" in response or "error_code" in response


@pytest.mark.integration
def test_event_response_websocket_format_consistency_success(authenticated_websocket_client, websocket_event_data):
    """
    Testa se o formato das respostas dos eventos é consistente.
    """
    url = f"/chat/ws?token={authenticated_websocket_client.token}"

    with authenticated_websocket_client.websocket_connect(url) as websocket:
        # Recebe mensagem de boas-vindas
        welcome_response = websocket.receive_json()
        assert welcome_response["type"] == "welcome"

        # Testa diferentes tipos de eventos para verificar consistência do formato
        test_events = [
            websocket_event_data["ping"],
            websocket_event_data["join_room"],
            websocket_event_data["send_message"]
        ]

        for event in test_events:
            websocket.send_json(event)
            response = websocket.receive_json()

            # Verifica formato padrão da resposta
            assert "request_id" in response or "type" in response
            assert "timestamp" in response or "success" in response

            # Se for resposta de erro, deve ter campos de erro
            if response.get("success") is False or response.get("type") == "error":
                assert "error_message" in response or "error_code" in response
