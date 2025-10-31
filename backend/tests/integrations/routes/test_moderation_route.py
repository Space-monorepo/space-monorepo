import pytest
from fastapi import status


@pytest.mark.integration
def test_list_all_member_brief_reports_route_success(
    authenticate_client,
    community_member_on_db,
    report_member_on_db,
):
    """
    Testa a listagem de resumos de reports de membros via rota.
    """
    # Arrange & Act
    response = authenticate_client.get(
        f'/moderation/{community_member_on_db.community_id}/list-all-member-brief-reports'
    )

    # Assert
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert response_data is not None
    assert 'items' in response_data
    assert 'total' in response_data
    assert isinstance(response_data['items'], list)


@pytest.mark.integration
def test_list_all_member_brief_reports_route_unauthorized(
    client_sql,
    community_member_on_db,
):
    """
    Testa a listagem de resumos de reports de membros sem autenticação.
    """
    # Arrange & Act
    response = client_sql.get(
        f'/moderation/{community_member_on_db.community_id}/list-all-member-brief-reports'
    )

    # Assert
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.integration
def test_list_all_member_reports_route_success(
    authenticate_client,
    community_member_on_db,
    commun_member_on_db,
    report_member_on_db,
):
    """
    Testa a listagem de todos os reports de um membro específico via rota.
    """
    # Arrange & Act
    response = authenticate_client.get(
        f'/moderation/{community_member_on_db.community_id}/list-all-member-reports/{commun_member_on_db.id}'
    )

    # Assert
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert response_data is not None
    assert 'items' in response_data
    assert 'total' in response_data
    assert isinstance(response_data['items'], list)


@pytest.mark.integration
def test_list_all_member_reports_route_unauthorized(
    client_sql,
    community_member_on_db,
    commun_member_on_db,
):
    """
    Testa a listagem de reports de um membro sem autenticação.
    """
    # Arrange & Act
    response = client_sql.get(
        f'/moderation/{community_member_on_db.community_id}/list-all-member-reports/{commun_member_on_db.id}'
    )

    # Assert
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.integration
def test_delete_report_member_route_success(
    authenticate_client,
    community_member_on_db,
    report_member_on_db,
):
    """
    Testa a deleção de um report de membro via rota.
    """
    # Arrange & Act
    response = authenticate_client.delete(
        f'/moderation/{community_member_on_db.community_id}/report-member/{report_member_on_db.report_id}'
    )

    # Assert
    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.integration
def test_delete_report_member_route_unauthorized(
    client_sql,
    community_member_on_db,
    report_member_on_db,
):
    """
    Testa a deleção de um report de membro sem autenticação.
    """
    # Arrange & Act
    response = client_sql.delete(
        f'/moderation/{community_member_on_db.community_id}/report-member/{report_member_on_db.report_id}'
    )

    # Assert
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.integration
def test_list_all_post_brief_reports_route_success(
    authenticate_client,
    community_member_on_db,
    report_post_on_db,
):
    """
    Testa a listagem de resumos de reports de posts via rota.
    """
    # Arrange & Act
    response = authenticate_client.get(
        f'/moderation/{community_member_on_db.community_id}/list-all-post-brief-reports'
    )

    # Assert
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert response_data is not None
    assert 'items' in response_data
    assert 'total' in response_data
    assert isinstance(response_data['items'], list)


@pytest.mark.integration
def test_list_all_post_brief_reports_route_unauthorized(
    client_sql,
    community_member_on_db,
):
    """
    Testa a listagem de resumos de reports de posts sem autenticação.
    """
    # Arrange & Act
    response = client_sql.get(
        f'/moderation/{community_member_on_db.community_id}/list-all-post-brief-reports'
    )

    # Assert
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.integration
def test_list_all_post_reports_route_success(
    authenticate_client,
    community_member_on_db,
    post_on_db,
    report_post_on_db,
):
    """
    Testa a listagem de todos os reports de um post específico via rota.
    """
    # Arrange & Act
    response = authenticate_client.get(
        f'/moderation/{community_member_on_db.community_id}/list-all-post-reports/{post_on_db.id}'
    )

    # Assert
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert response_data is not None
    assert 'items' in response_data
    assert 'total' in response_data
    assert isinstance(response_data['items'], list)


@pytest.mark.integration
def test_list_all_post_reports_route_unauthorized(
    client_sql,
    community_member_on_db,
    post_on_db,
):
    """
    Testa a listagem de reports de um post sem autenticação.
    """
    # Arrange & Act
    response = client_sql.get(
        f'/moderation/{community_member_on_db.community_id}/list-all-post-reports/{post_on_db.id}'
    )

    # Assert
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.integration
def test_delete_report_post_route_success(
    authenticate_client,
    community_member_on_db,
    report_post_on_db,
):
    """
    Testa a deleção de um report de post via rota.
    """
    # Arrange & Act
    response = authenticate_client.delete(
        f'/moderation/{community_member_on_db.community_id}/report-post/{report_post_on_db.report_id}'
    )

    # Assert
    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.integration
def test_delete_report_post_route_unauthorized(
    client_sql,
    community_member_on_db,
    report_post_on_db,
):
    """
    Testa a deleção de um report de post sem autenticação.
    """
    # Arrange & Act
    response = client_sql.delete(
        f'/moderation/{community_member_on_db.community_id}/report-post/{report_post_on_db.report_id}'
    )

    # Assert
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.integration
def test_list_all_comment_brief_reports_route_success(
    authenticate_client,
    community_member_on_db,
    report_comment_on_db,
):
    """
    Testa a listagem de resumos de reports de comentários via rota.
    """
    # Arrange & Act
    response = authenticate_client.get(
        f'/moderation/{community_member_on_db.community_id}/list-all-comment-brief-reports'
    )

    # Assert
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert response_data is not None
    assert 'items' in response_data
    assert 'total' in response_data
    assert isinstance(response_data['items'], list)


@pytest.mark.integration
def test_list_all_comment_brief_reports_route_unauthorized(
    client_sql,
    community_member_on_db,
):
    """
    Testa a listagem de resumos de reports de comentários sem autenticação.
    """
    # Arrange & Act
    response = client_sql.get(
        f'/moderation/{community_member_on_db.community_id}/list-all-comment-brief-reports'
    )

    # Assert
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.integration
def test_list_all_comment_reports_route_success(
    authenticate_client,
    community_member_on_db,
    comment_on_db,
    report_comment_on_db,
):
    """
    Testa a listagem de todos os reports de um comentário específico via rota.
    """
    # Arrange & Act
    response = authenticate_client.get(
        f'/moderation/{community_member_on_db.community_id}/list-all-comment-reports/{comment_on_db.id}'
    )

    # Assert
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert response_data is not None
    assert 'items' in response_data
    assert 'total' in response_data
    assert isinstance(response_data['items'], list)


@pytest.mark.integration
def test_list_all_comment_reports_route_unauthorized(
    client_sql,
    community_member_on_db,
    comment_on_db,
):
    """
    Testa a listagem de reports de um comentário sem autenticação.
    """
    # Arrange & Act
    response = client_sql.get(
        f'/moderation/{community_member_on_db.community_id}/list-all-comment-reports/{comment_on_db.id}'
    )

    # Assert
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.integration
def test_delete_report_comment_route_success(
    authenticate_client,
    community_member_on_db,
    report_comment_on_db,
):
    """
    Testa a deleção de um report de comentário via rota.
    """
    # Arrange & Act
    response = authenticate_client.delete(
        f'/moderation/{community_member_on_db.community_id}/report-comment/{report_comment_on_db.report_id}'
    )

    # Assert
    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.integration
def test_delete_report_comment_route_unauthorized(
    client_sql,
    community_member_on_db,
    report_comment_on_db,
):
    """
    Testa a deleção de um report de comentário sem autenticação.
    """
    # Arrange & Act
    response = client_sql.delete(
        f'/moderation/{community_member_on_db.community_id}/report-comment/{report_comment_on_db.report_id}'
    )

    # Assert
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.integration
def test_list_all_complaints_from_community_route_success(
    authenticate_client,
    community_member_on_db,
    complaint_post_on_db,
):
    """
    Testa a listagem de denúncias de uma comunidade via rota.
    """
    # Arrange & Act
    response = authenticate_client.get(
        f'/moderation/{community_member_on_db.community_id}/list-all-complaints'
    )

    # Assert
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert response_data is not None
    assert 'items' in response_data
    assert 'total' in response_data
    assert isinstance(response_data['items'], list)
    assert len(response_data['items']) >= 1


@pytest.mark.integration
def test_list_all_complaints_from_community_route_unauthorized(
    client_sql,
    community_member_on_db,
):
    """
    Testa a listagem de denúncias sem autenticação.
    """
    # Arrange & Act
    response = client_sql.get(
        f'/moderation/{community_member_on_db.community_id}/list-all-complaints'
    )

    # Assert
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.integration
def test_list_all_polls_from_community_route_success(
    authenticate_client,
    community_member_on_db,
    poll_post_on_db,
    poll_option_on_db,
):
    """
    Testa a listagem de enquetes de uma comunidade via rota.
    """
    # Arrange & Act
    response = authenticate_client.get(
        f'/moderation/{community_member_on_db.community_id}/list-all-polls'
    )

    # Assert
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert response_data is not None
    assert 'items' in response_data
    assert 'total' in response_data
    assert isinstance(response_data['items'], list)
    assert len(response_data['items']) >= 1
    if len(response_data['items']) > 0:
        assert 'post' in response_data['items'][0]
        assert 'question' in response_data['items'][0]
        assert 'options' in response_data['items'][0]
        assert 'total_votes' in response_data['items'][0]


@pytest.mark.integration
def test_list_all_polls_from_community_route_unauthorized(
    client_sql,
    community_member_on_db,
):
    """
    Testa a listagem de enquetes sem autenticação.
    """
    # Arrange & Act
    response = client_sql.get(
        f'/moderation/{community_member_on_db.community_id}/list-all-polls'
    )

    # Assert
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.integration
def test_list_all_announcements_from_community_route_success(
    authenticate_client,
    community_member_on_db,
    announcement_post_on_db,
):
    """
    Testa a listagem de anúncios de uma comunidade via rota.
    """
    # Arrange & Act
    response = authenticate_client.get(
        f'/moderation/{community_member_on_db.community_id}/list-all-announcements'
    )

    # Assert
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert response_data is not None
    assert 'items' in response_data
    assert 'total' in response_data
    assert isinstance(response_data['items'], list)
    assert len(response_data['items']) >= 1
    if len(response_data['items']) > 0:
        assert response_data['items'][0]['type_post'] == 'announcement'


@pytest.mark.integration
def test_list_all_announcements_from_community_route_unauthorized(
    client_sql,
    community_member_on_db,
):
    """
    Testa a listagem de anúncios sem autenticação.
    """
    # Arrange & Act
    response = client_sql.get(
        f'/moderation/{community_member_on_db.community_id}/list-all-announcements'
    )

    # Assert
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.integration
def test_update_status_complaint_route_success(
    authenticate_client,
    community_member_on_db,
    complaint_post_on_db,
):
    """
    Testa a atualização do status de uma denúncia via rota.
    """
    # Arrange
    from app.api.post.schemas import ComplaintStatusEnum

    complaint_status = ComplaintStatusEnum.UNDER_INVESTIGATION.value

    # Act
    response = authenticate_client.patch(
        f'/moderation/{community_member_on_db.community_id}/complaint/{complaint_post_on_db.post_id}/status/{complaint_status}'
    )

    # Assert
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert response_data is not None
    assert response_data['status_complaint'] == complaint_status


@pytest.mark.integration
def test_update_status_complaint_route_unauthorized(
    client_sql,
    community_member_on_db,
    complaint_post_on_db,
):
    """
    Testa a atualização do status de uma denúncia sem autenticação.
    """
    # Arrange
    from app.api.post.schemas import ComplaintStatusEnum

    complaint_status = ComplaintStatusEnum.UNDER_INVESTIGATION.value

    # Act
    response = client_sql.patch(
        f'/moderation/{community_member_on_db.community_id}/complaint/{complaint_post_on_db.post_id}/status/{complaint_status}'
    )

    # Assert
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.integration
def test_moderate_report_route_success(
    authenticate_client,
    community_member_on_db,
    report_post_on_db,
):
    """
    Testa a moderação de um report via rota (votação).
    """
    # Arrange
    from app.api.reports.schema import VoteTypeEnum

    vote_data = {
        'report_id': str(report_post_on_db.report_id),
        'moderator_id': str(community_member_on_db.id),
        'vote': VoteTypeEnum.SUSPEND.value
    }

    # Act
    response = authenticate_client.post(
        f'/moderation/{community_member_on_db.community_id}/moderate-report/{report_post_on_db.report_id}',
        json=vote_data
    )

    # Assert
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert response_data is not None
    # Pode retornar ModerationVotesResponse (se ainda faltam votos) ou ModerationActionResponse (se ação foi tomada)
    assert 'vote' in response_data or 'action' in response_data


@pytest.mark.integration
def test_moderate_report_route_unauthorized(
    client_sql,
    community_member_on_db,
    report_post_on_db,
):
    """
    Testa a moderação de um report sem autenticação.
    """
    # Arrange
    from app.api.reports.schema import VoteTypeEnum

    vote_data = {
        'report_id': str(report_post_on_db.report_id),
        'moderator_id': str(community_member_on_db.id),
        'vote': VoteTypeEnum.SUSPEND.value
    }

    # Act
    response = client_sql.post(
        f'/moderation/{community_member_on_db.community_id}/moderate-report/{report_post_on_db.report_id}',
        json=vote_data
    )

    # Assert
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
