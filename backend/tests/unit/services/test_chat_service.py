from datetime import datetime, timezone
from unittest.mock import Mock, patch
from uuid import uuid4

import pytest

from app.api.chat.exceptions import (
    CannotCreateSelfConversationError,
    ConversationAlreadyExistsError,
    ConversationNotFoundError,
    FileNotFoundError,
    MessageNotFoundError,
    UnauthorizedConversationAccessError,
    UnauthorizedMessageAccessError,
    UsersNotConnectedError,
)
from app.api.chat.model import Conversation, Message, MessageAttachment
from app.api.chat.schema import (
    ConversationParticipant,
    ConversationResponse,
    ConversationSearchParams,
    MessageAttachmentResponse,
    MessageResponse,
    MessageSearchParams,
    MessageTypeEnum,
)
from app.api.chat.service import ChatService


@pytest.mark.unit
def test_create_conversation_service_success():
    """
    Tests the `create_conversation` method of ChatService.

    Scenario:
    - Given two connected users who want to start a conversation
    - When the service creates a new conversation
    - Then it should return the created conversation with mapped response
    """
    # Arrange
    fake_conversation_id = uuid4()
    fake_user_id = uuid4()
    fake_participant_id = uuid4()
    fake_created_at = datetime.now(timezone.utc)
    fake_updated_at = datetime.now(timezone.utc)

    # Mock user objects
    fake_user = Mock()
    fake_user.id = fake_user_id
    fake_user.name = 'John Doe'
    fake_user.profile_image_url = 'https://example.com/john.jpg'

    fake_participant = Mock()
    fake_participant.id = fake_participant_id
    fake_participant.name = 'Jane Smith'
    fake_participant.profile_image_url = 'https://example.com/jane.jpg'

    # Mock connection
    fake_connection = Mock()
    fake_connection.status = 'accepted'

    # Mock created conversation
    fake_created_conversation = Mock(spec=Conversation)
    fake_created_conversation.id = fake_conversation_id
    fake_created_conversation.user1_id = str(fake_user_id)
    fake_created_conversation.user2_id = str(fake_participant_id)
    fake_created_conversation.created_at = fake_created_at
    fake_created_conversation.updated_at = fake_updated_at
    fake_created_conversation.last_message_id = None
    fake_created_conversation.user1 = fake_user
    fake_created_conversation.user2 = fake_participant
    fake_created_conversation.last_message = None

    # Mock repositories and services
    mock_tm = Mock()
    mock_conversation_repo = Mock()
    mock_message_repo = Mock()
    mock_user_service = Mock()

    mock_user_service.get_user.side_effect = [fake_user, fake_participant]
    mock_user_service.get_connection_status.return_value = fake_connection
    mock_conversation_repo.find_conversation_between_users.return_value = None
    mock_conversation_repo.create_conversation.return_value = fake_created_conversation
    mock_message_repo.count_unread_messages.return_value = 0

    service = ChatService(mock_tm)
    service.conversation_repo = mock_conversation_repo
    service.message_repo = mock_message_repo
    service.user_service = mock_user_service

    # Act
    result = service.create_conversation(fake_user_id, fake_participant_id)

    # Assert
    mock_user_service.get_user.assert_any_call(fake_user_id)
    mock_user_service.get_user.assert_any_call(fake_participant_id)
    mock_user_service.get_connection_status.assert_called_once_with(
        fake_user_id, fake_participant_id
    )
    mock_conversation_repo.find_conversation_between_users.assert_called_once_with(
        fake_user_id, fake_participant_id
    )
    mock_conversation_repo.create_conversation.assert_called_once_with(
        fake_user_id, fake_participant_id
    )
    assert result is not None
    assert isinstance(result, ConversationResponse)
    assert result.id == fake_conversation_id


@pytest.mark.unit
def test_create_conversation_service_with_self_error():
    """
    Tests the `create_conversation` method when user tries to create conversation with themselves.

    Scenario:
    - Given a user trying to create a conversation with themselves
    - When the service validates the request
    - Then it should raise CannotCreateSelfConversationError
    """
    # Arrange
    fake_user_id = uuid4()

    mock_tm = Mock()
    service = ChatService(mock_tm)

    # Act & Assert
    with pytest.raises(CannotCreateSelfConversationError) as exc_info:
        service.create_conversation(fake_user_id, fake_user_id)

    assert 'Cannot create a conversation with yourself' in str(exc_info.value)


@pytest.mark.unit
def test_create_conversation_service_users_not_connected_error():
    """
    Tests the `create_conversation` method when users are not connected.

    Scenario:
    - Given two users who are not connected
    - When the service checks connection status
    - Then it should raise UsersNotConnectedError
    """
    # Arrange
    fake_user_id = uuid4()
    fake_participant_id = uuid4()

    fake_user = Mock()
    fake_user.id = fake_user_id

    fake_participant = Mock()
    fake_participant.id = fake_participant_id

    mock_tm = Mock()
    mock_user_service = Mock()
    mock_user_service.get_user.side_effect = [fake_user, fake_participant]
    mock_user_service.get_connection_status.return_value = None

    service = ChatService(mock_tm)
    service.user_service = mock_user_service

    # Act & Assert
    with pytest.raises(UsersNotConnectedError) as exc_info:
        service.create_conversation(fake_user_id, fake_participant_id)

    assert 'Users must be connected' in str(exc_info.value)


@pytest.mark.unit
def test_create_conversation_service_already_exists_error():
    """
    Tests the `create_conversation` method when conversation already exists.

    Scenario:
    - Given two users who already have a conversation
    - When the service checks for existing conversation
    - Then it should raise ConversationAlreadyExistsError
    """
    # Arrange
    fake_user_id = uuid4()
    fake_participant_id = uuid4()

    fake_user = Mock()
    fake_user.id = fake_user_id

    fake_participant = Mock()
    fake_participant.id = fake_participant_id

    fake_connection = Mock()
    fake_connection.status = 'accepted'

    fake_existing_conversation = Mock()

    mock_tm = Mock()
    mock_conversation_repo = Mock()
    mock_user_service = Mock()

    mock_user_service.get_user.side_effect = [fake_user, fake_participant]
    mock_user_service.get_connection_status.return_value = fake_connection
    mock_conversation_repo.find_conversation_between_users.return_value = (
        fake_existing_conversation
    )

    service = ChatService(mock_tm)
    service.conversation_repo = mock_conversation_repo
    service.user_service = mock_user_service

    # Act & Assert
    with pytest.raises(ConversationAlreadyExistsError) as exc_info:
        service.create_conversation(fake_user_id, fake_participant_id)

    assert 'Conversation already exists' in str(exc_info.value)


@pytest.mark.unit
def test_get_conversation_service_success():
    """
    Tests the `get_conversation` method of ChatService.

    Scenario:
    - Given a valid conversation ID and user who is a participant
    - When the service retrieves the conversation
    - Then it should return the conversation with mapped response
    """
    # Arrange
    fake_conversation_id = uuid4()
    fake_user_id = uuid4()
    fake_other_user_id = uuid4()

    fake_user = Mock()
    fake_user.id = fake_user_id
    fake_user.name = 'Current User'
    fake_user.profile_image_url = 'https://example.com/current.jpg'

    fake_other_user = Mock()
    fake_other_user.id = fake_other_user_id
    fake_other_user.name = 'Other User'
    fake_other_user.profile_image_url = 'https://example.com/other.jpg'

    fake_conversation = Mock(spec=Conversation)
    fake_conversation.id = str(fake_conversation_id)
    fake_conversation.user1_id = str(fake_user_id)
    fake_conversation.user2_id = str(fake_other_user_id)
    fake_conversation.created_at = datetime.now(timezone.utc)
    fake_conversation.updated_at = datetime.now(timezone.utc)
    fake_conversation.last_message_id = None
    fake_conversation.user1 = fake_user
    fake_conversation.user2 = fake_other_user
    fake_conversation.last_message = None

    mock_tm = Mock()
    mock_conversation_repo = Mock()
    mock_message_repo = Mock()

    mock_conversation_repo.get_conversation_with_participants.return_value = (
        fake_conversation
    )
    mock_conversation_repo.validate_user_participation.return_value = True
    mock_message_repo.count_unread_messages.return_value = 2

    service = ChatService(mock_tm)
    service.conversation_repo = mock_conversation_repo
    service.message_repo = mock_message_repo

    # Act
    result = service.get_conversation(fake_conversation_id, fake_user_id)

    # Assert
    mock_conversation_repo.get_conversation_with_participants.assert_called_once_with(
        fake_conversation_id
    )
    mock_conversation_repo.validate_user_participation.assert_called_once_with(
        fake_conversation_id, fake_user_id
    )
    mock_message_repo.count_unread_messages.assert_called_once()
    assert result is not None
    assert isinstance(result, ConversationResponse)
    assert result.id == fake_conversation_id


@pytest.mark.unit
def test_get_conversation_service_not_found_error():
    """
    Tests the `get_conversation` method when conversation doesn't exist.

    Scenario:
    - Given an invalid conversation ID
    - When the service tries to retrieve the conversation
    - Then it should raise ConversationNotFoundError
    """
    # Arrange
    fake_conversation_id = uuid4()
    fake_user_id = uuid4()

    mock_tm = Mock()
    mock_conversation_repo = Mock()
    mock_conversation_repo.get_conversation_with_participants.return_value = None

    service = ChatService(mock_tm)
    service.conversation_repo = mock_conversation_repo

    # Act & Assert
    with pytest.raises(ConversationNotFoundError) as exc_info:
        service.get_conversation(fake_conversation_id, fake_user_id)

    assert 'Conversation not found' in str(exc_info.value)


@pytest.mark.unit
def test_get_conversation_service_unauthorized_access_error():
    """
    Tests the `get_conversation` method when user is not a participant.

    Scenario:
    - Given a user who is not part of the conversation
    - When the service validates participation
    - Then it should raise UnauthorizedConversationAccessError
    """
    # Arrange
    fake_conversation_id = uuid4()
    fake_user_id = uuid4()

    fake_conversation = Mock()
    fake_user = Mock()
    fake_user.id = fake_user_id
    fake_user.name = 'User'
    fake_user.profile_image_url = None

    fake_other_user = Mock()
    fake_other_user.id = uuid4()
    fake_other_user.name = 'Other'
    fake_other_user.profile_image_url = None

    fake_conversation = Mock(spec=Conversation)
    fake_conversation.id = fake_conversation_id
    fake_conversation.user1_id = str(fake_user_id)
    fake_conversation.user2_id = str(uuid4())
    fake_conversation.created_at = datetime.now(timezone.utc)
    fake_conversation.updated_at = datetime.now(timezone.utc)
    fake_conversation.last_message_id = None
    fake_conversation.user1 = fake_user
    fake_conversation.user2 = fake_other_user
    fake_conversation.last_message = None

    mock_tm = Mock()
    mock_conversation_repo = Mock()
    mock_message_repo = Mock()
    mock_conversation_repo.get_conversation_with_participants.return_value = (
        fake_conversation
    )
    mock_conversation_repo.validate_user_participation.return_value = False
    mock_message_repo.count_unread_messages.return_value = 0

    service = ChatService(mock_tm)
    service.conversation_repo = mock_conversation_repo
    service.message_repo = mock_message_repo

    # Act & Assert
    with pytest.raises(UnauthorizedConversationAccessError) as exc_info:
        service.get_conversation(fake_conversation_id, fake_user_id)

    assert 'not participate in this conversation' in str(exc_info.value)


@pytest.mark.unit
def test_list_user_conversations_service_success():
    """
    Tests the `list_user_conversations` method of ChatService.

    Scenario:
    - Given a user with multiple conversations
    - When the service lists their conversations
    - Then it should return paginated list with mapped responses
    """
    # Arrange
    fake_user_id = uuid4()
    fake_params = ConversationSearchParams(offset=0, limit=20, name=None)

    fake_user1 = Mock()
    fake_user1.id = fake_user_id
    fake_user1.name = 'User 1'
    fake_user1.profile_image_url = None

    fake_user2_id = uuid4()
    fake_user2 = Mock()
    fake_user2.id = fake_user2_id
    fake_user2.name = 'User 2'
    fake_user2.profile_image_url = None

    fake_conversation1 = Mock(spec=Conversation)
    fake_conversation1.id = uuid4()
    fake_conversation1.user1_id = str(fake_user_id)
    fake_conversation1.user2_id = str(fake_user2_id)
    fake_conversation1.created_at = datetime.now(timezone.utc)
    fake_conversation1.updated_at = datetime.now(timezone.utc)
    fake_conversation1.last_message_id = None
    fake_conversation1.user1 = fake_user1
    fake_conversation1.user2 = fake_user2
    fake_conversation1.last_message = None

    fake_params = ConversationSearchParams(limit=20, offset=0)

    mock_tm = Mock()
    mock_conversation_repo = Mock()
    mock_message_repo = Mock()

    mock_conversation_repo.list_user_conversations.return_value = (
        [fake_conversation1],
        1,
    )
    mock_message_repo.count_unread_messages.return_value = 0

    service = ChatService(mock_tm)
    service.conversation_repo = mock_conversation_repo
    service.message_repo = mock_message_repo

    # Act
    result = service.list_user_conversations(fake_user_id, fake_params)

    # Assert
    mock_conversation_repo.list_user_conversations.assert_called_once_with(
        fake_user_id, fake_params
    )
    assert result is not None
    assert result.total == 1
    assert len(result.items) == 1
    assert result.current_offset == 0
    assert result.current_limit == 20


@pytest.mark.unit
def test_send_message_service_success():
    """
    Tests the `send_message` method of ChatService.

    Scenario:
    - Given a valid conversation and message content
    - When the service sends a message
    - Then it should create the message and return mapped response
    """
    # Arrange
    fake_conversation_id = uuid4()
    fake_sender_id = uuid4()
    fake_message_id = uuid4()
    fake_content = 'Hello, how are you?'

    fake_user = Mock()
    fake_user.id = fake_sender_id
    fake_user.name = 'Sender'
    fake_user.profile_image_url = 'https://example.com/sender.jpg'

    fake_conversation = Mock(spec=Conversation)
    fake_conversation.id = fake_conversation_id
    fake_conversation.user1_id = str(fake_sender_id)
    fake_conversation.user2_id = str(uuid4())

    fake_message = Mock(spec=Message)
    fake_message.id = fake_message_id
    fake_message.conversation_id = str(fake_conversation_id)
    fake_message.sender_id = str(fake_sender_id)
    fake_message.content = fake_content
    fake_message.message_type = 'text'
    fake_message.created_at = datetime.now(timezone.utc)
    fake_message.is_read = False
    fake_message.reply_to_message_id = None
    fake_message.sender = fake_user
    fake_message.reply_to_message = None
    fake_message.attachments = []

    mock_tm = Mock()
    mock_conversation_repo = Mock()
    mock_message_repo = Mock()

    mock_conversation_repo.get_conversation_with_participants.return_value = (
        fake_conversation
    )
    mock_conversation_repo.validate_user_participation.return_value = True
    mock_message_repo.create_message.return_value = fake_message
    mock_message_repo.get_message_with_details.return_value = fake_message

    service = ChatService(mock_tm)
    service.conversation_repo = mock_conversation_repo
    service.message_repo = mock_message_repo

    # Act
    result = service.send_message(
        fake_conversation_id, fake_sender_id, fake_content, None
    )

    # Assert
    mock_conversation_repo.get_conversation_with_participants.assert_called_once()
    mock_conversation_repo.validate_user_participation.assert_called_once()
    mock_message_repo.create_message.assert_called_once()
    mock_conversation_repo.update_last_message.assert_called_once()
    assert result is not None
    assert isinstance(result, MessageResponse)
    assert result.content == fake_content


@pytest.mark.unit
def test_send_message_service_with_reply_success():
    """
    Tests the `send_message` method with reply to another message.

    Scenario:
    - Given a message being sent as a reply to another message
    - When the service validates the reply message exists
    - Then it should create the message with reply reference
    """
    # Arrange
    fake_conversation_id = uuid4()
    fake_sender_id = uuid4()
    fake_message_id = uuid4()
    fake_reply_to_id = uuid4()
    fake_content = 'This is a reply'

    fake_user = Mock()
    fake_user.id = fake_sender_id
    fake_user.name = 'Sender'
    fake_user.profile_image_url = None

    fake_conversation = Mock(spec=Conversation)
    fake_conversation.id = str(fake_conversation_id)
    fake_conversation.user1_id = str(fake_sender_id)
    fake_conversation.user2_id = str(uuid4())

    fake_reply_message = Mock(spec=Message)
    fake_reply_message.id = fake_reply_to_id
    fake_reply_message.conversation_id = str(fake_conversation_id)

    fake_reply_sender = Mock()
    fake_reply_sender.id = uuid4()
    fake_reply_sender.name = 'Reply Sender'
    fake_reply_sender.profile_image_url = None

    fake_reply_message.sender = fake_reply_sender
    fake_reply_message.reply_to_message = None
    fake_reply_message.attachments = []
    fake_reply_message.sender_id = str(fake_reply_sender.id)
    fake_reply_message.content = 'Original message'
    fake_reply_message.message_type = 'text'
    fake_reply_message.created_at = datetime.now(timezone.utc)
    fake_reply_message.is_read = True
    fake_reply_message.reply_to_message_id = None

    fake_message = Mock(spec=Message)
    fake_message.id = str(fake_message_id)
    fake_message.conversation_id = str(fake_conversation_id)
    fake_message.sender_id = str(fake_sender_id)
    fake_message.content = fake_content
    fake_message.message_type = 'text'
    fake_message.created_at = datetime.now(timezone.utc)
    fake_message.is_read = False
    fake_message.reply_to_message_id = str(fake_reply_to_id)
    fake_message.sender = fake_user
    fake_message.reply_to_message = fake_reply_message
    fake_message.attachments = []

    mock_tm = Mock()
    mock_conversation_repo = Mock()
    mock_message_repo = Mock()

    mock_conversation_repo.get_conversation_with_participants.return_value = (
        fake_conversation
    )
    mock_conversation_repo.validate_user_participation.return_value = True
    mock_message_repo.get_by_id.return_value = fake_reply_message
    mock_message_repo.create_message.return_value = fake_message
    mock_message_repo.get_message_with_details.return_value = fake_message

    service = ChatService(mock_tm)
    service.conversation_repo = mock_conversation_repo
    service.message_repo = mock_message_repo

    # Act
    result = service.send_message(
        fake_conversation_id, fake_sender_id, fake_content, fake_reply_to_id
    )

    # Assert
    mock_message_repo.get_by_id.assert_called_once_with(fake_reply_to_id)
    assert result is not None
    assert result.reply_to_message_id == fake_reply_to_id


@pytest.mark.unit
def test_send_message_service_reply_not_found_error():
    """
    Tests the `send_message` method when reply message doesn't exist.

    Scenario:
    - Given a reply_to_message_id that doesn't exist
    - When the service validates the reply message
    - Then it should raise MessageNotFoundError
    """
    # Arrange
    fake_conversation_id = uuid4()
    fake_sender_id = uuid4()
    fake_reply_to_id = uuid4()
    fake_content = 'This is a reply'

    fake_conversation = Mock(spec=Conversation)
    fake_conversation.id = fake_conversation_id

    mock_tm = Mock()
    mock_conversation_repo = Mock()
    mock_message_repo = Mock()

    mock_conversation_repo.get_conversation_with_participants.return_value = (
        fake_conversation
    )
    mock_conversation_repo.validate_user_participation.return_value = True
    mock_message_repo.get_by_id.return_value = None

    service = ChatService(mock_tm)
    service.conversation_repo = mock_conversation_repo
    service.message_repo = mock_message_repo

    # Act & Assert
    with pytest.raises(MessageNotFoundError) as exc_info:
        service.send_message(
            fake_conversation_id, fake_sender_id, fake_content, fake_reply_to_id
        )

    assert 'Reply message not found' in str(exc_info.value)


@pytest.mark.unit
def test_send_message_with_attachment_service_success():
    """
    Tests the `send_message_with_attachment` method of ChatService.

    Scenario:
    - Given a valid file upload and conversation
    - When the service uploads the file and creates message
    - Then it should return message with attachment
    """
    # Arrange
    fake_conversation_id = uuid4()
    fake_sender_id = uuid4()
    fake_message_id = uuid4()

    fake_file = Mock()
    fake_file.filename = 'test_image.jpg'
    fake_file.content_type = 'image/jpeg'
    fake_file.size = 1024
    fake_file.file.read.return_value = b'fake image content'
    fake_file.file.seek = Mock()

    fake_user = Mock()
    fake_user.id = fake_sender_id
    fake_user.name = 'Sender'
    fake_user.profile_image_url = None

    fake_conversation = Mock(spec=Conversation)
    fake_conversation.id = str(fake_conversation_id)

    fake_attachment = Mock(spec=MessageAttachment)
    fake_attachment.id = uuid4()
    fake_attachment.message_id = str(fake_message_id)
    fake_attachment.file_name = 'test_image.jpg'
    fake_attachment.file_size = 1024
    fake_attachment.file_type = 'image/jpeg'
    fake_attachment.file_url = 'https://res.cloudinary.com/demo/image.jpg'
    fake_attachment.public_id = 'chat/images/test123'
    fake_attachment.thumbnail_url = 'https://res.cloudinary.com/demo/thumb.jpg'
    fake_attachment.created_at = datetime.now(timezone.utc)

    fake_message = Mock(spec=Message)
    fake_message.id = str(fake_message_id)
    fake_message.conversation_id = str(fake_conversation_id)
    fake_message.sender_id = str(fake_sender_id)
    fake_message.content = 'Check this out!'
    fake_message.message_type = 'image'
    fake_message.created_at = datetime.now(timezone.utc)
    fake_message.is_read = False
    fake_message.reply_to_message_id = None
    fake_message.sender = fake_user
    fake_message.reply_to_message = None
    fake_message.attachments = [fake_attachment]

    mock_tm = Mock()
    mock_conversation_repo = Mock()
    mock_message_repo = Mock()
    mock_attachment_repo = Mock()
    mock_upload_service = Mock()

    mock_conversation_repo.get_conversation_with_participants.return_value = (
        fake_conversation
    )
    mock_conversation_repo.validate_user_participation.return_value = True
    mock_message_repo.create_message.return_value = fake_message
    mock_message_repo.get_message_with_details.return_value = fake_message
    mock_attachment_repo.create_attachment.return_value = fake_attachment
    mock_upload_service.upload_file.return_value = {
        'url': 'https://res.cloudinary.com/demo/image.jpg',
        'public_id': 'chat/images/test123',
        'format': 'jpg',
        'size': 1024,
        'thumbnail_url': 'https://res.cloudinary.com/demo/thumb.jpg',
    }

    service = ChatService(mock_tm)
    service.conversation_repo = mock_conversation_repo
    service.message_repo = mock_message_repo
    service.attachment_repo = mock_attachment_repo
    service.upload_service = mock_upload_service

    # Act
    result = service.send_message_with_attachment(
        fake_conversation_id,
        fake_sender_id,
        fake_file,
        MessageTypeEnum.image,
        'Check this out!',
        None,
    )

    # Assert
    mock_upload_service.upload_file.assert_called_once_with(
        fake_file, MessageTypeEnum.image
    )
    mock_attachment_repo.create_attachment.assert_called_once()
    assert result is not None
    assert isinstance(result, MessageResponse)
    assert result.message_type == 'image'
    assert len(result.attachments) == 1


@pytest.mark.unit
def test_get_conversation_messages_service_success():
    """
    Tests the `get_conversation_messages` method.

    Scenario:
    - Given a conversation with messages
    - When a user requests the messages
    - Then it should return paginated messages
    """
    # Arrange
    fake_conversation_id = uuid4()
    fake_user_id = uuid4()
    fake_other_user_id = uuid4()

    fake_user = Mock()
    fake_user.id = fake_user_id
    fake_user.name = 'User'
    fake_user.profile_image_url = None

    fake_other_user = Mock()
    fake_other_user.id = fake_other_user_id
    fake_other_user.name = 'Other User'
    fake_other_user.profile_image_url = None

    fake_conversation = Mock(spec=Conversation)
    fake_conversation.id = str(fake_conversation_id)
    fake_conversation.user1_id = str(fake_user_id)
    fake_conversation.user2_id = str(fake_other_user_id)
    fake_conversation.created_at = datetime.now(timezone.utc)
    fake_conversation.updated_at = datetime.now(timezone.utc)
    fake_conversation.last_message_id = None
    fake_conversation.user1 = fake_user
    fake_conversation.user2 = fake_other_user
    fake_conversation.last_message = None

    fake_message = Mock(spec=Message)
    fake_message.id = str(uuid4())
    fake_message.conversation_id = str(fake_conversation_id)
    fake_message.sender_id = str(fake_other_user_id)
    fake_message.content = 'Hello'
    fake_message.message_type = 'text'
    fake_message.created_at = datetime.now(timezone.utc)
    fake_message.is_read = False
    fake_message.reply_to_message_id = None
    fake_message.sender = fake_other_user
    fake_message.reply_to_message = None
    fake_message.attachments = []

    fake_params = MessageSearchParams(limit=50, offset=0)

    mock_tm = Mock()
    mock_conversation_repo = Mock()
    mock_message_repo = Mock()

    mock_conversation_repo.get_conversation_with_participants.return_value = (
        fake_conversation
    )
    mock_conversation_repo.validate_user_participation.return_value = True
    mock_message_repo.list_conversation_messages.return_value = (
        [fake_message],
        1,
    )

    service = ChatService(mock_tm)
    service.conversation_repo = mock_conversation_repo
    service.message_repo = mock_message_repo

    # Act
    result = service.get_conversation_messages(
        fake_conversation_id, fake_user_id, fake_params
    )

    # Assert
    mock_message_repo.list_conversation_messages.assert_called_once_with(
        fake_conversation_id, fake_params
    )
    assert result.total == 1
    assert len(result.items) == 1
    assert result.items[0].content == 'Hello'


@pytest.mark.unit
def test_mark_message_as_read_service_success():
    """
    Tests the `mark_message_as_read` method of ChatService.

    Scenario:
    - Given an unread message in a conversation
    - When the user marks it as read
    - Then it should update the message status
    """
    # Arrange
    fake_message_id = uuid4()
    fake_user_id = uuid4()
    fake_conversation_id = uuid4()

    fake_sender = Mock()
    fake_sender.id = uuid4()
    fake_sender.name = 'Sender'
    fake_sender.profile_image_url = None

    fake_message = Mock(spec=Message)
    fake_message.id = fake_message_id
    fake_message.conversation_id = str(fake_conversation_id)
    fake_message.sender_id = str(fake_sender.id)
    fake_message.content = 'Test message'
    fake_message.message_type = 'text'
    fake_message.created_at = datetime.now(timezone.utc)
    fake_message.is_read = False
    fake_message.reply_to_message_id = None
    fake_message.sender = fake_sender
    fake_message.reply_to_message = None
    fake_message.attachments = []

    mock_tm = Mock()
    mock_message_repo = Mock()
    mock_conversation_repo = Mock()

    mock_message_repo.get_by_id.return_value = fake_message
    mock_conversation_repo.validate_user_participation.return_value = True
    mock_message_repo.mark_message_as_read.return_value = True

    service = ChatService(mock_tm)
    service.message_repo = mock_message_repo
    service.conversation_repo = mock_conversation_repo

    # Act
    result = service.mark_message_as_read(fake_message_id, fake_user_id)

    # Assert
    mock_message_repo.get_by_id.assert_called_once_with(fake_message_id)
    mock_conversation_repo.validate_user_participation.assert_called_once()
    mock_message_repo.mark_message_as_read.assert_called_once_with(
        fake_message_id, fake_user_id
    )
    assert result is True


@pytest.mark.unit
def test_mark_message_as_read_service_not_found_error():
    """
    Tests the `mark_message_as_read` method when message doesn't exist.

    Scenario:
    - Given an invalid message ID
    - When the service tries to mark it as read
    - Then it should raise MessageNotFoundError
    """
    # Arrange
    fake_message_id = uuid4()
    fake_user_id = uuid4()

    mock_tm = Mock()
    mock_message_repo = Mock()
    mock_message_repo.get_by_id.return_value = None

    service = ChatService(mock_tm)
    service.message_repo = mock_message_repo

    # Act & Assert
    with pytest.raises(MessageNotFoundError) as exc_info:
        service.mark_message_as_read(fake_message_id, fake_user_id)

    assert 'Message not found' in str(exc_info.value)


@pytest.mark.unit
def test_mark_conversation_messages_as_read_service_success():
    """
    Tests the `mark_conversation_messages_as_read` method of ChatService.

    Scenario:
    - Given a conversation with unread messages
    - When the user marks all messages as read
    - Then it should update all message statuses
    """
    # Arrange
    fake_conversation_id = uuid4()
    fake_user_id = uuid4()

    fake_conversation = Mock(spec=Conversation)
    fake_conversation.id = fake_conversation_id

    mock_tm = Mock()
    mock_conversation_repo = Mock()
    mock_message_repo = Mock()

    mock_conversation_repo.get_conversation_with_participants.return_value = (
        fake_conversation
    )
    mock_conversation_repo.validate_user_participation.return_value = True
    fake_message_ids = [uuid4(), uuid4()]
    mock_message_repo.get_unread_message_ids.return_value = fake_message_ids
    mock_message_repo.bulk_mark_as_read.return_value = 5

    service = ChatService(mock_tm)
    service.conversation_repo = mock_conversation_repo
    service.message_repo = mock_message_repo

    # Act
    result = service.mark_conversation_messages_as_read(
        fake_conversation_id, fake_user_id, None
    )

    # Assert
    mock_message_repo.get_unread_message_ids.assert_called_once_with(
        fake_conversation_id, fake_user_id, None
    )
    mock_message_repo.bulk_mark_as_read.assert_called_once_with(
        fake_message_ids, fake_user_id
    )
    assert result == 5


@pytest.mark.unit
def test_get_unread_count_service_success():
    """
    Tests the `get_unread_count` method of ChatService.

    Scenario:
    - Given a conversation with unread messages
    - When the user requests unread count
    - Then it should return the correct count
    """
    # Arrange
    fake_conversation_id = uuid4()
    fake_user_id = uuid4()
    fake_unread_count = 7

    fake_conversation = Mock(spec=Conversation)
    fake_conversation.id = fake_conversation_id

    mock_tm = Mock()
    mock_conversation_repo = Mock()
    mock_message_repo = Mock()

    mock_conversation_repo.get_conversation_with_participants.return_value = (
        fake_conversation
    )
    mock_conversation_repo.validate_user_participation.return_value = True
    mock_message_repo.count_unread_messages.return_value = fake_unread_count

    service = ChatService(mock_tm)
    service.conversation_repo = mock_conversation_repo
    service.message_repo = mock_message_repo

    # Act
    result = service.get_unread_count(fake_conversation_id, fake_user_id)

    # Assert
    mock_message_repo.count_unread_messages.assert_called_once_with(
        fake_conversation_id, fake_user_id
    )
    assert result == fake_unread_count


@pytest.mark.unit
def test_delete_message_service_success():
    """
    Tests the `delete_message` method of ChatService.

    Scenario:
    - Given a message owned by the user
    - When the user deletes the message
    - Then it should remove the message
    """
    # Arrange
    fake_message_id = uuid4()
    fake_user_id = uuid4()

    fake_message = Mock(spec=Message)
    fake_message.id = fake_message_id
    fake_message.sender_id = str(fake_user_id)

    mock_tm = Mock()
    mock_message_repo = Mock()

    mock_message_repo.get_by_id.return_value = fake_message
    mock_message_repo.delete_message.return_value = True

    service = ChatService(mock_tm)
    service.message_repo = mock_message_repo

    # Act
    result = service.delete_message(fake_message_id, fake_user_id)

    # Assert
    mock_message_repo.get_by_id.assert_called_once_with(fake_message_id)
    mock_message_repo.delete_message.assert_called_once_with(fake_message_id)
    assert result is True


@pytest.mark.unit
def test_delete_message_service_not_found_error():
    """
    Tests the `delete_message` method when message doesn't exist.

    Scenario:
    - Given an invalid message ID
    - When the user tries to delete it
    - Then it should raise MessageNotFoundError
    """
    # Arrange
    fake_message_id = uuid4()
    fake_user_id = uuid4()

    mock_tm = Mock()
    mock_message_repo = Mock()
    mock_message_repo.get_by_id.return_value = None

    service = ChatService(mock_tm)
    service.message_repo = mock_message_repo

    # Act & Assert
    with pytest.raises(MessageNotFoundError) as exc_info:
        service.delete_message(fake_message_id, fake_user_id)

    assert 'Message not found' in str(exc_info.value)


@pytest.mark.unit
def test_delete_message_service_unauthorized_error():
    """
    Tests the `delete_message` method when user is not the sender.

    Scenario:
    - Given a message owned by another user
    - When the user tries to delete it
    - Then it should raise UnauthorizedMessageAccessError
    """
    # Arrange
    fake_message_id = uuid4()
    fake_user_id = uuid4()
    fake_other_user_id = uuid4()

    fake_message = Mock(spec=Message)
    fake_message.id = fake_message_id
    fake_message.sender_id = str(fake_other_user_id)

    mock_tm = Mock()
    mock_message_repo = Mock()
    mock_message_repo.get_by_id.return_value = fake_message

    service = ChatService(mock_tm)
    service.message_repo = mock_message_repo

    # Act & Assert
    with pytest.raises(UnauthorizedMessageAccessError) as exc_info:
        service.delete_message(fake_message_id, fake_user_id)

    assert 'only delete your own messages' in str(exc_info.value)


@pytest.mark.unit
def test_get_attachment_service_success():
    """
    Tests the `get_attachment` method of ChatService.

    Scenario:
    - Given a valid attachment ID and authorized user
    - When the service retrieves the attachment
    - Then it should return the attachment details
    """
    # Arrange
    fake_attachment_id = uuid4()
    fake_user_id = uuid4()
    fake_conversation_id = uuid4()

    fake_message = Mock(spec=Message)
    fake_message.conversation_id = str(fake_conversation_id)

    fake_attachment = Mock(spec=MessageAttachment)
    fake_attachment.id = fake_attachment_id
    fake_attachment.message_id = str(uuid4())
    fake_attachment.file_name = 'document.pdf'
    fake_attachment.file_size = 1024000
    fake_attachment.file_type = 'application/pdf'
    fake_attachment.file_url = 'https://example.com/document.pdf'
    fake_attachment.public_id = 'chat/documents/doc123'
    fake_attachment.thumbnail_url = None
    fake_attachment.created_at = datetime.now(timezone.utc)
    fake_attachment.message = fake_message

    mock_tm = Mock()
    mock_attachment_repo = Mock()
    mock_conversation_repo = Mock()

    mock_attachment_repo.get_attachment_with_message.return_value = fake_attachment
    mock_conversation_repo.validate_user_participation.return_value = True

    service = ChatService(mock_tm)
    service.attachment_repo = mock_attachment_repo
    service.conversation_repo = mock_conversation_repo

    # Act
    result = service.get_attachment(fake_attachment_id, fake_user_id)

    # Assert
    mock_attachment_repo.get_attachment_with_message.assert_called_once_with(
        fake_attachment_id
    )
    mock_conversation_repo.validate_user_participation.assert_called_once()
    assert result is not None
    assert isinstance(result, MessageAttachmentResponse)


@pytest.mark.unit
def test_get_attachment_service_not_found_error():
    """
    Tests the `get_attachment` method when attachment doesn't exist.

    Scenario:
    - Given an invalid attachment ID
    - When the service tries to retrieve it
    - Then it should raise FileNotFoundError
    """
    # Arrange
    fake_attachment_id = uuid4()
    fake_user_id = uuid4()

    mock_tm = Mock()
    mock_attachment_repo = Mock()
    mock_attachment_repo.get_attachment_with_message.return_value = None

    service = ChatService(mock_tm)
    service.attachment_repo = mock_attachment_repo

    # Act & Assert
    with pytest.raises(FileNotFoundError) as exc_info:
        service.get_attachment(fake_attachment_id, fake_user_id)

    assert 'Attachment not found' in str(exc_info.value)


@pytest.mark.unit
@patch('app.api.chat.service.cloudinary_uploader')
def test_delete_attachment_service_success(mock_cloudinary):
    """
    Tests the `delete_attachment` method of ChatService.

    Scenario:
    - Given an attachment owned by the user
    - When the user deletes the attachment
    - Then it should remove the file from cloudinary and database
    """
    # Arrange
    fake_attachment_id = uuid4()
    fake_user_id = uuid4()

    fake_message = Mock(spec=Message)
    fake_message.sender_id = str(fake_user_id)

    fake_attachment = Mock(spec=MessageAttachment)
    fake_attachment.id = fake_attachment_id
    fake_attachment.public_id = 'chat/images/image123'
    fake_attachment.message = fake_message

    mock_cloudinary.destroy.return_value = {'result': 'ok'}

    mock_tm = Mock()
    mock_attachment_repo = Mock()

    mock_attachment_repo.get_attachment_with_message.return_value = fake_attachment
    mock_attachment_repo.delete_attachment.return_value = True

    service = ChatService(mock_tm)
    service.attachment_repo = mock_attachment_repo

    # Act
    result = service.delete_attachment(fake_attachment_id, fake_user_id)

    # Assert
    mock_attachment_repo.get_attachment_with_message.assert_called_once_with(
        fake_attachment_id
    )
    mock_attachment_repo.delete_attachment.assert_called_once_with(fake_attachment_id)
    assert result is True


@pytest.mark.unit
def test_delete_attachment_service_not_sender_error():
    """
    Tests the `delete_attachment` method when user is not the message sender.

    Scenario:
    - Given an attachment from another user's message
    - When the user tries to delete it
    - Then it should raise UnauthorizedMessageAccessError
    """
    # Arrange
    fake_attachment_id = uuid4()
    fake_user_id = uuid4()
    fake_other_user_id = uuid4()

    fake_message = Mock(spec=Message)
    fake_message.sender_id = str(fake_other_user_id)

    fake_attachment = Mock(spec=MessageAttachment)
    fake_attachment.id = fake_attachment_id
    fake_attachment.message = fake_message

    mock_tm = Mock()
    mock_attachment_repo = Mock()
    mock_attachment_repo.get_attachment_with_message.return_value = fake_attachment

    service = ChatService(mock_tm)
    service.attachment_repo = mock_attachment_repo

    # Act & Assert
    with pytest.raises(UnauthorizedMessageAccessError) as exc_info:
        service.delete_attachment(fake_attachment_id, fake_user_id)

    assert 'only delete attachments from your own messages' in str(exc_info.value)


@pytest.mark.unit
def test_bulk_mark_messages_as_read_service_success():
    """
    Tests the `bulk_mark_messages_as_read` method of ChatService.

    Scenario:
    - Given a list of message IDs
    - When the user marks them all as read
    - Then it should update all messages and return count
    """
    # Arrange
    fake_user_id = uuid4()
    fake_conversation_id = uuid4()
    fake_message_ids = [uuid4(), uuid4(), uuid4()]
    fake_updated_count = 3

    # Create fake messages with proper UUIDs
    fake_messages = []
    for msg_id in fake_message_ids:
        fake_message = Mock(spec=Message)
        fake_message.id = msg_id
        fake_message.conversation_id = str(fake_conversation_id)
        fake_message.sender_id = str(uuid4())
        fake_messages.append(fake_message)

    mock_tm = Mock()
    mock_message_repo = Mock()
    mock_conversation_repo = Mock()

    # Mock get_by_id to return the appropriate message for each ID
    mock_message_repo.get_by_id.side_effect = fake_messages
    mock_conversation_repo.validate_user_participation.return_value = True
    mock_message_repo.bulk_mark_as_read.return_value = fake_updated_count

    service = ChatService(mock_tm)
    service.message_repo = mock_message_repo
    service.conversation_repo = mock_conversation_repo

    # Act
    result = service.bulk_mark_messages_as_read(fake_message_ids, fake_user_id)

    # Assert
    assert mock_message_repo.get_by_id.call_count == len(fake_message_ids)
    assert mock_conversation_repo.validate_user_participation.call_count == len(
        fake_message_ids
    )
    mock_message_repo.bulk_mark_as_read.assert_called_once_with(
        fake_message_ids, fake_user_id
    )
    assert result == fake_updated_count


@pytest.mark.unit
def test_bulk_mark_messages_as_read_service_empty_list():
    """
    Tests the `bulk_mark_messages_as_read` method with empty list.

    Scenario:
    - Given an empty list of message IDs
    - When the service is called
    - Then it should return 0 without calling repository
    """
    # Arrange
    fake_user_id = uuid4()
    fake_message_ids = []

    mock_tm = Mock()
    mock_message_repo = Mock()

    service = ChatService(mock_tm)
    service.message_repo = mock_message_repo

    # Act
    result = service.bulk_mark_messages_as_read(fake_message_ids, fake_user_id)

    # Assert
    mock_message_repo.bulk_mark_as_read.assert_not_called()
    assert result == 0
