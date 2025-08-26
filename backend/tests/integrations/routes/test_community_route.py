import pytest
from fastapi import status

from app.api.communities.schema import CommunityUpdate


@pytest.mark.integration
def test_get_community_by_id_route(authenticate_client, community_on_db):
    response = authenticate_client.get(f'/communities/{community_on_db.id}')
    response_data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert response_data['id'] == str(community_on_db.id)
    assert response_data['name'] == community_on_db.name
    assert response_data['description'] == community_on_db.description
    assert response_data['type_community'] == community_on_db.type_community


@pytest.mark.integration
def test_list_communities_route(authenticate_client, community_on_db):
    response = authenticate_client.get('/communities/')
    response_data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert 'items' in response_data
    assert 'total' in response_data
    assert len(response_data['items']) > 0
    assert any(item['id'] == str(community_on_db.id) for item in response_data['items'])


@pytest.mark.integration
def test_update_community_route(authenticate_client, community_on_db, community_member_on_db):
    community_update = CommunityUpdate(
        name="Updated Community Name",
        description="This is an updated description for the community"
    )

    response = authenticate_client.patch(
        f'/communities/{community_on_db.id}',
        json=community_update.model_dump(exclude_unset=True)
    )
    response_data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert response_data['id'] == str(community_on_db.id)
    assert response_data['name'] == "Updated Community Name"
    assert response_data['description'] == "This is an updated description for the community"
    assert response_data['type_community'] == community_on_db.type_community


@pytest.mark.integration
def test_delete_community_route_as_admin(authenticate_client, community_on_db, community_member_on_db):
    community_id = community_on_db.id
    response = authenticate_client.delete(f'/communities/{community_id}')
    assert response.status_code == status.HTTP_204_NO_CONTENT

    response = authenticate_client.get(f'/communities/{community_id}')
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.integration
def test_delete_community_route_as_non_admin(authenticate_member_client, community_on_db, commun_member_on_db):
    response = authenticate_member_client.delete(f'/communities/{community_on_db.id}')
    assert response.status_code == status.HTTP_403_FORBIDDEN

    response = authenticate_member_client.get(f'/communities/{community_on_db.id}')
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['id'] == str(community_on_db.id)


@pytest.mark.integration
def test_list_community_members_route(authenticate_client, community_on_db, community_member_on_db):
    response = authenticate_client.get(f'/communities/{community_on_db.id}/members')
    response_data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert 'items' in response_data
    assert 'total' in response_data
    assert len(response_data['items']) > 0
    assert response_data['items'][0]['user_id'] == str(community_member_on_db.user_id)
    assert response_data['items'][0]['community_id'] == str(community_member_on_db.community_id)
    assert response_data['items'][0]['role'] == community_member_on_db.role


@pytest.mark.integration
def test_list_user_communities_route(authenticate_client, user_on_db, community_on_db, community_member_on_db):
    response = authenticate_client.get(f'/communities/user/{user_on_db.id}/communities')
    response_data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert 'items' in response_data
    assert 'total' in response_data
    assert len(response_data['items']) > 0
    assert response_data['items'][0]['id'] == str(community_on_db.id)
    assert response_data['items'][0]['name'] == community_on_db.name


@pytest.mark.integration
def test_list_community_moderators_route(authenticate_client, community_on_db, community_member_on_db):
    response = authenticate_client.get(f'/communities/{community_on_db.id}/moderators')
    response_data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert 'items' in response_data
    assert 'total' in response_data
    assert len(response_data['items']) > 0
    assert response_data['items'][0]['user_id'] == str(community_member_on_db.user_id)
    assert response_data['items'][0]['community_id'] == str(community_member_on_db.community_id)
    assert response_data['items'][0]['role'] == community_member_on_db.role
