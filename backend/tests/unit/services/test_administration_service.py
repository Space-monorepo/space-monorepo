from app.api.administration.schema import ImportMembers
from app.api.administration.service import AdministrationService
from app.api.communities.schema import CommunityMemberRoleEnum
from app.api.post.schemas import (
    CampaignUpdate,
    ComplaintLevelEnum,
    ComplaintUpdate,
    PostFeedbackCreate,
)
from app.utils.schema import PaginationSearchParams


def test_import_users_to_community(transaction_manager, community_on_db, user_on_db):
    members = ImportMembers(emails=[user_on_db.email])
    members = AdministrationService(transaction_manager).import_users_to_community(
        members.emails, community_on_db.id
    )
    assert members is not None
    assert len(members) == 1
    assert members[0].user_id == user_on_db.id
    assert members[0].community_id == community_on_db.id
    assert members[0].role == CommunityMemberRoleEnum.MEMBER


def test_list_all_members_from_community(
    transaction_manager, community_on_db, community_member_on_db
):
    members = AdministrationService(transaction_manager).list_all_members_from_community(
        community_on_db.id, PaginationSearchParams(offset=0, limit=10)
    )
    assert members is not None
    assert members.items is not None
    assert len(members.items) == 1
    assert members.items[0].user_id == community_member_on_db.user_id
    assert members.items[0].community_id == community_member_on_db.community_id
    assert members.items[0].role == community_member_on_db.role
    assert (
        members.items[0].status_participation
        == community_member_on_db.status_participation
    )
    assert members.total == 1
    assert members.has_more == False


def test_list_user_admin_communities(
    transaction_manager, community_on_db, community_member_on_db
):
    communities = AdministrationService(transaction_manager).list_user_admin_communities(
        community_member_on_db.user_id, PaginationSearchParams(offset=0, limit=10)
    )
    assert communities is not None
    assert communities.items is not None
    assert len(communities.items) == 1
    assert communities.items[0].id == community_on_db.id
    assert communities.items[0].name == community_on_db.name
    assert communities.total == 1
    assert communities.has_more == False


def test_get_campaign(transaction_manager, campaign_post_on_db):
    campaign = AdministrationService(transaction_manager).get_campaign(
        campaign_post_on_db.post_id
    )
    assert campaign is not None
    assert campaign.post_id == campaign_post_on_db.post_id
    assert campaign.target_participants == campaign_post_on_db.target_participants
    assert campaign.current_participants == campaign_post_on_db.current_participants
    assert campaign.status_campaign == campaign_post_on_db.status_campaign


def test_update_campaign(transaction_manager, campaign_post_on_db):
    campaign = AdministrationService(transaction_manager).update_campaign(
        campaign_post_on_db.post_id, CampaignUpdate(target_participants=10)
    )
    assert campaign is not None
    assert campaign.post.id == campaign_post_on_db.post_id
    assert campaign.target_participants == 10
    assert campaign.current_participants == campaign_post_on_db.current_participants
    assert campaign.status_campaign == campaign_post_on_db.status_campaign


def test_list_all_campaigns_from_community(
    transaction_manager, community_on_db, campaign_post_on_db
):
    campaigns = AdministrationService(
        transaction_manager
    ).list_all_campaigns_from_community(
        community_on_db.id, PaginationSearchParams(offset=0, limit=10)
    )
    assert campaigns is not None
    assert campaigns.items is not None
    assert len(campaigns.items) == 1
    assert campaigns.items[0].post.id == campaign_post_on_db.post_id
    assert (
        campaigns.items[0].target_participants == campaign_post_on_db.target_participants
    )
    assert (
        campaigns.items[0].current_participants
        == campaign_post_on_db.current_participants
    )
    assert campaigns.items[0].status_campaign == campaign_post_on_db.status_campaign
    assert campaigns.total == 1
    assert campaigns.has_more == False


def test_get_complaint(transaction_manager, complaint_post_on_db):
    complaint = AdministrationService(transaction_manager).get_complaint(
        complaint_post_on_db.post_id
    )
    assert complaint is not None
    assert complaint.post_id == complaint_post_on_db.post_id
    assert complaint.confirmations_count == complaint_post_on_db.confirmations_count
    assert complaint.status_complaint == complaint_post_on_db.status_complaint
    assert complaint.level_complaint == complaint_post_on_db.level_complaint


def test_update_complaint(transaction_manager, complaint_post_on_db):
    complaint = AdministrationService(transaction_manager).update_complaint(
        complaint_post_on_db.post_id, ComplaintUpdate(confirmations_count=1)
    )
    assert complaint is not None
    assert complaint.post.id == complaint_post_on_db.post_id
    assert complaint.confirmations_count == 1
    assert complaint.status_complaint == complaint_post_on_db.status_complaint
    assert complaint.level_complaint == complaint_post_on_db.level_complaint

    complaint = AdministrationService(transaction_manager).update_complaint(
        complaint_post_on_db.post_id, ComplaintUpdate(confirmations_count=30)
    )
    assert complaint is not None
    assert complaint.post.id == complaint_post_on_db.post_id
    assert complaint.confirmations_count == 31
    assert complaint.status_complaint == complaint_post_on_db.status_complaint
    assert complaint.level_complaint == ComplaintLevelEnum.MEDIUM

    complaint = AdministrationService(transaction_manager).update_complaint(
        complaint_post_on_db.post_id, ComplaintUpdate(confirmations_count=50)
    )
    assert complaint is not None
    assert complaint.post.id == complaint_post_on_db.post_id
    assert complaint.confirmations_count == 81
    assert complaint.status_complaint == complaint_post_on_db.status_complaint
    assert complaint.level_complaint == ComplaintLevelEnum.HIGH

    complaint = AdministrationService(transaction_manager).update_complaint(
        complaint_post_on_db.post_id,
        ComplaintUpdate(status_complaint='under_investigation'),
    )
    assert complaint is not None
    assert complaint.post.id == complaint_post_on_db.post_id
    assert complaint.confirmations_count == 81
    assert complaint.status_complaint == 'under_investigation'
    assert complaint.level_complaint == ComplaintLevelEnum.HIGH


def test_list_all_complaints_from_community(
    transaction_manager, community_on_db, complaint_post_on_db
):
    complaints = AdministrationService(
        transaction_manager
    ).list_all_complaints_from_community(
        community_on_db.id, PaginationSearchParams(offset=0, limit=10)
    )
    assert complaints is not None
    assert complaints.items is not None
    assert len(complaints.items) == 1
    assert complaints.items[0].post.id == complaint_post_on_db.post_id
    assert (
        complaints.items[0].confirmations_count
        == complaint_post_on_db.confirmations_count
    )
    assert complaints.items[0].status_complaint == complaint_post_on_db.status_complaint
    assert complaints.items[0].level_complaint == complaint_post_on_db.level_complaint
    assert complaints.total == 1
    assert complaints.has_more == False


def test_create_post_feedback(transaction_manager, post_on_db, community_member_on_db):
    post_feedback_on_db = PostFeedbackCreate(
        post_id=post_on_db.id,
        member_id=community_member_on_db.id,
        subject='Feedback',
        message='Example message',
    )
    feedback = AdministrationService(transaction_manager).create_post_feedback(
        post_feedback_on_db
    )
    assert feedback is not None
    assert feedback.post_id == post_on_db.id
    assert feedback.member_id == community_member_on_db.id
    assert feedback.subject == 'Feedback'
    assert feedback.message == 'Example message'


def test_list_all_post_feedbacks(transaction_manager, post_feedback_on_db):
    params = PaginationSearchParams(offset=0, limit=10)
    feedbacks = AdministrationService(transaction_manager).list_feedbacks_from_post(
        post_feedback_on_db.post_id, params
    )
    assert feedbacks is not None
    assert feedbacks.items is not None
    assert len(feedbacks.items) == 1
    assert feedbacks.items[0].post_id == post_feedback_on_db.post_id
    assert feedbacks.items[0].member_id == post_feedback_on_db.member_id
    assert feedbacks.items[0].subject == post_feedback_on_db.subject
    assert feedbacks.items[0].message == post_feedback_on_db.message
    assert feedbacks.total == 1
    assert feedbacks.has_more == False
