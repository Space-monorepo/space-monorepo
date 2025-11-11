import pytest
from fastapi import status

from app.api.communities.model import CommunityMember


@pytest.mark.integration
def test_get_reputation_score_route(
    authenticate_client, session_sql, community_member_on_db
):
    # Arrange
    member = (
        session_sql.query(CommunityMember)
        .filter_by(id=community_member_on_db.id)
        .first()
    )
    member.reputation = 5000
    session_sql.commit()

    # Act
    response = authenticate_client.get(
        f'/reputation/{community_member_on_db.community_id}/score'
    )

    # Assert
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert 'reputation' in response_data
    assert response_data['reputation'] == 5000


@pytest.mark.integration
def test_get_reputation_level_route(
    authenticate_client, session_sql, community_member_on_db
):
    # Arrange
    member = (
        session_sql.query(CommunityMember)
        .filter_by(id=community_member_on_db.id)
        .first()
    )
    member.reputation = 7000
    member.reputation_level = 'contributor'
    session_sql.commit()

    # Act
    response = authenticate_client.get(
        f'/reputation/{community_member_on_db.community_id}/level'
    )

    # Assert
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert 'reputation_level' in response_data
    assert response_data['reputation_level'] == 'contributor'


@pytest.mark.integration
def test_get_popularity_score_route(
    authenticate_client, session_sql, community_member_on_db
):
    # Arrange
    member = (
        session_sql.query(CommunityMember)
        .filter_by(id=community_member_on_db.id)
        .first()
    )
    member.popularity = 3500
    session_sql.commit()

    # Act
    response = authenticate_client.get(
        f'/reputation/{community_member_on_db.community_id}/popularity'
    )

    # Assert
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert 'popularity' in response_data
    assert response_data['popularity'] == 3500


@pytest.mark.integration
def test_get_reputation_score_with_zero_points_route(
    authenticate_client, session_sql, community_member_on_db
):
    # Arrange
    member = (
        session_sql.query(CommunityMember)
        .filter_by(id=community_member_on_db.id)
        .first()
    )
    member.reputation = 0
    session_sql.commit()

    # Act
    response = authenticate_client.get(
        f'/reputation/{community_member_on_db.community_id}/score'
    )

    # Assert
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert response_data['reputation'] == 0


@pytest.mark.integration
def test_get_reputation_level_under_observation_route(
    authenticate_client, session_sql, community_member_on_db
):
    # Arrange
    member = (
        session_sql.query(CommunityMember)
        .filter_by(id=community_member_on_db.id)
        .first()
    )
    member.reputation = 1000
    member.reputation_level = 'under_observation'
    session_sql.commit()

    # Act
    response = authenticate_client.get(
        f'/reputation/{community_member_on_db.community_id}/level'
    )

    # Assert
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert response_data['reputation_level'] == 'under_observation'


@pytest.mark.integration
def test_get_reputation_level_helper_route(
    authenticate_client, session_sql, community_member_on_db
):
    # Arrange
    member = (
        session_sql.query(CommunityMember)
        .filter_by(id=community_member_on_db.id)
        .first()
    )
    member.reputation = 4500
    member.reputation_level = 'helper'
    session_sql.commit()

    # Act
    response = authenticate_client.get(
        f'/reputation/{community_member_on_db.community_id}/level'
    )

    # Assert
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert response_data['reputation_level'] == 'helper'


@pytest.mark.integration
def test_get_reputation_level_leader_route(
    authenticate_client, session_sql, community_member_on_db
):
    # Arrange
    member = (
        session_sql.query(CommunityMember)
        .filter_by(id=community_member_on_db.id)
        .first()
    )
    member.reputation = 10000
    member.reputation_level = 'leader'
    session_sql.commit()

    # Act
    response = authenticate_client.get(
        f'/reputation/{community_member_on_db.community_id}/level'
    )

    # Assert
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert response_data['reputation_level'] == 'leader'


@pytest.mark.integration
def test_get_reputation_score_unauthorized_returns_401(client_sql, community_on_db):
    # Act
    response = client_sql.get(f'/reputation/{community_on_db.id}/score')

    # Assert
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
