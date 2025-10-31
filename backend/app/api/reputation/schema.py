from enum import Enum


class ReputationLevelEnum(str, Enum):
    UNDER_OBSERVATION = 'under_observation'
    HELPER = 'helper'
    CONTRIBUTOR = 'contributor'
    LEADER = 'leader'


class ReputationActionEnum(str, Enum):
    CREATE_CAMPAIGN = 'create_campaign'
    CAMPAIGN_ACCEPTED = 'campaign_accepted'
    CAMPAIGN_REJECTED = 'campaign_rejected'
    CAMPAIGN_SUPPORT = 'campaign_support'
    REPORT_APPROVED = 'report_approved'
    REPORT_REJECTED = 'report_rejected'
    RECEIVED_VALID_SELF_REPORT = 'received_valid_self_report'
    RECEIVED_VALID_SELF_COMPLAINT = 'received_valid_self_complaint'


REPUTATION_POINTS = {
    ReputationActionEnum.CREATE_CAMPAIGN: 100,
    ReputationActionEnum.CAMPAIGN_ACCEPTED: 400,
    ReputationActionEnum.CAMPAIGN_REJECTED: -50,
    ReputationActionEnum.CAMPAIGN_SUPPORT: 50,
    ReputationActionEnum.REPORT_APPROVED: 200,
    ReputationActionEnum.REPORT_REJECTED: -100,
    ReputationActionEnum.RECEIVED_VALID_SELF_REPORT: -250,
    ReputationActionEnum.RECEIVED_VALID_SELF_COMPLAINT: -400,
}


class PopularityActionEnum(str, Enum):
    LIKE_POST = 'like_post'
    RECEIVE_LIKE = 'receive_like'
    COMMENT_POST = 'comment_post'
    RECEIVE_COMMENT = 'receive_comment'
    POST_REACH_100_VIEWS = 'post_reach_100_views'
    CREATE_POST = 'create_post'
    STREAK_7_DAYS_ACTIVE = 'streak_7_days_active'
    REPORT_APPROVED = 'report_approved'
    REPORT_REJECTED = 'report_rejected'
    RECEIVED_VALID_REPORT = 'received_valid_report'
    RECEIVED_VALID_COMPLAINT = 'received_valid_complaint'


POPULARITY_POINTS = {
    PopularityActionEnum.LIKE_POST: 10,
    PopularityActionEnum.RECEIVE_LIKE: 20,
    PopularityActionEnum.COMMENT_POST: 25,
    PopularityActionEnum.RECEIVE_COMMENT: 40,
    PopularityActionEnum.POST_REACH_100_VIEWS: 50,
    PopularityActionEnum.CREATE_POST: 100,
    PopularityActionEnum.STREAK_7_DAYS_ACTIVE: 200,
    PopularityActionEnum.REPORT_APPROVED: 200,
    PopularityActionEnum.REPORT_REJECTED: -100,
    PopularityActionEnum.RECEIVED_VALID_REPORT: -250,
    PopularityActionEnum.RECEIVED_VALID_COMPLAINT: -400,
}
