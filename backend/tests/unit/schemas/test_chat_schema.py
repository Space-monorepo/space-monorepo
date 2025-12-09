import uuid
from datetime import datetime

import pytest
from pydantic import ValidationError

from app.api.chat.schema import (
    ConversationCreate,
    ConversationParticipant,
    ConversationResponse,
    MessageAttachmentCreate,
    MessageAttachmentResponse,
    MessageCreate,
    MessageResponse,
    MessageTypeEnum,
    MessageUpdate,
    MessageWithAttachmentCreate,
    UnreadCountResponse,
)


@pytest.mark.unit
def test_message_type_enum_values():
    assert MessageTypeEnum.text.value == 'text'
    assert MessageTypeEnum.image.value == 'image'
    assert MessageTypeEnum.document.value == 'document'
    assert MessageTypeEnum.audio.value == 'audio'
    assert MessageTypeEnum.video.value == 'video'
    assert MessageTypeEnum.system.value == 'system'


@pytest.mark.unit
def test_conversation_participant_schema():
    user_id = uuid.uuid4()

    participant = ConversationParticipant(
        id=user_id,
        name='John Doe',
        profile_image_url='https://example.com/profile.jpg',
    )

    assert participant.model_dump() == {
        'id': user_id,
        'name': 'John Doe',
        'profile_image_url': 'https://example.com/profile.jpg',
    }


@pytest.mark.unit
def test_conversation_participant_schema_without_profile_image():
    user_id = uuid.uuid4()

    participant = ConversationParticipant(
        id=user_id,
        name='Jane Smith',
        profile_image_url=None,
    )

    assert participant.model_dump() == {
        'id': user_id,
        'name': 'Jane Smith',
        'profile_image_url': None,
    }


@pytest.mark.unit
def test_conversation_participant_invalid_schema():
    with pytest.raises(ValidationError):
        ConversationParticipant(
            id=uuid.uuid4(),
            profile_image_url=None,
        )

    with pytest.raises(ValidationError):
        ConversationParticipant(
            name='John Doe',
            profile_image_url=None,
        )


@pytest.mark.unit
def test_message_attachment_create_schema():
    attachment = MessageAttachmentCreate(
        file_name='document.pdf',
        file_size=1024000,
        file_type='application/pdf',
        file_url='https://res.cloudinary.com/demo/document.pdf',
        public_id='chat/documents/doc123',
        thumbnail_url='https://res.cloudinary.com/demo/thumbnail.jpg',
    )

    assert attachment.model_dump() == {
        'file_name': 'document.pdf',
        'file_size': 1024000,
        'file_type': 'application/pdf',
        'file_url': 'https://res.cloudinary.com/demo/document.pdf',
        'public_id': 'chat/documents/doc123',
        'thumbnail_url': 'https://res.cloudinary.com/demo/thumbnail.jpg',
    }


@pytest.mark.unit
def test_message_attachment_create_schema_without_optionals():
    attachment = MessageAttachmentCreate(
        file_name='image.jpg',
        file_size=2048,
        file_type='image/jpeg',
        file_url='https://example.com/image.jpg',
    )

    assert attachment.model_dump() == {
        'file_name': 'image.jpg',
        'file_size': 2048,
        'file_type': 'image/jpeg',
        'file_url': 'https://example.com/image.jpg',
        'public_id': None,
        'thumbnail_url': None,
    }


@pytest.mark.unit
def test_message_attachment_create_invalid_schema():
    with pytest.raises(ValidationError):
        MessageAttachmentCreate(
            file_name='',
            file_size=1024,
            file_type='image/jpeg',
            file_url='https://example.com/image.jpg',
        )

    with pytest.raises(ValidationError):
        MessageAttachmentCreate(
            file_name='test.jpg',
            file_size=0,
            file_type='image/jpeg',
            file_url='https://example.com/image.jpg',
        )

    with pytest.raises(ValidationError):
        MessageAttachmentCreate(
            file_name='test.jpg',
            file_size=1024,
            file_type='',
            file_url='https://example.com/image.jpg',
        )

    with pytest.raises(ValidationError):
        MessageAttachmentCreate(
            file_name='test.jpg',
            file_size=1024,
            file_type='image/jpeg',
            file_url='',
        )


@pytest.mark.unit
def test_message_attachment_response_schema():
    attachment_id = uuid.uuid4()
    message_id = uuid.uuid4()
    created_at = datetime.now()

    attachment = MessageAttachmentResponse(
        id=attachment_id,
        message_id=message_id,
        file_name='presentation.pptx',
        file_size=5242880,
        file_type='application/vnd.ms-powerpoint',
        file_url='https://res.cloudinary.com/demo/presentation.pptx',
        public_id='chat/documents/presentation123',
        thumbnail_url='https://res.cloudinary.com/demo/thumb.jpg',
        created_at=created_at,
    )

    assert attachment.model_dump() == {
        'id': attachment_id,
        'message_id': message_id,
        'file_name': 'presentation.pptx',
        'file_size': 5242880,
        'file_type': 'application/vnd.ms-powerpoint',
        'file_url': 'https://res.cloudinary.com/demo/presentation.pptx',
        'public_id': 'chat/documents/presentation123',
        'thumbnail_url': 'https://res.cloudinary.com/demo/thumb.jpg',
        'created_at': created_at,
    }


@pytest.mark.unit
def test_message_create_schema_text():
    message = MessageCreate(
        content='Hello, how are you?',
        message_type=MessageTypeEnum.text,
        reply_to_message_id=None,
    )

    assert message.model_dump() == {
        'content': 'Hello, how are you?',
        'message_type': MessageTypeEnum.text,
        'reply_to_message_id': None,
    }


@pytest.mark.unit
def test_message_create_schema_with_reply():
    reply_to_id = uuid.uuid4()

    message = MessageCreate(
        content='Thanks for the message!',
        message_type=MessageTypeEnum.text,
        reply_to_message_id=reply_to_id,
    )

    assert message.model_dump() == {
        'content': 'Thanks for the message!',
        'message_type': MessageTypeEnum.text,
        'reply_to_message_id': reply_to_id,
    }


@pytest.mark.unit
def test_message_create_schema_non_text_type():
    message = MessageCreate(
        content='Check out this image!',
        message_type=MessageTypeEnum.image,
        reply_to_message_id=None,
    )

    assert message.model_dump() == {
        'content': 'Check out this image!',
        'message_type': MessageTypeEnum.image,
        'reply_to_message_id': None,
    }


@pytest.mark.unit
def test_message_create_invalid_text_message():
    with pytest.raises(ValidationError):
        MessageCreate(
            content='',
            message_type=MessageTypeEnum.text,
        )

    with pytest.raises(ValidationError):
        MessageCreate(
            content=None,
            message_type=MessageTypeEnum.text,
        )

    with pytest.raises(ValidationError):
        MessageCreate(
            content='   ',
            message_type=MessageTypeEnum.text,
        )


@pytest.mark.unit
def test_message_create_content_max_length():
    message = MessageCreate(
        content='a' * 2000,
        message_type=MessageTypeEnum.text,
    )
    assert len(message.content) == 2000

    with pytest.raises(ValidationError):
        MessageCreate(
            content='a' * 2001,
            message_type=MessageTypeEnum.text,
        )


@pytest.mark.unit
def test_message_with_attachment_create_schema():
    message = MessageWithAttachmentCreate(
        message_type=MessageTypeEnum.image,
        content='Check out this photo!',
        reply_to_message_id=None,
    )

    assert message.model_dump() == {
        'message_type': MessageTypeEnum.image,
        'content': 'Check out this photo!',
        'reply_to_message_id': None,
    }


@pytest.mark.unit
def test_message_with_attachment_create_schema_without_content():
    message = MessageWithAttachmentCreate(
        message_type=MessageTypeEnum.document,
        content=None,
        reply_to_message_id=None,
    )

    assert message.model_dump() == {
        'message_type': MessageTypeEnum.document,
        'content': None,
        'reply_to_message_id': None,
    }


@pytest.mark.unit
def test_message_with_attachment_create_invalid_text_type():
    with pytest.raises(ValidationError):
        MessageWithAttachmentCreate(
            message_type=MessageTypeEnum.text,
            content='This should fail',
        )


@pytest.mark.unit
def test_message_update_schema():
    update = MessageUpdate(is_read=True)
    assert update.model_dump() == {'is_read': True}

    update = MessageUpdate(is_read=False)
    assert update.model_dump() == {'is_read': False}


@pytest.mark.unit
def test_message_response_schema_simple():
    message_id = uuid.uuid4()
    conversation_id = uuid.uuid4()
    sender_id = uuid.uuid4()
    created_at = datetime.now()

    sender = ConversationParticipant(
        id=sender_id,
        name='Alice Johnson',
        profile_image_url='https://example.com/alice.jpg',
    )

    message = MessageResponse(
        id=message_id,
        conversation_id=conversation_id,
        sender_id=sender_id,
        content='Hello there!',
        message_type=MessageTypeEnum.text,
        created_at=created_at,
        is_read=False,
        reply_to_message_id=None,
        sender=sender,
        reply_to_message=None,
        attachments=[],
    )

    result = message.model_dump()
    assert result['id'] == message_id
    assert result['conversation_id'] == conversation_id
    assert result['sender_id'] == sender_id
    assert result['content'] == 'Hello there!'
    assert result['message_type'] == 'text'
    assert result['created_at'] == created_at
    assert result['is_read'] is False
    assert result['reply_to_message_id'] is None
    assert result['sender']['id'] == sender_id
    assert result['sender']['name'] == 'Alice Johnson'
    assert result['attachments'] == []


@pytest.mark.unit
def test_message_response_schema_with_attachment():
    message_id = uuid.uuid4()
    conversation_id = uuid.uuid4()
    sender_id = uuid.uuid4()
    attachment_id = uuid.uuid4()
    created_at = datetime.now()

    sender = ConversationParticipant(
        id=sender_id,
        name='Bob Smith',
        profile_image_url=None,
    )

    attachment = MessageAttachmentResponse(
        id=attachment_id,
        message_id=message_id,
        file_name='photo.jpg',
        file_size=2048000,
        file_type='image/jpeg',
        file_url='https://example.com/photo.jpg',
        public_id='chat/images/photo123',
        thumbnail_url='https://example.com/photo_thumb.jpg',
        created_at=created_at,
    )

    message = MessageResponse(
        id=message_id,
        conversation_id=conversation_id,
        sender_id=sender_id,
        content='Look at this!',
        message_type=MessageTypeEnum.image,
        created_at=created_at,
        is_read=True,
        reply_to_message_id=None,
        sender=sender,
        reply_to_message=None,
        attachments=[attachment],
    )

    result = message.model_dump()
    assert result['message_type'] == 'image'
    assert len(result['attachments']) == 1
    assert result['attachments'][0]['file_name'] == 'photo.jpg'
    assert result['attachments'][0]['file_type'] == 'image/jpeg'


@pytest.mark.unit
def test_message_response_schema_with_reply():
    message_id = uuid.uuid4()
    original_message_id = uuid.uuid4()
    conversation_id = uuid.uuid4()
    sender_id = uuid.uuid4()
    original_sender_id = uuid.uuid4()
    created_at = datetime.now()

    sender = ConversationParticipant(
        id=sender_id,
        name='Charlie Brown',
        profile_image_url='https://example.com/charlie.jpg',
    )

    original_sender = ConversationParticipant(
        id=original_sender_id,
        name='Lucy van Pelt',
        profile_image_url='https://example.com/lucy.jpg',
    )

    original_message = MessageResponse(
        id=original_message_id,
        conversation_id=conversation_id,
        sender_id=original_sender_id,
        content='Are you free tomorrow?',
        message_type=MessageTypeEnum.text,
        created_at=created_at,
        is_read=True,
        reply_to_message_id=None,
        sender=original_sender,
        reply_to_message=None,
        attachments=[],
    )

    reply_message = MessageResponse(
        id=message_id,
        conversation_id=conversation_id,
        sender_id=sender_id,
        content='Yes, I am!',
        message_type=MessageTypeEnum.text,
        created_at=created_at,
        is_read=False,
        reply_to_message_id=original_message_id,
        sender=sender,
        reply_to_message=original_message,
        attachments=[],
    )

    result = reply_message.model_dump()
    assert result['reply_to_message_id'] == original_message_id
    assert result['reply_to_message'] is not None
    assert result['reply_to_message']['content'] == 'Are you free tomorrow?'
    assert result['reply_to_message']['sender']['name'] == 'Lucy van Pelt'


@pytest.mark.unit
def test_conversation_create_schema():
    participant_id = uuid.uuid4()

    conversation = ConversationCreate(participant_user_id=participant_id)

    assert conversation.model_dump() == {
        'participant_user_id': participant_id,
    }


@pytest.mark.unit
def test_conversation_create_invalid_schema():
    with pytest.raises(ValidationError):
        ConversationCreate(participant_user_id='not-a-uuid')


@pytest.mark.unit
def test_conversation_response_schema():
    conversation_id = uuid.uuid4()
    user1_id = uuid.uuid4()
    user2_id = uuid.uuid4()
    message_id = uuid.uuid4()
    created_at = datetime.now()
    updated_at = datetime.now()

    user1 = ConversationParticipant(
        id=user1_id,
        name='John Doe',
        profile_image_url='https://example.com/john.jpg',
    )

    user2 = ConversationParticipant(
        id=user2_id,
        name='Jane Smith',
        profile_image_url='https://example.com/jane.jpg',
    )

    last_message = MessageResponse(
        id=message_id,
        conversation_id=conversation_id,
        sender_id=user2_id,
        content='See you tomorrow!',
        message_type=MessageTypeEnum.text,
        created_at=created_at,
        is_read=False,
        reply_to_message_id=None,
        sender=user2,
        reply_to_message=None,
        attachments=[],
    )

    conversation = ConversationResponse(
        id=conversation_id,
        user1_id=user1_id,
        user2_id=user2_id,
        created_at=created_at,
        updated_at=updated_at,
        last_message_id=message_id,
        user1=user1,
        user2=user2,
        last_message=last_message,
        unread_count=3,
        other_participant=user2,
    )

    result = conversation.model_dump()
    assert result['id'] == conversation_id
    assert result['user1_id'] == user1_id
    assert result['user2_id'] == user2_id
    assert result['created_at'] == created_at
    assert result['updated_at'] == updated_at
    assert result['last_message_id'] == message_id
    assert result['user1']['name'] == 'John Doe'
    assert result['user2']['name'] == 'Jane Smith'
    assert result['last_message']['content'] == 'See you tomorrow!'
    assert result['unread_count'] == 3
    assert result['other_participant']['name'] == 'Jane Smith'


@pytest.mark.unit
def test_conversation_response_schema_without_last_message():
    conversation_id = uuid.uuid4()
    user1_id = uuid.uuid4()
    user2_id = uuid.uuid4()
    created_at = datetime.now()
    updated_at = datetime.now()

    user1 = ConversationParticipant(
        id=user1_id,
        name='Alice',
        profile_image_url=None,
    )

    user2 = ConversationParticipant(
        id=user2_id,
        name='Bob',
        profile_image_url=None,
    )

    conversation = ConversationResponse(
        id=conversation_id,
        user1_id=user1_id,
        user2_id=user2_id,
        created_at=created_at,
        updated_at=updated_at,
        last_message_id=None,
        user1=user1,
        user2=user2,
        last_message=None,
        unread_count=0,
        other_participant=user2,
    )

    result = conversation.model_dump()
    assert result['last_message_id'] is None
    assert result['last_message'] is None
    assert result['unread_count'] == 0


@pytest.mark.unit
def test_unread_count_response_schema():
    response = UnreadCountResponse(unread_count=5)
    assert response.model_dump() == {'unread_count': 5}

    response = UnreadCountResponse(unread_count=0)
    assert response.model_dump() == {'unread_count': 0}


@pytest.mark.unit
def test_unread_count_response_invalid_schema():
    with pytest.raises(ValidationError):
        UnreadCountResponse(unread_count=-1)


@pytest.mark.unit
def test_message_response_system_type():
    message_id = uuid.uuid4()
    conversation_id = uuid.uuid4()
    sender_id = uuid.uuid4()
    created_at = datetime.now()

    sender = ConversationParticipant(
        id=sender_id,
        name='System',
        profile_image_url=None,
    )

    message = MessageResponse(
        id=message_id,
        conversation_id=conversation_id,
        sender_id=sender_id,
        content='User joined the conversation',
        message_type=MessageTypeEnum.system,
        created_at=created_at,
        is_read=True,
        reply_to_message_id=None,
        sender=sender,
        reply_to_message=None,
        attachments=[],
    )

    result = message.model_dump()
    assert result['message_type'] == 'system'
    assert result['content'] == 'User joined the conversation'


@pytest.mark.unit
def test_message_response_all_attachment_types():
    message_id = uuid.uuid4()
    conversation_id = uuid.uuid4()
    sender_id = uuid.uuid4()
    created_at = datetime.now()

    sender = ConversationParticipant(
        id=sender_id,
        name='Test User',
        profile_image_url='https://example.com/user.jpg',
    )

    video_message = MessageResponse(
        id=message_id,
        conversation_id=conversation_id,
        sender_id=sender_id,
        content=None,
        message_type=MessageTypeEnum.video,
        created_at=created_at,
        is_read=False,
        reply_to_message_id=None,
        sender=sender,
        reply_to_message=None,
        attachments=[],
    )
    assert video_message.model_dump()['message_type'] == 'video'

    audio_message = MessageResponse(
        id=message_id,
        conversation_id=conversation_id,
        sender_id=sender_id,
        content=None,
        message_type=MessageTypeEnum.audio,
        created_at=created_at,
        is_read=False,
        reply_to_message_id=None,
        sender=sender,
        reply_to_message=None,
        attachments=[],
    )
    assert audio_message.model_dump()['message_type'] == 'audio'

    document_message = MessageResponse(
        id=message_id,
        conversation_id=conversation_id,
        sender_id=sender_id,
        content=None,
        message_type=MessageTypeEnum.document,
        created_at=created_at,
        is_read=False,
        reply_to_message_id=None,
        sender=sender,
        reply_to_message=None,
        attachments=[],
    )
    assert document_message.model_dump()['message_type'] == 'document'


@pytest.mark.unit
def test_message_response_multiple_attachments():
    message_id = uuid.uuid4()
    conversation_id = uuid.uuid4()
    sender_id = uuid.uuid4()
    created_at = datetime.now()

    sender = ConversationParticipant(
        id=sender_id,
        name='Multi Sender',
        profile_image_url=None,
    )

    attachments = [
        MessageAttachmentResponse(
            id=uuid.uuid4(),
            message_id=message_id,
            file_name=f'file{i}.jpg',
            file_size=1024 * (i + 1),
            file_type='image/jpeg',
            file_url=f'https://example.com/file{i}.jpg',
            public_id=f'chat/images/file{i}',
            thumbnail_url=f'https://example.com/file{i}_thumb.jpg',
            created_at=created_at,
        )
        for i in range(3)
    ]

    message = MessageResponse(
        id=message_id,
        conversation_id=conversation_id,
        sender_id=sender_id,
        content='Multiple files',
        message_type=MessageTypeEnum.image,
        created_at=created_at,
        is_read=False,
        reply_to_message_id=None,
        sender=sender,
        reply_to_message=None,
        attachments=attachments,
    )

    result = message.model_dump()
    assert len(result['attachments']) == 3
    assert result['attachments'][0]['file_name'] == 'file0.jpg'
    assert result['attachments'][1]['file_name'] == 'file1.jpg'
    assert result['attachments'][2]['file_name'] == 'file2.jpg'
