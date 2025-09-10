import uuid
from datetime import datetime

import pytest
from pydantic import ValidationError

from app.api.comment.schema import (
    CommentAuthor,
    CommentCreate,
    CommentLikeResponse,
    CommentResponse,
    CommentStatusEnum,
    CommentUpdate,
    PostRelated,
)
from app.api.communities.schema import CommunityMemberRoleEnum


def test_comment_create_schema():
    post_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())

    comment = CommentCreate(
        post_id=post_id,
        user_id=user_id,
        content='Este é um comentário de teste',
        parent_id=None,
        status=CommentStatusEnum.ACTIVE,
    )

    assert comment.model_dump() == {
        'post_id': post_id,
        'user_id': user_id,
        'content': 'Este é um comentário de teste',
        'parent_id': None,
        'status': 'active',
    }


def test_comment_create_with_parent_schema():
    post_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())
    parent_id = str(uuid.uuid4())

    comment = CommentCreate(
        post_id=post_id,
        user_id=user_id,
        content='Esta é uma resposta',
        parent_id=parent_id,
        status=CommentStatusEnum.ACTIVE,
    )

    assert comment.model_dump() == {
        'post_id': post_id,
        'user_id': user_id,
        'content': 'Esta é uma resposta',
        'parent_id': parent_id,
        'status': 'active',
    }


def test_comment_update_schema():
    comment = CommentUpdate(
        content='Conteúdo atualizado',
        status=CommentStatusEnum.SUSPENDED,
    )

    assert comment.model_dump() == {
        'content': 'Conteúdo atualizado',
        'status': 'suspended',
    }


def test_comment_update_partial_schema():
    comment = CommentUpdate(
        content='Apenas conteúdo atualizado',
    )

    assert comment.model_dump() == {
        'content': 'Apenas conteúdo atualizado',
        'status': None,
    }


def test_comment_update_status_only_schema():
    comment = CommentUpdate(
        status=CommentStatusEnum.REPORTED,
    )

    assert comment.model_dump() == {
        'content': None,
        'status': 'reported',
    }


def test_comment_author_schema():
    user_id = uuid.uuid4()

    author = CommentAuthor(
        id=user_id,
        name='João Silva',
        profile_image_url='https://example.com/profile.jpg',
        member_role=CommunityMemberRoleEnum.MEMBER,
    )

    assert author.model_dump() == {
        'id': user_id,
        'name': 'João Silva',
        'profile_image_url': 'https://example.com/profile.jpg',
        'member_role': 'member',
    }


def test_comment_author_with_admin_role_schema():
    user_id = uuid.uuid4()

    author = CommentAuthor(
        id=user_id,
        name='Admin User',
        profile_image_url='https://example.com/admin.jpg',
        member_role=CommunityMemberRoleEnum.ADMIN,
    )

    assert author.model_dump() == {
        'id': user_id,
        'name': 'Admin User',
        'profile_image_url': 'https://example.com/admin.jpg',
        'member_role': 'admin',
    }


def test_comment_author_with_moderator_role_schema():
    user_id = uuid.uuid4()

    author = CommentAuthor(
        id=user_id,
        name='Moderator User',
        profile_image_url=None,
        member_role=CommunityMemberRoleEnum.MODERATOR,
    )

    assert author.model_dump() == {
        'id': user_id,
        'name': 'Moderator User',
        'profile_image_url': None,
        'member_role': 'moderator',
    }


def test_comment_author_without_profile_image_schema():
    user_id = uuid.uuid4()

    author = CommentAuthor(
        id=user_id,
        name='Maria Santos',
        profile_image_url=None,
        member_role=CommunityMemberRoleEnum.MEMBER,
    )

    assert author.model_dump() == {
        'id': user_id,
        'name': 'Maria Santos',
        'profile_image_url': None,
        'member_role': 'member',
    }


def test_comment_author_without_member_role_schema():
    user_id = uuid.uuid4()

    author = CommentAuthor(
        id=user_id,
        name='Guest User',
        profile_image_url=None,
        member_role=None,
    )

    assert author.model_dump() == {
        'id': user_id,
        'name': 'Guest User',
        'profile_image_url': None,
        'member_role': None,
    }


def test_post_related_schema():
    post_id = uuid.uuid4()

    post = PostRelated(
        id=post_id,
        title='Título do Post',
    )

    assert post.model_dump() == {
        'id': post_id,
        'title': 'Título do Post',
    }


def test_comment_response_schema():
    comment_id = uuid.uuid4()
    post_id = uuid.uuid4()
    user_id = uuid.uuid4()
    created_at = datetime.now()

    post = PostRelated(
        id=post_id,
        title='Título do Post',
    )

    author = CommentAuthor(
        id=user_id,
        name='João Silva',
        profile_image_url='https://example.com/profile.jpg',
        member_role=CommunityMemberRoleEnum.MEMBER,
    )

    comment = CommentResponse(
        id=comment_id,
        post=post,
        user=author,
        content='Este é um comentário de teste',
        status=CommentStatusEnum.ACTIVE,
        likes_count=5,
        report_count=0,
        parent_id=None,
        created_at=created_at,
        replies=[],
    )

    assert comment.model_dump() == {
        'id': comment_id,
        'post': {
            'id': post_id,
            'title': 'Título do Post',
        },
        'user': {
            'id': user_id,
            'name': 'João Silva',
            'profile_image_url': 'https://example.com/profile.jpg',
            'member_role': 'member',
        },
        'content': 'Este é um comentário de teste',
        'status': 'active',
        'likes_count': 5,
        'report_count': 0,
        'parent_id': None,
        'created_at': created_at,
        'replies': [],
    }


def test_comment_response_with_replies_schema():
    comment_id = uuid.uuid4()
    reply_id = uuid.uuid4()
    post_id = uuid.uuid4()
    user_id = uuid.uuid4()
    reply_user_id = uuid.uuid4()
    created_at = datetime.now()
    reply_created_at = datetime.now()

    post = PostRelated(
        id=post_id,
        title='Título do Post',
    )

    author = CommentAuthor(
        id=user_id,
        name='João Silva',
        profile_image_url='https://example.com/profile.jpg',
        member_role=CommunityMemberRoleEnum.ADMIN,
    )

    reply_author = CommentAuthor(
        id=reply_user_id,
        name='Maria Santos',
        profile_image_url=None,
        member_role=CommunityMemberRoleEnum.MODERATOR,
    )

    reply = CommentResponse(
        id=reply_id,
        post=post,
        user=reply_author,
        content='Esta é uma resposta',
        status=CommentStatusEnum.ACTIVE,
        likes_count=2,
        report_count=0,
        parent_id=comment_id,
        created_at=reply_created_at,
        replies=[],
    )

    comment = CommentResponse(
        id=comment_id,
        post=post,
        user=author,
        content='Este é um comentário de teste',
        status=CommentStatusEnum.ACTIVE,
        likes_count=5,
        report_count=0,
        parent_id=None,
        created_at=created_at,
        replies=[reply],
    )

    assert comment.model_dump() == {
        'id': comment_id,
        'post': {
            'id': post_id,
            'title': 'Título do Post',
        },
        'user': {
            'id': user_id,
            'name': 'João Silva',
            'profile_image_url': 'https://example.com/profile.jpg',
            'member_role': 'admin',
        },
        'content': 'Este é um comentário de teste',
        'status': 'active',
        'likes_count': 5,
        'report_count': 0,
        'parent_id': None,
        'created_at': created_at,
        'replies': [
            {
                'id': reply_id,
                'post': {
                    'id': post_id,
                    'title': 'Título do Post',
                },
                'user': {
                    'id': reply_user_id,
                    'name': 'Maria Santos',
                    'profile_image_url': None,
                    'member_role': 'moderator',
                },
                'content': 'Esta é uma resposta',
                'status': CommentStatusEnum.ACTIVE,
                'likes_count': 2,
                'report_count': 0,
                'parent_id': comment_id,
                'created_at': reply_created_at,
                'replies': [],
            }
        ],
    }


def test_comment_like_response_schema():
    comment_id = uuid.uuid4()
    user_id = uuid.uuid4()
    created_at = datetime.now()

    comment_like = CommentLikeResponse(
        comment_id=comment_id,
        user_id=user_id,
        created_at=created_at,
    )

    assert comment_like.model_dump() == {
        'comment_id': comment_id,
        'user_id': user_id,
        'created_at': created_at,
    }


def test_comment_create_invalid_schema():
    with pytest.raises(ValidationError):
        CommentCreate(
            post_id=str(uuid.uuid4()),
            user_id=str(uuid.uuid4()),
            content='',
            parent_id=None,
            status=CommentStatusEnum.ACTIVE,
        )


def test_comment_create_content_too_long_invalid_schema():
    with pytest.raises(ValidationError):
        CommentCreate(
            post_id=str(uuid.uuid4()),
            user_id=str(uuid.uuid4()),
            content='a' * 1001,
            parent_id=None,
            status=CommentStatusEnum.ACTIVE,
        )


def test_comment_update_invalid_schema():
    with pytest.raises(ValidationError):
        CommentUpdate(
            content='',
            status=CommentStatusEnum.ACTIVE,
        )


def test_comment_update_content_too_long_invalid_schema():
    with pytest.raises(ValidationError):
        CommentUpdate(
            content='a' * 1001,
            status=CommentStatusEnum.ACTIVE,
        )


def test_comment_author_invalid_schema():
    with pytest.raises(ValidationError):
        CommentAuthor(
            id=uuid.uuid4(),
            name='',
            profile_image_url=None,
            member_role=CommunityMemberRoleEnum.MEMBER,
        )

    with pytest.raises(ValidationError):
        CommentAuthor(
            id=uuid.uuid4(),
            name='a' * 256,
            profile_image_url=None,
            member_role=CommunityMemberRoleEnum.MEMBER,
        )


def test_post_related_invalid_schema():
    with pytest.raises(ValidationError):
        PostRelated(
            id=uuid.uuid4(),
            title='',
        )

    with pytest.raises(ValidationError):
        PostRelated(
            id=uuid.uuid4(),
            title='a' * 256,
        )


def test_comment_response_invalid_schema():
    with pytest.raises(ValidationError):
        CommentResponse(
            id=uuid.uuid4(),
            post=PostRelated(id=uuid.uuid4(), title=''),
            user=CommentAuthor(
                id=uuid.uuid4(),
                name='João Silva',
                profile_image_url=None,
                member_role=CommunityMemberRoleEnum.MEMBER,
            ),
            content='Conteúdo válido',
            status=CommentStatusEnum.ACTIVE,
            likes_count=0,
            report_count=0,
            parent_id=None,
            created_at=datetime.now(),
            replies=[],
        )


def test_comment_status_enum_values():
    assert CommentStatusEnum.ACTIVE == 'active'
    assert CommentStatusEnum.REPORTED == 'reported'
    assert CommentStatusEnum.SUSPENDED == 'suspended'


def test_community_member_role_enum_values():
    assert CommunityMemberRoleEnum.ADMIN == 'admin'
    assert CommunityMemberRoleEnum.MODERATOR == 'moderator'
    assert CommunityMemberRoleEnum.MEMBER == 'member'
