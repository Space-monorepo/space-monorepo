import io

import pytest
from fastapi import status

from app.api.chat.schema import (
    ConversationCreate,
    MessageCreate,
    MessageTypeEnum,
)


@pytest.mark.integration
def test_create_conversation_route(
    authenticate_client, secondary_user_on_db, user_connection_on_db
):
    """Test creating a new conversation between two users."""
    conversation_data = ConversationCreate(
        participant_user_id=str(secondary_user_on_db.id)
    )

    response = authenticate_client.post(
        '/chat/conversations',
        json=conversation_data.model_dump(mode='json'),
    )

    assert response.status_code == status.HTTP_201_CREATED
    response_data = response.json()
    assert 'id' in response_data
    assert 'user1' in response_data
    assert 'user2' in response_data
    assert 'other_participant' in response_data
    assert 'created_at' in response_data


@pytest.mark.integration
def test_create_conversation_with_self_error(authenticate_client, user_on_db):
    """Test that creating a conversation with yourself is not allowed."""
    conversation_data = ConversationCreate(participant_user_id=str(user_on_db.id))

    response = authenticate_client.post(
        '/chat/conversations',
        json=conversation_data.model_dump(mode='json'),
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    response_data = response.json()
    assert (
        'cannot create a conversation with yourself' in response_data['message'].lower()
    )
    assert response_data['error_type'] == 'cannot_create_self_conversation'


@pytest.mark.integration
def test_get_conversation_route(authenticate_client, conversation_on_db):
    """Test getting conversation details."""
    response = authenticate_client.get(f'/chat/conversations/{conversation_on_db.id}')

    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert response_data['id'] == str(conversation_on_db.id)
    assert 'user1' in response_data
    assert 'user2' in response_data
    assert 'other_participant' in response_data


@pytest.mark.integration
def test_get_conversation_not_found_route(authenticate_client):
    """Test getting a non-existent conversation."""
    fake_id = '12345678-1234-5678-1234-567812345678'
    response = authenticate_client.get(f'/chat/conversations/{fake_id}')

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.integration
def test_list_user_conversations_route(authenticate_client, conversation_on_db):
    """Test listing user conversations with pagination."""
    response = authenticate_client.get('/chat/conversations')

    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert 'items' in response_data
    assert 'total' in response_data
    assert response_data['total'] >= 1
    assert len(response_data['items']) >= 1


@pytest.mark.integration
def test_list_user_conversations_with_pagination_route(
    authenticate_client, conversation_on_db
):
    """Test listing conversations with pagination parameters."""
    response = authenticate_client.get('/chat/conversations?offset=0&limit=10')

    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert 'items' in response_data
    assert 'total' in response_data
    assert len(response_data['items']) <= 10


@pytest.mark.integration
def test_send_message_route(authenticate_client, conversation_on_db):
    """Test sending a text message in a conversation."""
    message_data = MessageCreate(
        content='Hello, this is a test message!',
        reply_to_message_id=None,
    )

    response = authenticate_client.post(
        f'/chat/conversations/{conversation_on_db.id}/messages',
        json=message_data.model_dump(mode='json'),
    )

    assert response.status_code == status.HTTP_201_CREATED
    response_data = response.json()
    assert response_data['content'] == message_data.content
    assert response_data['message_type'] == 'text'
    assert 'id' in response_data
    assert 'sender' in response_data
    assert 'created_at' in response_data
    assert response_data['is_read'] is False


@pytest.mark.integration
def test_send_message_empty_content_error(authenticate_client, conversation_on_db):
    """Test that sending a message with empty content fails validation."""
    message_data = {'content': '', 'reply_to_message_id': None}

    response = authenticate_client.post(
        f'/chat/conversations/{conversation_on_db.id}/messages',
        json=message_data,
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.integration
def test_send_message_to_nonexistent_conversation_error(authenticate_client):
    """Test sending a message to a non-existent conversation."""
    fake_id = '12345678-1234-5678-1234-567812345678'
    message_data = MessageCreate(content='Test message', reply_to_message_id=None)

    response = authenticate_client.post(
        f'/chat/conversations/{fake_id}/messages',
        json=message_data.model_dump(mode='json'),
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.integration
def test_send_message_with_attachment_route(
    authenticate_client, conversation_on_db, mock_cloudinary_upload
):
    """Test sending a message with file attachment."""
    file_content = b'fake image content'
    file = io.BytesIO(file_content)
    file.name = 'test_image.jpg'

    response = authenticate_client.post(
        f'/chat/conversations/{conversation_on_db.id}/messages/attachment',
        data={
            'message_type': MessageTypeEnum.image.value,
            'content': 'Check out this image!',
        },
        files={'file': ('test_image.jpg', file, 'image/jpeg')},
    )

    # Should succeed with mocked cloudinary
    assert response.status_code == status.HTTP_201_CREATED
    response_data = response.json()
    assert response_data['content'] == 'Check out this image!'
    assert response_data['message_type'] == 'image'
    assert 'attachments' in response_data
    assert len(response_data['attachments']) == 1
    attachment = response_data['attachments'][0]
    assert attachment['file_name'] == 'test_image.jpg'
    assert attachment['file_type'] == 'image/jpeg'
    assert 'cloudinary.com' in attachment['file_url']


@pytest.mark.integration
def test_send_message_with_attachment_invalid_type_error(
    authenticate_client, conversation_on_db, mock_cloudinary_upload
):
    """Test that sending attachment with text message type fails."""
    file_content = b'fake image content'
    file = io.BytesIO(file_content)
    file.name = 'test_image.jpg'

    response = authenticate_client.post(
        f'/chat/conversations/{conversation_on_db.id}/messages/attachment',
        data={
            'message_type': MessageTypeEnum.text.value,
            'content': 'This should fail',
        },
        files={'file': ('test_image.jpg', file, 'image/jpeg')},
    )

    # Should return 400 because text type should use regular message endpoint
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    response_data = response.json()
    assert 'text message' in response_data['message'].lower()


@pytest.mark.integration
def test_get_conversation_messages_route(
    authenticate_client, conversation_on_db, user_on_db, message_factory
):
    """Test getting messages from a conversation."""
    message_factory(
        conversation_id=conversation_on_db.id,
        sender_id=user_on_db.id,
        content='Test message',
        message_type='text',
    )

    response = authenticate_client.get(
        f'/chat/conversations/{conversation_on_db.id}/messages'
    )

    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert 'items' in response_data
    assert 'total' in response_data
    assert response_data['total'] >= 1


@pytest.mark.integration
def test_get_conversation_messages_with_pagination_route(
    authenticate_client, conversation_on_db, user_on_db, message_factory
):
    """Test getting messages with pagination parameters."""
    for i in range(5):
        message_factory(
            conversation_id=conversation_on_db.id,
            sender_id=user_on_db.id,
            content=f'Test message {i}',
            message_type='text',
        )

    response = authenticate_client.get(
        f'/chat/conversations/{conversation_on_db.id}/messages?offset=0&limit=3'
    )

    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert 'items' in response_data
    assert len(response_data['items']) <= 3


@pytest.mark.integration
def test_mark_message_as_read_route(
    authenticate_client, conversation_on_db, user_on_db, message_factory
):
    """Test marking a specific message as read."""
    message = message_factory(
        conversation_id=conversation_on_db.id,
        sender_id=user_on_db.id,
        content='Test message',
        message_type='text',
        is_read=False,
    )

    response = authenticate_client.patch(f'/chat/messages/{message.id}/read')

    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.integration
def test_mark_message_as_read_not_found_error(authenticate_client):
    """Test marking a non-existent message as read."""
    fake_id = '12345678-1234-5678-1234-567812345678'
    response = authenticate_client.patch(f'/chat/messages/{fake_id}/read')

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.integration
def test_mark_conversation_messages_as_read_route(
    authenticate_client, conversation_on_db, user_on_db, message_factory
):
    """Test marking all messages in a conversation as read."""
    for i in range(3):
        message_factory(
            conversation_id=conversation_on_db.id,
            sender_id=user_on_db.id,
            content=f'Test message {i}',
            message_type='text',
            is_read=False,
        )

    response = authenticate_client.patch(
        f'/chat/conversations/{conversation_on_db.id}/messages/read'
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.integration
def test_get_conversation_unread_count_route(
    authenticate_client, conversation_on_db, secondary_user_on_db, message_factory
):
    """Test getting unread message count for a conversation."""
    for i in range(3):
        message_factory(
            conversation_id=conversation_on_db.id,
            sender_id=secondary_user_on_db.id,
            content=f'Unread message {i}',
            message_type='text',
            is_read=False,
        )

    response = authenticate_client.get(
        f'/chat/conversations/{conversation_on_db.id}/unread-count'
    )

    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert 'unread_count' in response_data
    assert response_data['unread_count'] >= 0


@pytest.mark.integration
def test_delete_message_route(
    authenticate_client, conversation_on_db, user_on_db, message_factory
):
    """Test deleting a message (only by sender)."""
    message = message_factory(
        conversation_id=conversation_on_db.id,
        sender_id=user_on_db.id,
        content='Test message to delete',
        message_type='text',
    )

    response = authenticate_client.delete(f'/chat/messages/{message.id}')

    assert response.status_code == status.HTTP_204_NO_CONTENT

    response = authenticate_client.get(
        f'/chat/conversations/{conversation_on_db.id}/messages'
    )
    messages = response.json()['items']
    message_ids = [msg['id'] for msg in messages]
    assert str(message.id) not in message_ids


@pytest.mark.integration
def test_delete_message_not_sender_error(
    authenticate_member_client, conversation_on_db, user_on_db, message_factory
):
    """Test that a user cannot delete another user's message."""
    message = message_factory(
        conversation_id=conversation_on_db.id,
        sender_id=user_on_db.id,
        content='Test message from another user',
        message_type='text',
    )

    response = authenticate_member_client.delete(f'/chat/messages/{message.id}')

    assert response.status_code == status.HTTP_403_FORBIDDEN
    response_data = response.json()
    assert 'only delete your own messages' in response_data['message'].lower()


@pytest.mark.integration
def test_delete_message_not_found_error(authenticate_client):
    """Test deleting a non-existent message."""
    fake_id = '12345678-1234-5678-1234-567812345678'
    response = authenticate_client.delete(f'/chat/messages/{fake_id}')

    assert response.status_code == status.HTTP_404_NOT_FOUND
    response_data = response.json()
    assert 'not found' in response_data['message'].lower()


@pytest.mark.integration
def test_get_attachment_route(
    authenticate_client,
    conversation_on_db,
    user_on_db,
    message_factory,
    attachment_factory,
):
    """Test getting attachment details."""
    message = message_factory(
        conversation_id=conversation_on_db.id,
        sender_id=user_on_db.id,
        content='Message with attachment',
        message_type='image',
    )

    attachment = attachment_factory(
        message_id=message.id,
        file_name='test_attachment.jpg',
        file_size=2048,
        file_type='image/jpeg',
        file_url='https://example.com/test_attachment.jpg',
    )

    response = authenticate_client.get(f'/chat/attachments/{attachment.id}')

    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert response_data['id'] == str(attachment.id)
    assert response_data['file_name'] == 'test_attachment.jpg'
    assert response_data['file_size'] == 2048
    assert response_data['file_type'] == 'image/jpeg'


@pytest.mark.integration
def test_get_attachment_not_found_error(authenticate_client):
    """Test getting a non-existent attachment."""
    fake_id = '12345678-1234-5678-1234-567812345678'
    response = authenticate_client.get(f'/chat/attachments/{fake_id}')

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.integration
def test_delete_attachment_route(
    authenticate_client,
    conversation_on_db,
    user_on_db,
    message_factory,
    attachment_factory,
):
    """Test deleting an attachment (only by message sender)."""
    message = message_factory(
        conversation_id=conversation_on_db.id,
        sender_id=user_on_db.id,
        content='Message with attachment',
        message_type='image',
    )

    attachment = attachment_factory(
        message_id=message.id,
        file_name='attachment_to_delete.jpg',
        file_size=2048,
        file_type='image/jpeg',
        file_url='https://example.com/attachment_to_delete.jpg',
    )

    response = authenticate_client.delete(f'/chat/attachments/{attachment.id}')

    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.integration
def test_delete_attachment_not_sender_error(
    authenticate_member_client,
    conversation_on_db,
    user_on_db,
    message_factory,
    attachment_factory,
):
    """Test that a user cannot delete another user's attachment."""
    message = message_factory(
        conversation_id=conversation_on_db.id,
        sender_id=user_on_db.id,
        content='Message with attachment',
        message_type='image',
    )

    attachment = attachment_factory(
        message_id=message.id,
        file_name='protected_attachment.jpg',
        file_size=2048,
        file_type='image/jpeg',
        file_url='https://example.com/protected_attachment.jpg',
    )

    response = authenticate_member_client.delete(f'/chat/attachments/{attachment.id}')

    assert response.status_code == status.HTTP_403_FORBIDDEN
    response_data = response.json()
    assert (
        'only delete attachments from your own messages'
        in response_data['message'].lower()
    )


@pytest.mark.integration
def test_chat_health_check_route(authenticate_client):
    """Test chat service health check endpoint."""
    response = authenticate_client.get('/chat/health')

    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert response_data['status'] == 'healthy'
    assert response_data['service'] == 'chat'


@pytest.mark.integration
def test_send_reply_message_route(
    authenticate_client, conversation_on_db, user_on_db, message_factory
):
    """Test sending a message that replies to another message."""
    original_message = message_factory(
        conversation_id=conversation_on_db.id,
        sender_id=user_on_db.id,
        content='Original message',
        message_type='text',
    )

    reply_data = MessageCreate(
        content='This is a reply',
        reply_to_message_id=str(original_message.id),
    )

    response = authenticate_client.post(
        f'/chat/conversations/{conversation_on_db.id}/messages',
        json=reply_data.model_dump(mode='json'),
    )

    assert response.status_code == status.HTTP_201_CREATED
    response_data = response.json()
    assert response_data['content'] == reply_data.content
    assert 'reply_to_message' in response_data or 'reply_to_message_id' in response_data


@pytest.mark.integration
def test_list_conversations_with_name_filter_route(
    authenticate_client, conversation_on_db
):
    """Test listing conversations with name filter."""
    response = authenticate_client.get('/chat/conversations?name=test')

    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert 'items' in response_data
    assert 'total' in response_data


@pytest.mark.integration
def test_get_messages_with_before_message_id_route(
    authenticate_client, conversation_on_db, user_on_db, message_factory
):
    """Test getting messages before a specific message ID."""
    messages = []
    for i in range(5):
        message = message_factory(
            conversation_id=conversation_on_db.id,
            sender_id=user_on_db.id,
            content=f'Message {i}',
            message_type='text',
        )
        messages.append(message)
    before_message_id = messages[2].id

    response = authenticate_client.get(
        f'/chat/conversations/{conversation_on_db.id}/messages?before_message_id={before_message_id}'
    )

    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert 'items' in response_data


@pytest.mark.integration
def test_mark_conversation_messages_as_read_with_up_to_message_id_route(
    authenticate_client, conversation_on_db, user_on_db, message_factory
):
    """Test marking messages as read up to a specific message ID."""
    messages = []
    for i in range(3):
        message = message_factory(
            conversation_id=conversation_on_db.id,
            sender_id=user_on_db.id,
            content=f'Message {i}',
            message_type='text',
            is_read=False,
        )
        messages.append(message)

    response = authenticate_client.patch(
        f'/chat/conversations/{conversation_on_db.id}/messages/read?up_to_message_id={messages[1].id}'
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.integration
def test_create_conversation_users_not_connected_error(
    authenticate_client, secondary_user_on_db
):
    """Test that users must be connected to create a conversation."""
    conversation_data = ConversationCreate(
        participant_user_id=str(secondary_user_on_db.id)
    )

    response = authenticate_client.post(
        '/chat/conversations',
        json=conversation_data.model_dump(mode='json'),
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
