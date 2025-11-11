from enum import Enum

from pydantic import BaseModel


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
    REPORT_SUSPENDED = 'report_suspended'
    REPORT_TOLERATED = 'report_tolerated'
    RECEIVED_VALID_REPORT_TO_USER = 'received_valid_report_to_user'
    CREATE_COMPLAINT = 'create_complaint'
    CONFIRM_COMPLAINT = 'confirm_complaint'
    COMPLAINT_RESOLVED = 'complaint_resolved'
    RESOLVE_COMPLAINT_MODERATOR = 'resolve_complaint_moderator'


REPUTATION_POINTS = {
    ReputationActionEnum.CREATE_CAMPAIGN: 100,
    ReputationActionEnum.CAMPAIGN_ACCEPTED: 400,
    ReputationActionEnum.CAMPAIGN_REJECTED: -50,
    ReputationActionEnum.CAMPAIGN_SUPPORT: 50,
    ReputationActionEnum.REPORT_SUSPENDED: 200,
    ReputationActionEnum.REPORT_TOLERATED: -100,
    ReputationActionEnum.RECEIVED_VALID_REPORT_TO_USER: -250,
    ReputationActionEnum.CREATE_COMPLAINT: 100,
    ReputationActionEnum.CONFIRM_COMPLAINT: 30,
    ReputationActionEnum.COMPLAINT_RESOLVED: 200,
    ReputationActionEnum.RESOLVE_COMPLAINT_MODERATOR: 500,
}


class PopularityActionEnum(str, Enum):
    LIKE = 'like'
    RECEIVE_LIKE = 'receive_like'
    COMMENT_POST = 'comment_post'
    RECEIVE_COMMENT = 'receive_comment'
    CREATE_POST = 'create_post'
    REPORT_SUSPENDED = 'report_suspended'
    REPORT_TOLERATED = 'report_tolerated'
    RECEIVED_VALID_REPORT_TO_USER = 'received_valid_report_to_user'
    CREATE_COMPLAINT = 'create_complaint'
    COMPLAINT_RESOLVED = 'complaint_resolved'


POPULARITY_POINTS = {
    PopularityActionEnum.LIKE: 10,
    PopularityActionEnum.RECEIVE_LIKE: 20,
    PopularityActionEnum.COMMENT_POST: 25,
    PopularityActionEnum.RECEIVE_COMMENT: 40,
    PopularityActionEnum.CREATE_POST: 100,
    PopularityActionEnum.REPORT_SUSPENDED: 200,
    PopularityActionEnum.REPORT_TOLERATED: -100,
    PopularityActionEnum.RECEIVED_VALID_REPORT_TO_USER: -250,
    PopularityActionEnum.CREATE_COMPLAINT: 100,
    PopularityActionEnum.COMPLAINT_RESOLVED: 200,
}


class ReputationScoreResponse(BaseModel):
    reputation: int


class ReputationLevelResponse(BaseModel):
    reputation_level: str


class PopularityScoreResponse(BaseModel):
    popularity: int
