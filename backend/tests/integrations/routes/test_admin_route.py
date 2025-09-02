import pytest

from fastapi import status

from app.api.administration.schema import ImportMembers, MemberRoleUpdate
from app.api.administration.service import AdministrationService
from app.api.communities.schema import CommunityMemberRoleEnum
from app.api.post.schemas import (
    CampaignStatusEnum,
    CampaignUpdate,
    ComplaintStatusEnum,
    ComplaintUpdate,
    PostFeedbackCreate,
)
from app.utils.schema import PaginationSearchParams


@pytest.mark.integration
def test_import_users_to_community_route(
    authenticate_client,
    transaction_manager,
    community_member_on_db,
    secondary_user_on_db,
):
    members = ImportMembers(emails=[secondary_user_on_db.email])
    response = authenticate_client.post(
        f'/admin/{community_member_on_db.community_id}/users/add-users',
        json=members.model_dump(),
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() is not None
    assert len(response.json()) == 1
    assert response.json()[0]['user']['id'] == str(secondary_user_on_db.id)
    assert response.json()[0]['community']['id'] == str(community_member_on_db.community_id)
    assert response.json()[0]['role'] == CommunityMemberRoleEnum.MEMBER


@pytest.mark.integration
def test_list_all_members_from_community_route(
    authenticate_client, community_on_db, community_member_on_db
):
    response = authenticate_client.get(f'/admin/{community_on_db.id}/users/list-all')

    assert response.status_code == status.HTTP_200_OK
    assert response.json() is not None
    assert response.json()['items'] is not None
    assert len(response.json()['items']) == 1
    assert response.json()['items'][0]['user']['id'] == str(community_member_on_db.user_id)
    assert response.json()['items'][0]['community']['id'] == str(
        community_member_on_db.community_id
    )
    assert response.json()['items'][0]['role'] == CommunityMemberRoleEnum.ADMIN


@pytest.mark.integration
def test_list_user_admin_communities_route(
    authenticate_client, community_on_db, community_member_on_db
):
    response = authenticate_client.get(
        f'/admin/{community_on_db.id}/users/list-admin-communities'
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() is not None
    assert response.json()['items'] is not None
    assert len(response.json()['items']) == 1
    assert response.json()['items'][0]['id'] == str(community_on_db.id)
    assert response.json()['items'][0]['name'] == community_on_db.name
    assert response.json()['items'][0]['description'] == community_on_db.description


@pytest.mark.integration
def test_update_member_role_route(
    authenticate_client, community_on_db, community_member_on_db
):
    role = MemberRoleUpdate(new_role=CommunityMemberRoleEnum.MODERATOR)

    response = authenticate_client.patch(
        f'/admin/{community_on_db.id}/users/{community_member_on_db.id}/update-role',
        json=role.model_dump(),
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() is not None
    assert response.json()['role'] == role.new_role


@pytest.mark.integration
def test_remove_member_from_community_route(
    authenticate_client, community_on_db, community_member_on_db
):
    response = authenticate_client.delete(
        f'/admin/{community_on_db.id}/users/{community_member_on_db.id}/remove'
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.integration
def test_update_campaign_route(
    authenticate_client, community_on_db, community_member_on_db, campaign_post_on_db
):
    campaign = CampaignUpdate(
        target_participants=10, status_campaign=CampaignStatusEnum.APPROVED
    )
    response = authenticate_client.patch(
        f'/admin/{community_on_db.id}/post/{campaign_post_on_db.post_id}/campaign',
        json=campaign.model_dump(),
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() is not None
    assert response.json()['target_participants'] == 10
    assert response.json()['status_campaign'] == CampaignStatusEnum.APPROVED


@pytest.mark.integration
def test_list_all_campaigns_from_community_route(
    authenticate_client, community_on_db, community_member_on_db, campaign_post_on_db
):
    response = authenticate_client.get(
        f'/admin/{community_on_db.id}/post/list-all-campaigns'
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() is not None
    assert response.json()['items'] is not None
    assert len(response.json()['items']) == 1
    assert response.json()['items'][0]['post']['id'] == str(campaign_post_on_db.post_id)
    assert (
        response.json()['items'][0]['target_participants']
        == campaign_post_on_db.target_participants
    )
    assert (
        response.json()['items'][0]['status_campaign']
        == campaign_post_on_db.status_campaign
    )


@pytest.mark.integration
def test_update_complaint_route(
    authenticate_client, community_on_db, community_member_on_db, complaint_post_on_db
):
    complaint = ComplaintUpdate(
        confirmations_count=1, status_complaint=ComplaintStatusEnum.UNDER_INVESTIGATION
    )
    response = authenticate_client.patch(
        f'/admin/{community_on_db.id}/post/{complaint_post_on_db.post_id}/complaint',
        json=complaint.model_dump(),
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() is not None
    assert response.json()['confirmations_count'] == 1
    assert response.json()['status_complaint'] == ComplaintStatusEnum.UNDER_INVESTIGATION


@pytest.mark.integration
def test_list_all_complaints_from_community_route(
    authenticate_client, community_on_db, community_member_on_db, complaint_post_on_db
):
    response = authenticate_client.get(
        f'/admin/{community_on_db.id}/post/list-all-complaints'
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() is not None
    assert response.json()['items'] is not None
    assert len(response.json()['items']) == 1
    assert response.json()['items'][0]['post']['id'] == str(complaint_post_on_db.post_id)
    assert (
        response.json()['items'][0]['confirmations_count']
        == complaint_post_on_db.confirmations_count
    )
    assert (
        response.json()['items'][0]['status_complaint']
        == complaint_post_on_db.status_complaint
    )
    assert (
        response.json()['items'][0]['level_complaint']
        == complaint_post_on_db.level_complaint
    )


@pytest.mark.integration
def test_create_post_feedback_route(
    authenticate_client, community_on_db, community_member_on_db, post_on_db
):
    post_feedback = PostFeedbackCreate(
        post_id=str(post_on_db.id),
        member_id=str(community_member_on_db.id),
        subject='Feedback',
        message='Example message',
    )
    response = authenticate_client.post(
        f'/admin/{community_on_db.id}/post/create-feedback',
        json=post_feedback.model_dump(mode='json'),
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() is not None
    assert response.json()['post_id'] == str(post_on_db.id)
    assert response.json()['member_id'] == str(community_member_on_db.id)
    assert response.json()['subject'] == 'Feedback'
    assert response.json()['message'] == 'Example message'


@pytest.mark.integration
def test_list_feedbacks_from_post_route(
    authenticate_client,
    community_on_db,
    community_member_on_db,
    post_on_db,
    post_feedback_on_db,
):
    response = authenticate_client.get(
        f'/admin/{community_on_db.id}/post/{post_on_db.id}/list-feedbacks'
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() is not None
    assert response.json()['items'] is not None
    assert len(response.json()['items']) == 1
    assert response.json()['items'][0]['post_id'] == str(post_on_db.id)
    assert response.json()['items'][0]['member_id'] == str(community_member_on_db.id)
    assert response.json()['items'][0]['subject'] == 'Feedback'
    assert response.json()['items'][0]['message'] == 'Example message'
