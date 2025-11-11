import uuid

import pytest
from fastapi import status

from app.api.comment.model import Comment, CommentLikes
from app.api.comment.schema import (
    CommentCreate,
    CommentStatusEnum,
    CommentUpdate,
)


@pytest.mark.integration
def test_create_comment_route(authenticate_client, community_member_on_db, post_on_db):
    comment = CommentCreate(
        post_id=str(post_on_db.id),
        member_id=str(community_member_on_db.id),
        content='Este é um comentário de teste via rota',
        parent_id=None,
        status=CommentStatusEnum.ACTIVE,
    )

    response = authenticate_client.post(
        f'/comments/{community_member_on_db.community_id}/post/{post_on_db.id}/create-comment',
        json=comment.model_dump(mode='json'),
    )
    response_data = response.json()
    assert response.status_code == status.HTTP_201_CREATED
    assert response_data['content'] == comment.content
    assert response_data['member']['id'] == str(comment.member_id)
    assert response_data['post']['id'] == str(comment.post_id)
    assert response_data['status'] == comment.status
    assert response_data['likes_count'] == 0
    assert response_data['report_count'] == 0
    assert response_data['parent_id'] is None


@pytest.mark.integration
def test_create_comment_reply_route(
    authenticate_client, community_member_on_db, comment_on_db
):
    reply = CommentCreate(
        post_id=str(comment_on_db.post_id),
        member_id=str(community_member_on_db.id),
        content='Esta é uma resposta via rota',
        parent_id=str(comment_on_db.id),
        status=CommentStatusEnum.ACTIVE,
    )

    response = authenticate_client.post(
        f'/comments/{community_member_on_db.community_id}/post/{comment_on_db.post_id}/create-comment',
        json=reply.model_dump(mode='json'),
    )
    response_data = response.json()
    assert response.status_code == status.HTTP_201_CREATED
    assert response_data['content'] == reply.content
    assert response_data['parent_id'] == str(comment_on_db.id)
    assert response_data['post']['id'] == str(comment_on_db.post_id)


@pytest.mark.integration
def test_get_comment_route(authenticate_client, comment_on_db, community_member_on_db):
    response = authenticate_client.get(
        f'/comments/{community_member_on_db.community_id}/post/{comment_on_db.post_id}/comment/{comment_on_db.id}'
    )
    response_data = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert response_data['id'] == str(comment_on_db.id)
    assert response_data['content'] == comment_on_db.content
    assert response_data['member']['id'] == str(comment_on_db.member_id)
    assert response_data['post']['id'] == str(comment_on_db.post_id)
    assert response_data['status'] == comment_on_db.status


@pytest.mark.integration
def test_list_comments_by_post_route(
    authenticate_client, comment_on_db, community_member_on_db
):
    response = authenticate_client.get(
        f'/comments/{community_member_on_db.community_id}/post/{comment_on_db.post_id}/list-comments'
    )
    response_data = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert len(response_data['items']) > 0
    assert response_data['items'][0]['post']['id'] == str(comment_on_db.post_id)
    assert response_data['total'] > 0


@pytest.mark.integration
def test_list_comments_by_user_route(
    authenticate_client, comment_on_db, community_member_on_db
):
    response = authenticate_client.get(
        f'/comments/{community_member_on_db.community_id}/user/{comment_on_db.member_id}/list-comments'
    )
    response_data = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert len(response_data['items']) > 0
    assert response_data['items'][0]['member']['id'] == str(comment_on_db.member_id)
    assert response_data['total'] > 0


@pytest.mark.integration
def test_list_replies_by_parent_route(
    authenticate_client, comment_reply_on_db, comment_on_db, community_member_on_db
):
    response = authenticate_client.get(
        f'/comments/{community_member_on_db.community_id}/comment/{comment_on_db.id}/list-replies'
    )
    response_data = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert len(response_data['items']) > 0
    assert response_data['items'][0]['parent_id'] == str(comment_on_db.id)
    assert response_data['total'] > 0


@pytest.mark.integration
def test_update_comment_content_route(
    authenticate_client, comment_on_db, community_member_on_db
):
    comment_update = CommentUpdate(
        content='Conteúdo atualizado via rota',
    )

    response = authenticate_client.patch(
        f'/comments/{community_member_on_db.community_id}/comment/{comment_on_db.id}',
        json=comment_update.model_dump(mode='json'),
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()['content'] == comment_update.content


@pytest.mark.integration
def test_update_comment_status_route(
    authenticate_client, comment_on_db, community_member_on_db
):
    comment_update = CommentUpdate(
        status=CommentStatusEnum.SUSPENDED,
    )

    response = authenticate_client.patch(
        f'/comments/{community_member_on_db.community_id}/comment/{comment_on_db.id}',
        json=comment_update.model_dump(mode='json'),
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()['status'] == comment_update.status


@pytest.mark.integration
def test_update_comment_status_from_not_admin_route(
    authenticate_member_client, comment_on_db, commun_member_on_db
):
    comment_update = CommentUpdate(
        status=CommentStatusEnum.SUSPENDED,
    )

    response = authenticate_member_client.patch(
        f'/comments/{commun_member_on_db.community_id}/comment/{comment_on_db.id}',
        json=comment_update.model_dump(mode='json'),
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.integration
def test_update_comment_from_not_owner_route(
    authenticate_member_client, comment_on_db, commun_member_on_db
):
    comment_update = CommentUpdate(
        content='Conteúdo atualizado por não proprietário',
    )

    response = authenticate_member_client.patch(
        f'/comments/{commun_member_on_db.community_id}/comment/{comment_on_db.id}',
        json=comment_update.model_dump(mode='json'),
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.integration
def test_delete_comment_route(
    authenticate_client, comment_on_db, community_member_on_db
):
    response = authenticate_client.delete(
        f'/comments/{community_member_on_db.community_id}/comment/{comment_on_db.id}'
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT

    response = authenticate_client.get(
        f'/comments/{community_member_on_db.community_id}/post/{comment_on_db.post_id}/comment/{comment_on_db.id}'
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.integration
def test_like_comment_route(authenticate_client, comment_on_db, community_member_on_db):
    initial_likes_count = comment_on_db.likes_count

    response = authenticate_client.post(
        f'/comments/{community_member_on_db.community_id}/comment/{comment_on_db.id}/like'
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['likes_count'] == initial_likes_count + 1


@pytest.mark.integration
def test_unlike_comment_route(
    session_sql, authenticate_client, comment_on_db, community_member_on_db
):
    initial_likes_count = comment_on_db.likes_count

    response = authenticate_client.post(
        f'/comments/{community_member_on_db.community_id}/comment/{comment_on_db.id}/like'
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['likes_count'] == initial_likes_count + 1

    response = authenticate_client.post(
        f'/comments/{community_member_on_db.community_id}/comment/{comment_on_db.id}/unlike'
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['likes_count'] == initial_likes_count

    like_db = (
        session_sql.query(CommentLikes)
        .filter(
            CommentLikes.comment_id == comment_on_db.id,
            CommentLikes.member_id == community_member_on_db.id,
        )
        .first()
    )
    assert like_db is None


@pytest.mark.integration
def test_list_likes_comment_route(
    authenticate_client, comment_on_db, community_member_on_db
):
    response = authenticate_client.post(
        f'/comments/{community_member_on_db.community_id}/comment/{comment_on_db.id}/like'
    )
    assert response.status_code == status.HTTP_200_OK

    response = authenticate_client.get(
        f'/comments/{community_member_on_db.community_id}/comment/{comment_on_db.id}/list-likes'
    )
    response_data = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert len(response_data) == 1
    assert response_data[0]['id'] == str(community_member_on_db.id)


@pytest.mark.integration
def test_report_comment_route(
    session_sql, authenticate_client, comment_on_db, community_member_on_db
):
    original_report_count = comment_on_db.report_count

    response = authenticate_client.patch(
        f'/comments/{community_member_on_db.community_id}/comment/{comment_on_db.id}/report'
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['report_count'] == original_report_count + 1

    comment_db = (
        session_sql.query(Comment).filter(Comment.id == comment_on_db.id).first()
    )
    assert comment_db.report_count == original_report_count + 1


@pytest.mark.integration
def test_create_comment_increments_post_comments_count_route(
    session_sql, authenticate_client, community_member_on_db, post_on_db
):
    from app.api.post.model import Post

    original_comments_count = post_on_db.comments_count

    comment = CommentCreate(
        post_id=str(post_on_db.id),
        member_id=str(community_member_on_db.id),
        content='Comentário que deve incrementar contador via rota',
        parent_id=None,
        status=CommentStatusEnum.ACTIVE,
    )

    response = authenticate_client.post(
        f'/comments/{community_member_on_db.community_id}/post/{post_on_db.id}/create-comment',
        json=comment.model_dump(mode='json'),
    )
    assert response.status_code == status.HTTP_201_CREATED

    post_db = session_sql.query(Post).filter(Post.id == post_on_db.id).first()
    assert post_db.comments_count == original_comments_count + 1


@pytest.mark.integration
def test_delete_comment_decrements_post_comments_count_route(
    session_sql, authenticate_client, comment_on_db, community_member_on_db, post_on_db
):
    from app.api.post.model import Post

    original_comments_count = post_on_db.comments_count

    response = authenticate_client.delete(
        f'/comments/{community_member_on_db.community_id}/comment/{comment_on_db.id}'
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT

    post_db = session_sql.query(Post).filter(Post.id == post_on_db.id).first()
    if original_comments_count > 0:
        assert post_db.comments_count == original_comments_count - 1
    else:
        assert post_db.comments_count == 0


@pytest.mark.integration
def test_get_nonexistent_comment_route(
    authenticate_client, community_member_on_db, post_on_db
):
    import uuid

    response = authenticate_client.get(
        f'/comments/{community_member_on_db.community_id}/post/{post_on_db.id}/comment/{uuid.uuid4()}'
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.integration
def test_update_nonexistent_comment_route(authenticate_client, community_member_on_db):
    import uuid

    comment_update = CommentUpdate(
        content='Tentativa de atualizar comentário inexistente'
    )

    response = authenticate_client.patch(
        f'/comments/{community_member_on_db.community_id}/comment/{uuid.uuid4()}',
        json=comment_update.model_dump(mode='json'),
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.integration
def test_delete_nonexistent_comment_route(authenticate_client, community_member_on_db):
    import uuid

    response = authenticate_client.delete(
        f'/comments/{community_member_on_db.community_id}/comment/{uuid.uuid4()}'
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.integration
def test_like_nonexistent_comment_route(authenticate_client, community_member_on_db):
    import uuid

    response = authenticate_client.post(
        f'/comments/{community_member_on_db.community_id}/comment/{uuid.uuid4()}/like'
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.integration
def test_unlike_comment_without_like_route(
    authenticate_client, comment_on_db, community_member_on_db
):
    response = authenticate_client.post(
        f'/comments/{community_member_on_db.community_id}/comment/{comment_on_db.id}/unlike'
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.integration
def test_unlike_comment_with_invalid_id_route(
    authenticate_client, comment_on_db, community_member_on_db
):
    response = authenticate_client.post(
        f'/comments/{community_member_on_db.community_id}/comment/{uuid.uuid4()}/unlike'
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.integration
def test_create_comment_with_invalid_content_route(
    authenticate_client, community_member_on_db, post_on_db
):
    invalid_comment_data = {
        'post_id': str(post_on_db.id),
        'user_id': str(community_member_on_db.user_id),
        'content': '',
        'parent_id': None,
        'status': 'active',
    }

    response = authenticate_client.post(
        f'/comments/{community_member_on_db.community_id}/post/{post_on_db.id}/create-comment',
        json=invalid_comment_data,
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.integration
def test_create_comment_with_nonexistent_post_route(
    authenticate_client, community_member_on_db
):
    comment = CommentCreate(
        post_id=str(uuid.uuid4()),
        member_id=str(community_member_on_db.id),
        content='Comentário em post inexistente',
        parent_id=None,
        status=CommentStatusEnum.ACTIVE,
    )

    response = authenticate_client.post(
        f'/comments/{community_member_on_db.community_id}/post/{uuid.uuid4()}/create-comment',
        json=comment.model_dump(mode='json'),
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.integration
def test_create_comment_reply_with_nonexistent_parent_route(
    authenticate_client, community_member_on_db, post_on_db
):
    reply = CommentCreate(
        post_id=str(post_on_db.id),
        member_id=str(community_member_on_db.id),
        content='Resposta a comentário inexistente',
        parent_id=str(uuid.uuid4()),
        status=CommentStatusEnum.ACTIVE,
    )

    response = authenticate_client.post(
        f'/comments/{community_member_on_db.community_id}/post/{post_on_db.id}/create-comment',
        json=reply.model_dump(mode='json'),
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.integration
def test_create_comment_reply_with_invalid_parent_route(
    authenticate_client, community_member_on_db, post_on_db
):
    reply = CommentCreate(
        post_id=str(post_on_db.id),
        member_id=str(community_member_on_db.id),
        content='Resposta a comentário inválido',
        parent_id=str(uuid.uuid4()),
        status=CommentStatusEnum.ACTIVE,
    )

    response = authenticate_client.post(
        f'/comments/{community_member_on_db.community_id}/post/{post_on_db.id}/create-comment',
        json=reply.model_dump(mode='json'),
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.integration
def test_comment_includes_member_role(
    authenticate_client, community_member_on_db, post_on_db
):
    comment = CommentCreate(
        post_id=str(post_on_db.id),
        member_id=str(community_member_on_db.id),
        content='Este é um comentário para testar o member_role',
        parent_id=None,
        status=CommentStatusEnum.ACTIVE,
    )

    response = authenticate_client.post(
        f'/comments/{community_member_on_db.community_id}/post/{post_on_db.id}/create-comment',
        json=comment.model_dump(mode='json'),
    )
    response_data = response.json()

    assert response.status_code == status.HTTP_201_CREATED
    assert 'member' in response_data
    assert 'member_role' in response_data['member']
    assert response_data['member']['member_role'] == community_member_on_db.role


@pytest.mark.integration
def test_list_comments_includes_member_role(
    authenticate_client, comment_on_db, community_member_on_db
):
    response = authenticate_client.get(
        f'/comments/{community_member_on_db.community_id}/post/{comment_on_db.post_id}/list-comments'
    )
    response_data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert len(response_data['items']) > 0

    comment_item = response_data['items'][0]
    assert 'member' in comment_item
    assert 'member_role' in comment_item['member']
    assert comment_item['member']['member_role'] is not None
