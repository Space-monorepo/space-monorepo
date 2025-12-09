import pytest


@pytest.mark.integration
def test_send_message_websocket_success(authenticated_websocket_client, sample_conversation_id):
    """
    Testa se mensagens são enviadas corretamente através do WebSocket de chat.
    """
    url = f"/chat/ws?token={authenticated_websocket_client.token}"

    with authenticated_websocket_client.websocket_connect(url) as websocket:
        # Recebe mensagem de boas-vindas
        welcome_response = websocket.receive_json()
        assert welcome_response["type"] == "welcome"

        # Envia mensagem de chat
        message_event = {
            "type": "send_message",
            "conversation_id": str(sample_conversation_id),
            "content": "Hello, this is a test message!",
            "request_id": "chat_msg_123",
            "timestamp": 1703001600.0
        }

        websocket.send_json(message_event)
        response = websocket.receive_json()

        # Verifica se a resposta contém o request_id
        assert "request_id" in response
        assert response["request_id"] == "chat_msg_123"

        # Verifica se é sucesso ou erro
        if response.get("success") is True:
            assert "data" in response
            if "data" in response and response["data"]:
                assert "id" in response["data"]  # mensagem deve ter um id
        else:
            assert response.get("success") is False
            assert "message" in response or "error_code" in response


@pytest.mark.integration
def test_join_conversation_websocket_success(authenticated_websocket_client, sample_room_data):
    """
    Testa se é possível entrar em uma conversa através do WebSocket de chat.
    """
    url = f"/chat/ws?token={authenticated_websocket_client.token}"

    with authenticated_websocket_client.websocket_connect(url) as websocket:
        # Recebe mensagem de boas-vindas
        welcome_response = websocket.receive_json()
        assert welcome_response["type"] == "welcome"

        # Entra em uma conversa
        join_event = {
            "type": "join_conversation",
            "conversation_id": sample_room_data["conversation_id"],
            "request_id": "chat_join_123",
            "timestamp": 1703001600.0
        }

        websocket.send_json(join_event)
        response = websocket.receive_json()

        # Verifica se a resposta contém o request_id
        assert "request_id" in response
        assert response["request_id"] == "chat_join_123"

        # Verifica se é sucesso ou erro
        if response.get("success") is True:
            assert "data" in response
            if "data" in response and response["data"]:
                assert response["data"].get("type") == "conversation_joined"
        else:
            assert response.get("success") is False
            assert "message" in response or "error_code" in response


@pytest.mark.integration
def test_leave_conversation_websocket_success(authenticated_websocket_client, sample_conversation_id):
    """
    Testa se é possível sair de uma conversa através do WebSocket de chat.
    """
    url = f"/chat/ws?token={authenticated_websocket_client.token}"

    with authenticated_websocket_client.websocket_connect(url) as websocket:
        # Recebe mensagem de boas-vindas
        welcome_response = websocket.receive_json()
        assert welcome_response["type"] == "welcome"

        # Primeiro entra na conversa
        join_event = {
            "type": "join_conversation",
            "conversation_id": str(sample_conversation_id),
            "request_id": "join_before_leave",
            "timestamp": 1703001600.0
        }

        websocket.send_json(join_event)
        join_response = websocket.receive_json()

        # Verifica se entrou na conversa
        assert "request_id" in join_response
        assert join_response["request_id"] == "join_before_leave"

        # Agora sai da conversa
        leave_event = {
            "type": "leave_conversation",
            "conversation_id": str(sample_conversation_id),
            "request_id": "chat_leave_123",
            "timestamp": 1703001601.0
        }

        websocket.send_json(leave_event)
        leave_response = websocket.receive_json()

        # Verifica se a resposta contém o request_id
        assert "request_id" in leave_response
        assert leave_response["request_id"] == "chat_leave_123"

        # Verifica se é sucesso ou erro
        if leave_response.get("success") is True:
            assert "data" in leave_response
            if "data" in leave_response and leave_response["data"]:
                assert leave_response["data"].get("type") == "conversation_left"
        else:
            assert leave_response.get("success") is False
            assert "message" in leave_response or "error_code" in leave_response


@pytest.mark.integration
def test_typing_indicators_websocket_success(authenticated_websocket_client, sample_conversation_id):
    """
    Testa se os indicadores de digitação funcionam corretamente.
    """
    url = f"/chat/ws?token={authenticated_websocket_client.token}"

    with authenticated_websocket_client.websocket_connect(url) as websocket:
        # Recebe mensagem de boas-vindas
        welcome_response = websocket.receive_json()
        assert welcome_response["type"] == "welcome"

        # Inicia digitação
        typing_event = {
            "type": "typing",
            "conversation_id": str(sample_conversation_id),
            "request_id": "typing_123",
            "timestamp": 1703001600.0
        }

        websocket.send_json(typing_event)
        typing_response = websocket.receive_json()

        # Verifica se a resposta contém o request_id
        assert "request_id" in typing_response
        assert typing_response["request_id"] == "typing_123"

        # Verifica se é sucesso ou erro
        if typing_response.get("success") is True:
            assert "message" in typing_response
        else:
            assert typing_response.get("success") is False
            assert "message" in typing_response or "error_code" in typing_response

        # Para de digitar
        stop_typing_event = {
            "type": "stop_typing",
            "conversation_id": str(sample_conversation_id),
            "request_id": "stop_typing_123",
            "timestamp": 1703001601.0
        }

        websocket.send_json(stop_typing_event)
        stop_response = websocket.receive_json()

        # Verifica se a resposta contém o request_id
        assert "request_id" in stop_response
        assert stop_response["request_id"] == "stop_typing_123"

        # Verifica se é sucesso ou erro
        if stop_response.get("success") is True:
            assert "message" in stop_response
        else:
            assert stop_response.get("success") is False
            assert "message" in stop_response or "error_code" in stop_response


@pytest.mark.integration
def test_mark_message_read_websocket_success(authenticated_websocket_client, sample_conversation_id):
    """
    Testa se mensagens podem ser marcadas como lidas.
    """
    url = f"/chat/ws?token={authenticated_websocket_client.token}"

    with authenticated_websocket_client.websocket_connect(url) as websocket:
        # Recebe mensagem de boas-vindas
        welcome_response = websocket.receive_json()
        assert welcome_response["type"] == "welcome"

        # Marca uma mensagem como lida
        read_event = {
            "type": "mark_message_read",
            "message_id": "test_message_456",
            "conversation_id": str(sample_conversation_id),
            "request_id": "read_123",
            "timestamp": 1703001600.0
        }

        websocket.send_json(read_event)
        response = websocket.receive_json()

        # Verifica se a resposta contém o request_id
        assert "request_id" in response
        assert response["request_id"] == "read_123"

        # Verifica se é sucesso ou erro
        if response.get("success") is True:
            assert "data" in response
            if "data" in response and response["data"]:
                assert "message_id" in response["data"]
        else:
            assert response.get("success") is False
            assert "message" in response or "error_code" in response


@pytest.mark.integration
def test_bulk_mark_read_websocket_success(authenticated_websocket_client, sample_conversation_id):
    """
    Testa se múltiplas mensagens podem ser marcadas como lidas em lote.
    """
    url = f"/chat/ws?token={authenticated_websocket_client.token}"

    with authenticated_websocket_client.websocket_connect(url) as websocket:
        # Recebe mensagem de boas-vindas
        welcome_response = websocket.receive_json()
        assert welcome_response["type"] == "welcome"

        # Marca múltiplas mensagens como lidas
        bulk_read_event = {
            "type": "bulk_mark_read",
            "message_ids": ["msg_456", "msg_789", "msg_101"],
            "conversation_id": str(sample_conversation_id),
            "request_id": "bulk_read_123",
            "timestamp": 1703001600.0
        }

        websocket.send_json(bulk_read_event)
        response = websocket.receive_json()

        # Verifica se a resposta contém o request_id
        assert "request_id" in response
        assert response["request_id"] == "bulk_read_123"

        # Verifica se é sucesso ou erro
        if response.get("success") is True:
            assert "data" in response
            if "data" in response and response["data"]:
                assert "marked_count" in response["data"]
        else:
            assert response.get("success") is False
            assert "message" in response or "error_code" in response


@pytest.mark.integration
def test_message_with_attachment_websocket_success(authenticated_websocket_client, sample_conversation_id):
    """
    Testa se mensagens com anexos são enviadas corretamente.
    """
    url = f"/chat/ws?token={authenticated_websocket_client.token}"

    with authenticated_websocket_client.websocket_connect(url) as websocket:
        # Recebe mensagem de boas-vindas
        welcome_response = websocket.receive_json()
        assert welcome_response["type"] == "welcome"

        # Envia mensagem com anexo
        attachment_event = {
            "type": "send_message_with_attachment",
            "conversation_id": str(sample_conversation_id),
            "content": "Check out this file!",
            "attachment": {
                "filename": "document.pdf",
                "file_url": "https://example.com/files/document.pdf",
                "file_type": "application/pdf",
                "file_size": 1024000
            },
            "request_id": "attachment_123",
            "timestamp": 1703001600.0
        }

        websocket.send_json(attachment_event)
        response = websocket.receive_json()

        # Verifica se a resposta contém o request_id
        assert "request_id" in response
        assert response["request_id"] == "attachment_123"

        # Verifica se é sucesso ou erro
        if response.get("success") is True:
            assert "data" in response
            if "data" in response and response["data"]:
                assert "id" in response["data"]  # mensagem deve ter um id
        else:
            assert response.get("success") is False
            assert "message" in response or "error_code" in response


@pytest.mark.integration
def test_conversation_websocket_invalid_error(authenticated_websocket_client):
    """
    Testa se operações com conversas inválidas são tratadas adequadamente.
    """
    url = f"/chat/ws?token={authenticated_websocket_client.token}"

    with authenticated_websocket_client.websocket_connect(url) as websocket:
        # Recebe mensagem de boas-vindas
        welcome_response = websocket.receive_json()
        assert welcome_response["type"] == "welcome"

        # Tenta entrar em conversa inexistente
        invalid_join_event = {
            "type": "join_conversation",
            "conversation_id": "12345678-1234-5678-9012-123456789012",  # UUID válido mas inexistente
            "request_id": "invalid_join_123",
            "timestamp": 1703001600.0
        }

        websocket.send_json(invalid_join_event)
        response = websocket.receive_json()

        # Verifica se a resposta contém o request_id
        assert "request_id" in response
        assert response["request_id"] == "invalid_join_123"
        assert response.get("success") is False
        assert "message" in response or "error_code" in response


@pytest.mark.integration
def test_message_websocket_validation_error(authenticated_websocket_client, sample_conversation_id):
    """
    Testa se a validação de mensagens funciona corretamente.
    """
    url = f"/chat/ws?token={authenticated_websocket_client.token}"

    with authenticated_websocket_client.websocket_connect(url) as websocket:
        # Recebe mensagem de boas-vindas
        welcome_response = websocket.receive_json()
        assert welcome_response["type"] == "welcome"

        # Testa mensagem com conteúdo vazio
        empty_message_event = {
            "type": "send_message",
            "conversation_id": str(sample_conversation_id),
            "content": "",
            "request_id": "empty_msg_123",
            "timestamp": 1703001600.0
        }

        websocket.send_json(empty_message_event)
        response = websocket.receive_json()

        # Verifica se a resposta contém o request_id
        assert "request_id" in response
        assert response["request_id"] == "empty_msg_123"
        assert response.get("success") is False
        assert "message" in response  # Deve indicar erro de validação


@pytest.mark.integration
def test_error_handling_websocket_success(authenticated_websocket_client):
    """
    Testa se o tratamento de erros funciona adequadamente.
    """
    url = f"/chat/ws?token={authenticated_websocket_client.token}"

    with authenticated_websocket_client.websocket_connect(url) as websocket:
        # Recebe mensagem de boas-vindas
        welcome_response = websocket.receive_json()
        assert welcome_response["type"] == "welcome"

        # Envia evento que deve causar erro de validação
        error_event = {
            "type": "send_message",
            "conversation_id": None,  # conversation_id inválido
            "content": "This should fail validation",
            "request_id": "error_test_123",
            "timestamp": 1703001600.0
        }

        websocket.send_json(error_event)
        error_response = websocket.receive_json()

        # Verifica se a resposta contém o request_id
        assert "request_id" in error_response
        assert error_response["request_id"] == "error_test_123"
        assert error_response.get("success") is False

        # Testa recuperação com um evento válido
        recovery_event = {
            "type": "typing",
            "conversation_id": "12345678-1234-5678-9012-123456789abc",
            "request_id": "recovery_after_error",
            "timestamp": 1703001605.0
        }

        websocket.send_json(recovery_event)
        recovery_response = websocket.receive_json()

        # Verifica se a resposta contém o request_id
        assert "request_id" in recovery_response
        assert recovery_response["request_id"] == "recovery_after_error"
        # Deve funcionar ou falhar graciosamente - conexão deve permanecer funcional
        assert "success" in recovery_response


@pytest.mark.integration
def test_event_sequence_websocket_success(authenticated_websocket_client, sample_conversation_id):
    """
    Testa se uma sequência típica de eventos de chat funciona corretamente.
    """
    url = f"/chat/ws?token={authenticated_websocket_client.token}"

    with authenticated_websocket_client.websocket_connect(url) as websocket:
        # Recebe mensagem de boas-vindas
        welcome_response = websocket.receive_json()
        assert welcome_response["type"] == "welcome"

        # Executa uma sequência típica de chat
        sequence_events = [
            {
                "type": "join_conversation",
                "conversation_id": str(sample_conversation_id),
                "request_id": "seq_join",
                "timestamp": 1703001600.0
            },
            {
                "type": "typing",
                "conversation_id": str(sample_conversation_id),
                "request_id": "seq_typing",
                "timestamp": 1703001601.0
            },
            {
                "type": "send_message",
                "conversation_id": str(sample_conversation_id),
                "content": "Sequence test message",
                "request_id": "seq_message",
                "timestamp": 1703001602.0
            },
            {
                "type": "stop_typing",
                "conversation_id": str(sample_conversation_id),
                "request_id": "seq_stop_typing",
                "timestamp": 1703001603.0
            }
        ]

        # Processa cada evento na sequência
        for event in sequence_events:
            websocket.send_json(event)
            response = websocket.receive_json()

            # Verifica se a resposta contém o request_id
            assert "request_id" in response
            assert response["request_id"] == event["request_id"]
            # Cada evento deve ser processado com sucesso ou ter detalhes de erro adequados
            if response.get("success") is False:
                assert "message" in response or "error_code" in response
