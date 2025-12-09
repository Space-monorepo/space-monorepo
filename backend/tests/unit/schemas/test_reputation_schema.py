import pytest
from pydantic import ValidationError

from app.api.reputation.schema import (
    POPULARITY_POINTS,
    REPUTATION_POINTS,
    PopularityActionEnum,
    PopularityScoreResponse,
    ReputationActionEnum,
    ReputationLevelEnum,
    ReputationLevelResponse,
    ReputationScoreResponse,
)


@pytest.mark.unit
def test_reputation_level_enum_values():
    assert ReputationLevelEnum.UNDER_OBSERVATION.value == 'under_observation'
    assert ReputationLevelEnum.HELPER.value == 'helper'
    assert ReputationLevelEnum.CONTRIBUTOR.value == 'contributor'
    assert ReputationLevelEnum.LEADER.value == 'leader'


@pytest.mark.unit
def test_reputation_level_enum_count():
    assert len(ReputationLevelEnum) == 4


@pytest.mark.unit
def test_reputation_action_enum_values():
    assert ReputationActionEnum.CREATE_CAMPAIGN.value == 'create_campaign'
    assert ReputationActionEnum.CAMPAIGN_ACCEPTED.value == 'campaign_accepted'
    assert ReputationActionEnum.CAMPAIGN_REJECTED.value == 'campaign_rejected'
    assert ReputationActionEnum.CAMPAIGN_SUPPORT.value == 'campaign_support'
    assert ReputationActionEnum.REPORT_SUSPENDED.value == 'report_suspended'
    assert ReputationActionEnum.REPORT_TOLERATED.value == 'report_tolerated'
    assert (
        ReputationActionEnum.RECEIVED_VALID_REPORT_TO_USER.value
        == 'received_valid_report_to_user'
    )
    assert ReputationActionEnum.CREATE_COMPLAINT.value == 'create_complaint'
    assert ReputationActionEnum.CONFIRM_COMPLAINT.value == 'confirm_complaint'
    assert ReputationActionEnum.COMPLAINT_RESOLVED.value == 'complaint_resolved'
    assert (
        ReputationActionEnum.RESOLVE_COMPLAINT_MODERATOR.value
        == 'resolve_complaint_moderator'
    )


@pytest.mark.unit
def test_reputation_action_enum_count():
    assert len(ReputationActionEnum) == 11


@pytest.mark.unit
def test_popularity_action_enum_values():
    assert PopularityActionEnum.LIKE.value == 'like'
    assert PopularityActionEnum.RECEIVE_LIKE.value == 'receive_like'
    assert PopularityActionEnum.COMMENT_POST.value == 'comment_post'
    assert PopularityActionEnum.RECEIVE_COMMENT.value == 'receive_comment'
    assert PopularityActionEnum.CREATE_POST.value == 'create_post'
    assert PopularityActionEnum.REPORT_SUSPENDED.value == 'report_suspended'
    assert PopularityActionEnum.REPORT_TOLERATED.value == 'report_tolerated'
    assert (
        PopularityActionEnum.RECEIVED_VALID_REPORT_TO_USER.value
        == 'received_valid_report_to_user'
    )
    assert PopularityActionEnum.CREATE_COMPLAINT.value == 'create_complaint'
    assert PopularityActionEnum.COMPLAINT_RESOLVED.value == 'complaint_resolved'


@pytest.mark.unit
def test_popularity_action_enum_count():
    assert len(PopularityActionEnum) == 10


@pytest.mark.unit
def test_reputation_points_mapping():
    assert REPUTATION_POINTS[ReputationActionEnum.CREATE_CAMPAIGN] == 100
    assert REPUTATION_POINTS[ReputationActionEnum.CAMPAIGN_ACCEPTED] == 400
    assert REPUTATION_POINTS[ReputationActionEnum.CAMPAIGN_REJECTED] == -50
    assert REPUTATION_POINTS[ReputationActionEnum.CAMPAIGN_SUPPORT] == 50
    assert REPUTATION_POINTS[ReputationActionEnum.REPORT_SUSPENDED] == 200
    assert REPUTATION_POINTS[ReputationActionEnum.REPORT_TOLERATED] == -100
    assert REPUTATION_POINTS[ReputationActionEnum.RECEIVED_VALID_REPORT_TO_USER] == -250
    assert REPUTATION_POINTS[ReputationActionEnum.CREATE_COMPLAINT] == 100
    assert REPUTATION_POINTS[ReputationActionEnum.CONFIRM_COMPLAINT] == 30
    assert REPUTATION_POINTS[ReputationActionEnum.COMPLAINT_RESOLVED] == 200
    assert REPUTATION_POINTS[ReputationActionEnum.RESOLVE_COMPLAINT_MODERATOR] == 500


@pytest.mark.unit
def test_reputation_points_has_all_actions():
    for action in ReputationActionEnum:
        assert action in REPUTATION_POINTS, f'Missing points for {action}'


@pytest.mark.unit
def test_reputation_points_positive_values():
    positive_actions = [
        ReputationActionEnum.CREATE_CAMPAIGN,
        ReputationActionEnum.CAMPAIGN_ACCEPTED,
        ReputationActionEnum.CAMPAIGN_SUPPORT,
        ReputationActionEnum.REPORT_SUSPENDED,
        ReputationActionEnum.CREATE_COMPLAINT,
        ReputationActionEnum.CONFIRM_COMPLAINT,
        ReputationActionEnum.COMPLAINT_RESOLVED,
        ReputationActionEnum.RESOLVE_COMPLAINT_MODERATOR,
    ]
    for action in positive_actions:
        assert REPUTATION_POINTS[action] > 0


@pytest.mark.unit
def test_reputation_points_negative_values():
    negative_actions = [
        ReputationActionEnum.CAMPAIGN_REJECTED,
        ReputationActionEnum.REPORT_TOLERATED,
        ReputationActionEnum.RECEIVED_VALID_REPORT_TO_USER,
    ]
    for action in negative_actions:
        assert REPUTATION_POINTS[action] < 0


@pytest.mark.unit
def test_popularity_points_mapping():
    assert POPULARITY_POINTS[PopularityActionEnum.LIKE] == 10
    assert POPULARITY_POINTS[PopularityActionEnum.RECEIVE_LIKE] == 20
    assert POPULARITY_POINTS[PopularityActionEnum.COMMENT_POST] == 25
    assert POPULARITY_POINTS[PopularityActionEnum.RECEIVE_COMMENT] == 40
    assert POPULARITY_POINTS[PopularityActionEnum.CREATE_POST] == 100
    assert POPULARITY_POINTS[PopularityActionEnum.REPORT_SUSPENDED] == 200
    assert POPULARITY_POINTS[PopularityActionEnum.REPORT_TOLERATED] == -100
    assert POPULARITY_POINTS[PopularityActionEnum.RECEIVED_VALID_REPORT_TO_USER] == -250
    assert POPULARITY_POINTS[PopularityActionEnum.CREATE_COMPLAINT] == 100
    assert POPULARITY_POINTS[PopularityActionEnum.COMPLAINT_RESOLVED] == 200


@pytest.mark.unit
def test_popularity_points_has_all_actions():
    for action in PopularityActionEnum:
        assert action in POPULARITY_POINTS, f'Missing points for {action}'


@pytest.mark.unit
def test_popularity_points_positive_values():
    positive_actions = [
        PopularityActionEnum.LIKE,
        PopularityActionEnum.RECEIVE_LIKE,
        PopularityActionEnum.COMMENT_POST,
        PopularityActionEnum.RECEIVE_COMMENT,
        PopularityActionEnum.CREATE_POST,
        PopularityActionEnum.REPORT_SUSPENDED,
        PopularityActionEnum.CREATE_COMPLAINT,
        PopularityActionEnum.COMPLAINT_RESOLVED,
    ]
    for action in positive_actions:
        assert POPULARITY_POINTS[action] > 0


@pytest.mark.unit
def test_popularity_points_negative_values():
    negative_actions = [
        PopularityActionEnum.REPORT_TOLERATED,
        PopularityActionEnum.RECEIVED_VALID_REPORT_TO_USER,
    ]
    for action in negative_actions:
        assert POPULARITY_POINTS[action] < 0


@pytest.mark.unit
def test_reputation_score_response_schema():
    response = ReputationScoreResponse(reputation=5000)

    assert response.model_dump() == {'reputation': 5000}


@pytest.mark.unit
def test_reputation_score_response_zero():
    response = ReputationScoreResponse(reputation=0)

    assert response.model_dump() == {'reputation': 0}


@pytest.mark.unit
def test_reputation_score_response_negative():
    response = ReputationScoreResponse(reputation=-100)

    assert response.model_dump() == {'reputation': -100}


@pytest.mark.unit
def test_reputation_score_response_high_value():
    response = ReputationScoreResponse(reputation=999999)

    assert response.model_dump() == {'reputation': 999999}


@pytest.mark.unit
def test_reputation_score_response_missing_field():
    with pytest.raises(ValidationError) as exc_info:
        ReputationScoreResponse()

    errors = exc_info.value.errors()
    assert any(error['type'] == 'missing' for error in errors)
    assert any('reputation' in str(error) for error in errors)


@pytest.mark.unit
def test_reputation_score_response_invalid_type():
    with pytest.raises(ValidationError) as exc_info:
        ReputationScoreResponse(reputation='not a number')

    errors = exc_info.value.errors()
    assert any(error['type'] in ['int_parsing', 'int_type'] for error in errors)


@pytest.mark.unit
def test_reputation_level_response_schema():
    response = ReputationLevelResponse(reputation_level='contributor')

    assert response.model_dump() == {'reputation_level': 'contributor'}


@pytest.mark.unit
def test_reputation_level_response_all_levels():
    levels = ['under_observation', 'helper', 'contributor', 'leader']

    for level in levels:
        response = ReputationLevelResponse(reputation_level=level)
        assert response.reputation_level == level


@pytest.mark.unit
def test_reputation_level_response_missing_field():
    with pytest.raises(ValidationError) as exc_info:
        ReputationLevelResponse()

    errors = exc_info.value.errors()
    assert any(error['type'] == 'missing' for error in errors)
    assert any('reputation_level' in str(error) for error in errors)


@pytest.mark.unit
def test_reputation_level_response_invalid_type():
    with pytest.raises(ValidationError) as exc_info:
        ReputationLevelResponse(reputation_level=123)

    errors = exc_info.value.errors()
    assert any(error['type'] in ['string_type'] for error in errors)


@pytest.mark.unit
def test_popularity_score_response_schema():
    response = PopularityScoreResponse(popularity=3500)

    assert response.model_dump() == {'popularity': 3500}


@pytest.mark.unit
def test_popularity_score_response_zero():
    response = PopularityScoreResponse(popularity=0)

    assert response.model_dump() == {'popularity': 0}


@pytest.mark.unit
def test_popularity_score_response_negative():
    response = PopularityScoreResponse(popularity=-50)

    assert response.model_dump() == {'popularity': -50}


@pytest.mark.unit
def test_popularity_score_response_high_value():
    response = PopularityScoreResponse(popularity=888888)

    assert response.model_dump() == {'popularity': 888888}


@pytest.mark.unit
def test_popularity_score_response_missing_field():
    with pytest.raises(ValidationError) as exc_info:
        PopularityScoreResponse()

    errors = exc_info.value.errors()
    assert any(error['type'] == 'missing' for error in errors)
    assert any('popularity' in str(error) for error in errors)


@pytest.mark.unit
def test_popularity_score_response_invalid_type():
    with pytest.raises(ValidationError) as exc_info:
        PopularityScoreResponse(popularity='not a number')

    errors = exc_info.value.errors()
    assert any(error['type'] in ['int_parsing', 'int_type'] for error in errors)
