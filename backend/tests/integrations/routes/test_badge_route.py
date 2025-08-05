from uuid import uuid4

from fastapi import status


def test_get_badge_route(authenticate_member_client, commun_member_on_db, badge_on_db):
    response = authenticate_member_client.get(
        f'/badges/{commun_member_on_db.community_id}/badge/{badge_on_db.id}'
    )
    response_data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert response_data['id'] == str(badge_on_db.id)
    assert response_data['name'] == badge_on_db.name
    assert response_data['description'] == badge_on_db.description
    assert response_data['image_url'] == badge_on_db.image_url
    assert response_data['community_id'] == str(badge_on_db.community_id)


def test_get_non_existent_badge_route(authenticate_member_client, commun_member_on_db):
    response = authenticate_member_client.get(
        f'/badges/{commun_member_on_db.community_id}/badge/{uuid4()}'
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_list_badges_no_community_filter(
    authenticate_member_client, commun_member_on_db, badge_on_db
):
    response = authenticate_member_client.get(
        f'/badges/{commun_member_on_db.community_id}/list-badges'
    )
    response_data = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert response_data['total'] == 1
    assert response_data['items'][0]['id'] == str(badge_on_db.id)
    assert response_data['items'][0]['name'] == badge_on_db.name
    assert response_data['items'][0]['description'] == badge_on_db.description
    assert response_data['items'][0]['image_url'] == badge_on_db.image_url
    assert response_data['items'][0]['community_id'] == str(badge_on_db.community_id)


def test_list_badges_for_member(
    authenticate_member_client,
    commun_member_on_db,
    member_badge_assignment_on_db,
    badge_on_db,
):
    response = authenticate_member_client.get(
        f'/badges/{commun_member_on_db.community_id}/member/{member_badge_assignment_on_db.member_id}/list-badges'
    )
    response_data = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert len(response_data) == 1
    assert response_data[0]['id'] == str(member_badge_assignment_on_db.badge_id)
    assert response_data[0]['name'] == badge_on_db.name
    assert response_data[0]['description'] == badge_on_db.description
    assert response_data[0]['image_url'] == badge_on_db.image_url
    assert response_data[0]['community_id'] == str(badge_on_db.community_id)
