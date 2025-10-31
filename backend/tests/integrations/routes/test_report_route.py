import pytest
from fastapi import status

from app.api.reports.schema import ReportCreate, ReportReasonEnum, ReportTypeEnum


@pytest.mark.integration
def test_create_report_member_route_success(
    authenticate_client,
    community_member_on_db,
    commun_member_on_db,
):
    # Arrange
    report_data = ReportCreate(
        reporter_id=str(community_member_on_db.id),
        type=ReportTypeEnum.MEMBER_REPORT,
        reason=ReportReasonEnum.HARASSMENT,
        description='Member is harassing other members',
    )

    # Act
    response = authenticate_client.post(
        f'/reports/{community_member_on_db.community_id}/create-report-member/{commun_member_on_db.id}',
        json=report_data.model_dump(mode='json'),
    )

    # Assert
    assert response.status_code == status.HTTP_201_CREATED
    response_data = response.json()
    assert response_data is not None
    assert response_data['member_id'] == str(commun_member_on_db.id)
    assert response_data['community_id'] == str(community_member_on_db.community_id)
    assert response_data['report']['reporter']['id'] == str(community_member_on_db.id)
    assert response_data['report']['type'] == ReportTypeEnum.MEMBER_REPORT
    assert response_data['report']['reason'] == ReportReasonEnum.HARASSMENT
    assert response_data['report']['description'] == report_data.description


@pytest.mark.integration
def test_create_report_member_route_unauthorized(
    client_sql,
    community_member_on_db,
    commun_member_on_db,
):
    # Arrange
    report_data = ReportCreate(
        reporter_id=str(community_member_on_db.id),
        type=ReportTypeEnum.MEMBER_REPORT,
        reason=ReportReasonEnum.HARASSMENT,
        description='Member is harassing other members',
    )

    # Act
    response = client_sql.post(
        f'/reports/{community_member_on_db.community_id}/create-report-member/{commun_member_on_db.id}',
        json=report_data.model_dump(mode='json'),
    )

    # Assert
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.integration
def test_create_report_post_route(
    authenticate_client,
    community_member_on_db,
    post_on_db,
):
    # Arrange
    report_data = ReportCreate(
        reporter_id=str(community_member_on_db.id),
        type=ReportTypeEnum.POST_REPORT,
        reason=ReportReasonEnum.SPAM,
        description='Post contains spam content',
    )

    # Act
    response = authenticate_client.post(
        f'/reports/{community_member_on_db.community_id}/create-report-post/{post_on_db.id}',
        json=report_data.model_dump(mode='json'),
    )

    # Assert
    assert response.status_code == status.HTTP_201_CREATED
    response_data = response.json()
    assert response_data is not None
    assert response_data['post_id'] == str(post_on_db.id)
    assert response_data['community_id'] == str(community_member_on_db.community_id)
    assert response_data['report']['reporter']['id'] == str(community_member_on_db.id)
    assert response_data['report']['type'] == ReportTypeEnum.POST_REPORT
    assert response_data['report']['reason'] == ReportReasonEnum.SPAM
    assert response_data['report']['description'] == report_data.description


@pytest.mark.integration
def test_create_report_post_route_unauthorized(
    client_sql,
    community_member_on_db,
    post_on_db,
):
    # Arrange
    report_data = ReportCreate(
        reporter_id=str(community_member_on_db.id),
        type=ReportTypeEnum.POST_REPORT,
        reason=ReportReasonEnum.SPAM,
        description='Post contains spam content',
    )

    # Act
    response = client_sql.post(
        f'/reports/{community_member_on_db.community_id}/create-report-post/{post_on_db.id}',
        json=report_data.model_dump(mode='json'),
    )

    # Assert
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.integration
def test_create_report_comment_route(
    authenticate_client,
    community_member_on_db,
    comment_on_db,
):
    # Arrange
    report_data = ReportCreate(
        reporter_id=str(community_member_on_db.id),
        type=ReportTypeEnum.COMMENT_REPORT,
        reason=ReportReasonEnum.HATE_SPEECH,
        description='Comment contains hate speech',
    )

    # Act
    response = authenticate_client.post(
        f'/reports/{community_member_on_db.community_id}/create-report-comment/{comment_on_db.id}',
        json=report_data.model_dump(mode='json'),
    )

    # Assert
    assert response.status_code == status.HTTP_201_CREATED
    response_data = response.json()
    assert response_data is not None
    assert response_data['comment_id'] == str(comment_on_db.id)
    assert response_data['community_id'] == str(community_member_on_db.community_id)
    assert response_data['report']['reporter']['id'] == str(community_member_on_db.id)
    assert response_data['report']['type'] == ReportTypeEnum.COMMENT_REPORT
    assert response_data['report']['reason'] == ReportReasonEnum.HATE_SPEECH
    assert response_data['report']['description'] == report_data.description


@pytest.mark.integration
def test_create_report_comment_route_unauthorized(
    client_sql,
    community_member_on_db,
    comment_on_db,
):
    # Arrange
    report_data = ReportCreate(
        reporter_id=str(community_member_on_db.id),
        type=ReportTypeEnum.COMMENT_REPORT,
        reason=ReportReasonEnum.HATE_SPEECH,
        description='Comment contains hate speech',
    )

    # Act
    response = client_sql.post(
        f'/reports/{community_member_on_db.community_id}/create-report-comment/{comment_on_db.id}',
        json=report_data.model_dump(mode='json'),
    )

    # Assert
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.integration
def test_create_duplicate_report_member_route(
    authenticate_client,
    community_member_on_db,
    commun_member_on_db,
):
    # Arrange
    report_data = ReportCreate(
        reporter_id=str(community_member_on_db.id),
        type=ReportTypeEnum.MEMBER_REPORT,
        reason=ReportReasonEnum.DISCRIMINATION,
        description='The description of the report',
    )

    # Act
    first_response = authenticate_client.post(
        f'/reports/{community_member_on_db.community_id}/create-report-member/{commun_member_on_db.id}',
        json=report_data.model_dump(mode='json'),
    )

    # Assert
    assert first_response.status_code == status.HTTP_201_CREATED

    # Tenta criar o mesmo report novamente
    second_response = authenticate_client.post(
        f'/reports/{community_member_on_db.community_id}/create-report-member/{commun_member_on_db.id}',
        json=report_data.model_dump(mode='json'),
    )
    assert second_response.status_code in [
        status.HTTP_400_BAD_REQUEST,
        status.HTTP_409_CONFLICT,
    ]


@pytest.mark.integration
def test_create_report_post_with_different_reasons_route(
    authenticate_client,
    community_member_on_db,
    post_on_db,
):
    # Arrange
    report_data_1 = ReportCreate(
        reporter_id=str(community_member_on_db.id),
        type=ReportTypeEnum.POST_REPORT,
        reason=ReportReasonEnum.SPAM,
        description='Post contains spam',
    )

    report_data_2 = ReportCreate(
        reporter_id=str(community_member_on_db.id),
        type=ReportTypeEnum.POST_REPORT,
        reason=ReportReasonEnum.INAPPROPRIATE_CONTENT,
        description='Post has inappropriate content',
    )

    # Act
    first_response = authenticate_client.post(
        f'/reports/{community_member_on_db.community_id}/create-report-post/{post_on_db.id}',
        json=report_data_1.model_dump(mode='json'),
    )
    assert first_response.status_code == status.HTTP_201_CREATED
    assert first_response.json()['report']['reason'] == ReportReasonEnum.SPAM

    # Cria o segundo report com motivo diferente
    second_response = authenticate_client.post(
        f'/reports/{community_member_on_db.community_id}/create-report-post/{post_on_db.id}',
        json=report_data_2.model_dump(mode='json'),
    )
    assert second_response.status_code == status.HTTP_201_CREATED
    assert (
        second_response.json()['report']['reason']
        == ReportReasonEnum.INAPPROPRIATE_CONTENT
    )


@pytest.mark.integration
def test_create_report_comment_with_all_reasons_route(
    authenticate_client,
    community_member_on_db,
    comment_on_db,
):
    # Arrange
    reasons = [
        (ReportReasonEnum.SPAM, 'Spam content'),
        (ReportReasonEnum.HARASSMENT, 'Harassment behavior'),
        (ReportReasonEnum.HATE_SPEECH, 'Hate speech detected'),
        (ReportReasonEnum.INAPPROPRIATE_CONTENT, 'Inappropriate content'),
        (ReportReasonEnum.DISCRIMINATION, 'Discriminatory language'),
        (ReportReasonEnum.MISINFORMATION, 'False information spread'),
        (ReportReasonEnum.OTHER, 'Other reason'),
    ]

    for reason, description in reasons:
        report_data = ReportCreate(
            reporter_id=str(community_member_on_db.id),
            type=ReportTypeEnum.COMMENT_REPORT,
            reason=reason,
            description=description,
        )

        # Act
        response = authenticate_client.post(
            f'/reports/{community_member_on_db.community_id}/create-report-comment/{comment_on_db.id}',
            json=report_data.model_dump(mode='json'),
        )

        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        response_data = response.json()
        assert response_data['report']['reason'] == reason
        assert response_data['report']['description'] == description
