from unittest.mock import Mock
from uuid import uuid4

import pytest

from app.api.communities.exceptions import CommunityMemberNotFoundError
from app.api.communities.model import CommunityMember
from app.api.reputation.exceptions import (
    PopularityUpdateError,
    ReputationUpdateError,
)
from app.api.reputation.schema import (
    PopularityActionEnum,
    ReputationActionEnum,
    ReputationLevelEnum,
)
from app.api.reputation.service import ReputationService


@pytest.mark.unit
def test_calculate_level_under_observation():
    """
    Tests the `_calculate_level` method for under observation level.

    Scenario:
    - Given a reputation score less than 3000
    - When the level is calculated
    - Then it should return 'under_observation'
    """
    # Arrange
    mock_tm = Mock()
    service = ReputationService(mock_tm)

    # Act
    level = service._calculate_level(1000)

    # Assert
    assert level == ReputationLevelEnum.UNDER_OBSERVATION.value


@pytest.mark.unit
def test_calculate_level_helper():
    """
    Tests the `_calculate_level` method for helper level.

    Scenario:
    - Given a reputation score between 3000 and 5999
    - When the level is calculated
    - Then it should return 'helper'
    """
    # Arrange
    mock_tm = Mock()
    service = ReputationService(mock_tm)

    # Act
    level = service._calculate_level(4500)

    # Assert
    assert level == ReputationLevelEnum.HELPER.value


@pytest.mark.unit
def test_calculate_level_contributor():
    """
    Tests the `_calculate_level` method for contributor level.

    Scenario:
    - Given a reputation score between 6000 and 8499
    - When the level is calculated
    - Then it should return 'contributor'
    """
    # Arrange
    mock_tm = Mock()
    service = ReputationService(mock_tm)

    # Act
    level = service._calculate_level(7000)

    # Assert
    assert level == ReputationLevelEnum.CONTRIBUTOR.value


@pytest.mark.unit
def test_calculate_level_leader():
    """
    Tests the `_calculate_level` method for leader level.

    Scenario:
    - Given a reputation score of 8500 or more
    - When the level is calculated
    - Then it should return 'leader'
    """
    # Arrange
    mock_tm = Mock()
    service = ReputationService(mock_tm)

    # Act
    level = service._calculate_level(10000)

    # Assert
    assert level == ReputationLevelEnum.LEADER.value


@pytest.mark.unit
def test_get_member_stats_success():
    """
    Tests the `get_member_stats` method.

    Scenario:
    - Given a valid member ID
    - When requesting member stats
    - Then it should return reputation, level, and popularity
    """
    # Arrange
    member_id = uuid4()
    mock_member = Mock(spec=CommunityMember)
    mock_member.reputation = 5000
    mock_member.reputation_level = 'contributor'
    mock_member.popularity = 2500

    mock_tm = Mock()
    mock_member_repo = Mock()
    mock_member_repo.get_by_id.return_value = mock_member

    service = ReputationService(mock_tm)
    service.member_repo = mock_member_repo

    # Act
    stats = service.get_member_stats(member_id)

    # Assert
    mock_member_repo.get_by_id.assert_called_once_with(member_id)
    assert stats['reputation'] == 5000
    assert stats['reputation_level'] == 'contributor'
    assert stats['popularity'] == 2500


@pytest.mark.unit
def test_get_member_stats_member_not_found():
    """
    Tests the `get_member_stats` method when member not found.

    Scenario:
    - Given an invalid member ID
    - When requesting member stats
    - Then it should raise CommunityMemberNotFoundError
    """
    # Arrange
    member_id = uuid4()

    mock_tm = Mock()
    mock_member_repo = Mock()
    mock_member_repo.get_by_id.return_value = None

    service = ReputationService(mock_tm)
    service.member_repo = mock_member_repo

    # Act & Assert
    with pytest.raises(CommunityMemberNotFoundError):
        service.get_member_stats(member_id)

    mock_member_repo.get_by_id.assert_called_once_with(member_id)


@pytest.mark.unit
def test_add_reputation_points_success():
    """
    Tests the `_add_reputation_points` method.

    Scenario:
    - Given a valid member and reputation action
    - When adding reputation points
    - Then member reputation should be updated and level recalculated
    """
    # Arrange
    member_id = uuid4()
    mock_member = Mock(spec=CommunityMember)
    mock_member.reputation = 2000
    mock_member.reputation_level = 'under_observation'

    mock_tm = Mock()
    mock_member_repo = Mock()
    mock_member_repo.get_by_id.return_value = mock_member
    mock_member_repo.save.return_value = mock_member

    service = ReputationService(mock_tm)
    service.member_repo = mock_member_repo

    # Act
    service._add_reputation_points(member_id, ReputationActionEnum.CREATE_CAMPAIGN)

    # Assert
    mock_member_repo.get_by_id.assert_called_once_with(member_id)
    assert mock_member.reputation == 2100  # 2000 + 100
    mock_member_repo.save.assert_called_once()


@pytest.mark.unit
def test_add_reputation_points_negative_capped_at_zero():
    """
    Tests that reputation cannot go below zero.

    Scenario:
    - Given a member with low reputation
    - When losing reputation points that would make it negative
    - Then reputation should be capped at zero
    """
    # Arrange
    member_id = uuid4()
    mock_member = Mock(spec=CommunityMember)
    mock_member.reputation = 50
    mock_member.reputation_level = 'under_observation'

    mock_tm = Mock()
    mock_member_repo = Mock()
    mock_member_repo.get_by_id.return_value = mock_member
    mock_member_repo.save.return_value = mock_member

    service = ReputationService(mock_tm)
    service.member_repo = mock_member_repo

    # Act - REPORT_TOLERATED gives -100 points
    service._add_reputation_points(member_id, ReputationActionEnum.REPORT_TOLERATED)

    # Assert
    assert mock_member.reputation == 0  # Should be capped at 0, not -50


@pytest.mark.unit
def test_add_reputation_points_member_not_found():
    """
    Tests `_add_reputation_points` when member not found.

    Scenario:
    - Given an invalid member ID
    - When trying to add reputation points
    - Then it should raise CommunityMemberNotFoundError
    """
    # Arrange
    member_id = uuid4()

    mock_tm = Mock()
    mock_member_repo = Mock()
    mock_member_repo.get_by_id.return_value = None

    service = ReputationService(mock_tm)
    service.member_repo = mock_member_repo

    # Act & Assert
    with pytest.raises(CommunityMemberNotFoundError):
        service._add_reputation_points(member_id, ReputationActionEnum.CREATE_CAMPAIGN)


@pytest.mark.unit
def test_add_reputation_points_save_error():
    """
    Tests `_add_reputation_points` when save fails.

    Scenario:
    - Given a valid member
    - When saving reputation fails
    - Then it should raise ReputationUpdateError
    """
    # Arrange
    member_id = uuid4()
    mock_member = Mock(spec=CommunityMember)
    mock_member.reputation = 2000

    mock_tm = Mock()
    mock_member_repo = Mock()
    mock_member_repo.get_by_id.return_value = mock_member
    mock_member_repo.save.side_effect = Exception('Database error')

    service = ReputationService(mock_tm)
    service.member_repo = mock_member_repo

    # Act & Assert
    with pytest.raises(ReputationUpdateError):
        service._add_reputation_points(member_id, ReputationActionEnum.CREATE_CAMPAIGN)


@pytest.mark.unit
def test_add_popularity_points_success():
    """
    Tests the `_add_popularity_points` method.

    Scenario:
    - Given a valid member and popularity action
    - When adding popularity points
    - Then member popularity should be updated
    """
    # Arrange
    member_id = uuid4()
    mock_member = Mock(spec=CommunityMember)
    mock_member.popularity = 1000

    mock_tm = Mock()
    mock_member_repo = Mock()
    mock_member_repo.get_by_id.return_value = mock_member
    mock_member_repo.save.return_value = mock_member

    service = ReputationService(mock_tm)
    service.member_repo = mock_member_repo

    # Act
    service._add_popularity_points(member_id, PopularityActionEnum.CREATE_POST)

    # Assert
    mock_member_repo.get_by_id.assert_called_once_with(member_id)
    assert mock_member.popularity == 1100  # 1000 + 100
    mock_member_repo.save.assert_called_once()


@pytest.mark.unit
def test_add_popularity_points_negative_capped_at_zero():
    """
    Tests that popularity cannot go below zero.

    Scenario:
    - Given a member with low popularity
    - When losing popularity points that would make it negative
    - Then popularity should be capped at zero
    """
    # Arrange
    member_id = uuid4()
    mock_member = Mock(spec=CommunityMember)
    mock_member.popularity = 50

    mock_tm = Mock()
    mock_member_repo = Mock()
    mock_member_repo.get_by_id.return_value = mock_member
    mock_member_repo.save.return_value = mock_member

    service = ReputationService(mock_tm)
    service.member_repo = mock_member_repo

    # Act - REPORT_TOLERATED gives -100 points
    service._add_popularity_points(member_id, PopularityActionEnum.REPORT_TOLERATED)

    # Assert
    assert mock_member.popularity == 0  # Should be capped at 0


@pytest.mark.unit
def test_add_popularity_points_save_error():
    """
    Tests `_add_popularity_points` when save fails.

    Scenario:
    - Given a valid member
    - When saving popularity fails
    - Then it should raise PopularityUpdateError
    """
    # Arrange
    member_id = uuid4()
    mock_member = Mock(spec=CommunityMember)
    mock_member.popularity = 1000

    mock_tm = Mock()
    mock_member_repo = Mock()
    mock_member_repo.get_by_id.return_value = mock_member
    mock_member_repo.save.side_effect = Exception('Database error')

    service = ReputationService(mock_tm)
    service.member_repo = mock_member_repo

    # Act & Assert
    with pytest.raises(PopularityUpdateError):
        service._add_popularity_points(member_id, PopularityActionEnum.CREATE_POST)


@pytest.mark.unit
def test_reward_campaign_creation_to_member():
    """
    Tests the `reward_campaign_creation_to_member` method.

    Scenario:
    - Given a campaign author
    - When awarding points for campaign creation
    - Then reputation should increase by 100 points
    """
    # Arrange
    author_id = uuid4()
    mock_member = Mock(spec=CommunityMember)
    mock_member.reputation = 1000

    mock_tm = Mock()
    mock_member_repo = Mock()
    mock_member_repo.get_by_id.return_value = mock_member
    mock_member_repo.save.return_value = mock_member

    service = ReputationService(mock_tm)
    service.member_repo = mock_member_repo

    # Act
    service.reward_campaign_creation_to_member(author_id)

    # Assert
    assert mock_member.reputation == 1100


@pytest.mark.unit
def test_reward_campaign_status_change_approved():
    """
    Tests campaign approval reward.

    Scenario:
    - Given a campaign changing from pending to approved
    - When awarding points for status change
    - Then reputation should increase by 400 points
    """
    # Arrange
    author_id = uuid4()
    mock_member = Mock(spec=CommunityMember)
    mock_member.reputation = 2000

    mock_tm = Mock()
    mock_member_repo = Mock()
    mock_member_repo.get_by_id.return_value = mock_member
    mock_member_repo.save.return_value = mock_member

    service = ReputationService(mock_tm)
    service.member_repo = mock_member_repo

    # Act
    service.reward_campaign_status_change_to_member(author_id, 'pending', 'approved')

    # Assert
    assert mock_member.reputation == 2400  # 2000 + 400


@pytest.mark.unit
def test_reward_campaign_status_change_rejected():
    """
    Tests campaign rejection penalty.

    Scenario:
    - Given a campaign changing from pending to rejected
    - When processing the status change
    - Then reputation should decrease by 50 points
    """
    # Arrange
    author_id = uuid4()
    mock_member = Mock(spec=CommunityMember)
    mock_member.reputation = 2000

    mock_tm = Mock()
    mock_member_repo = Mock()
    mock_member_repo.get_by_id.return_value = mock_member
    mock_member_repo.save.return_value = mock_member

    service = ReputationService(mock_tm)
    service.member_repo = mock_member_repo

    # Act
    service.reward_campaign_status_change_to_member(author_id, 'pending', 'rejected')

    # Assert
    assert mock_member.reputation == 1950  # 2000 - 50


@pytest.mark.unit
def test_reward_campaign_support_to_member():
    """
    Tests the `reward_campaign_support_to_member` method.

    Scenario:
    - Given a member supporting a campaign
    - When awarding support points
    - Then reputation should increase by 50 points
    """
    # Arrange
    supporter_id = uuid4()
    mock_member = Mock(spec=CommunityMember)
    mock_member.reputation = 3000

    mock_tm = Mock()
    mock_member_repo = Mock()
    mock_member_repo.get_by_id.return_value = mock_member
    mock_member_repo.save.return_value = mock_member

    service = ReputationService(mock_tm)
    service.member_repo = mock_member_repo

    # Act
    service.reward_campaign_support_to_member(supporter_id)

    # Assert
    assert mock_member.reputation == 3050


@pytest.mark.unit
def test_reward_post_creation_to_member():
    """
    Tests the `reward_post_creation_to_member` method.

    Scenario:
    - Given a member creating a post
    - When awarding post creation points
    - Then popularity should increase by 100 points
    """
    # Arrange
    author_id = uuid4()
    mock_member = Mock(spec=CommunityMember)
    mock_member.popularity = 500

    mock_tm = Mock()
    mock_member_repo = Mock()
    mock_member_repo.get_by_id.return_value = mock_member
    mock_member_repo.save.return_value = mock_member

    service = ReputationService(mock_tm)
    service.member_repo = mock_member_repo

    # Act
    service.reward_post_creation_to_member(author_id)

    # Assert
    assert mock_member.popularity == 600


@pytest.mark.unit
def test_reward_post_like_to_member():
    """
    Tests the `reward_post_like_to_member` method.

    Scenario:
    - Given a member liking a post
    - When awarding like points
    - Then liker gets 10 points and author gets 20 points
    """
    # Arrange
    liker_id = uuid4()
    author_id = uuid4()

    mock_liker = Mock(spec=CommunityMember)
    mock_liker.popularity = 100

    mock_author = Mock(spec=CommunityMember)
    mock_author.popularity = 500

    mock_tm = Mock()
    mock_member_repo = Mock()

    def get_by_id_side_effect(member_id):
        if member_id == liker_id:
            return mock_liker
        elif member_id == author_id:
            return mock_author
        return None

    mock_member_repo.get_by_id.side_effect = get_by_id_side_effect
    mock_member_repo.save.return_value = Mock()

    service = ReputationService(mock_tm)
    service.member_repo = mock_member_repo

    # Act
    service.reward_post_like_to_member(liker_id, author_id)

    # Assert
    assert mock_liker.popularity == 110  # 100 + 10 (LIKE)
    assert mock_author.popularity == 520  # 500 + 20 (RECEIVE_LIKE)


@pytest.mark.unit
def test_reward_comment_creation_to_member():
    """
    Tests the `award_comment_creation` method.

    Scenario:
    - Given a member commenting on a post
    - When awarding comment points
    - Then commenter gets 25 points and post author gets 40 points
    """
    # Arrange
    commenter_id = uuid4()
    post_author_id = uuid4()

    mock_commenter = Mock(spec=CommunityMember)
    mock_commenter.popularity = 200

    mock_author = Mock(spec=CommunityMember)
    mock_author.popularity = 800

    mock_tm = Mock()
    mock_member_repo = Mock()

    def get_by_id_side_effect(member_id):
        if member_id == commenter_id:
            return mock_commenter
        elif member_id == post_author_id:
            return mock_author
        return None

    mock_member_repo.get_by_id.side_effect = get_by_id_side_effect
    mock_member_repo.save.return_value = Mock()

    service = ReputationService(mock_tm)
    service.member_repo = mock_member_repo

    # Act
    service.reward_comment_creation_to_member(commenter_id, post_author_id)

    # Assert
    assert mock_commenter.popularity == 225  # 200 + 25 (COMMENT_POST)
    assert mock_author.popularity == 840  # 800 + 40 (RECEIVE_COMMENT)


@pytest.mark.unit
def test_reward_comment_like_to_member():
    """
    Tests the `reward_comment_like_to_member` method.

    Scenario:
    - Given a member liking a comment
    - When awarding like points
    - Then liker gets 10 points and comment author gets 20 points
    """
    # Arrange
    liker_id = uuid4()
    comment_author_id = uuid4()

    mock_liker = Mock(spec=CommunityMember)
    mock_liker.popularity = 150

    mock_author = Mock(spec=CommunityMember)
    mock_author.popularity = 600

    mock_tm = Mock()
    mock_member_repo = Mock()

    def get_by_id_side_effect(member_id):
        if member_id == liker_id:
            return mock_liker
        elif member_id == comment_author_id:
            return mock_author
        return None

    mock_member_repo.get_by_id.side_effect = get_by_id_side_effect
    mock_member_repo.save.return_value = Mock()

    service = ReputationService(mock_tm)
    service.member_repo = mock_member_repo

    # Act
    service.reward_comment_like_to_member(liker_id, comment_author_id)

    # Assert
    assert mock_liker.popularity == 160  # 150 + 10 (LIKE)
    assert mock_author.popularity == 620  # 600 + 20 (RECEIVE_LIKE)


@pytest.mark.unit
def test_reward_complaint_creation():
    """
    Tests the `reward_complaint_creation` method.

    Scenario:
    - Given a member creating a complaint
    - When awarding complaint creation points
    - Then both reputation and popularity should increase by 100 points each
    """
    # Arrange
    author_id = uuid4()
    mock_member = Mock(spec=CommunityMember)
    mock_member.reputation = 1000
    mock_member.popularity = 500

    mock_tm = Mock()
    mock_member_repo = Mock()
    mock_member_repo.get_by_id.return_value = mock_member
    mock_member_repo.save.return_value = mock_member

    service = ReputationService(mock_tm)
    service.member_repo = mock_member_repo

    # Act
    service.reward_complaint_creation_to_member(author_id)

    # Assert
    assert mock_member.reputation == 1100
    assert mock_member.popularity == 600


@pytest.mark.unit
def test_reward_complaint_confirmation_to_member():
    """
    Tests the `reward_complaint_confirmation_to_member` method.

    Scenario:
    - Given a member confirming a complaint
    - When awarding confirmation points
    - Then reputation should increase by 30 points
    """
    # Arrange
    member_id = uuid4()
    mock_member = Mock(spec=CommunityMember)
    mock_member.reputation = 2000

    mock_tm = Mock()
    mock_member_repo = Mock()
    mock_member_repo.get_by_id.return_value = mock_member
    mock_member_repo.save.return_value = mock_member

    service = ReputationService(mock_tm)
    service.member_repo = mock_member_repo

    # Act
    service.reward_complaint_confirmation_to_member(member_id)

    # Assert
    assert mock_member.reputation == 2030


@pytest.mark.unit
def test_reward_complaint_resolution_to_member():
    """
    Tests the `reward_complaint_resolution_to_member` method.

    Scenario:
    - Given a post whose complaint is resolved
    - When awarding resolution points to the post author
    - Then both reputation and popularity should increase by 200 points each
    """
    # Arrange
    author_id = uuid4()
    community_id = uuid4()
    
    # Mock do Post
    mock_post = Mock()
    mock_post.user = Mock()
    mock_post.user.id = uuid4()
    mock_post.community = Mock()
    mock_post.community.id = community_id
    
    # Mock do author_member
    mock_author_member = Mock()
    mock_author_member.id = author_id
    mock_author_member.reputation = 3000
    mock_author_member.popularity = 1500
    
    mock_tm = Mock()
    mock_member_repo = Mock()
    mock_member_repo.get_by_id.return_value = mock_author_member
    mock_member_repo.save.return_value = mock_author_member
    
    mock_community_service = Mock()
    mock_community_service.get_member_association.return_value = mock_author_member
    
    service = ReputationService(mock_tm)
    service.member_repo = mock_member_repo
    service.community_service = mock_community_service
    
    # Act
    service.reward_complaint_resolution_to_member(mock_post)
    
    # Assert
    assert mock_author_member.reputation == 3200
    assert mock_author_member.popularity == 1700
    mock_community_service.get_member_association.assert_called_once_with(
        mock_post.user.id, mock_post.community.id
    )


@pytest.mark.unit
def test_reward_complaint_resolution_to_moderator():
    """
    Tests the `reward_complaint_resolution_to_moderator` method.

    Scenario:
    - Given a moderator resolving a complaint
    - When awarding moderator resolution points
    - Then reputation should increase by 500 points
    """
    # Arrange
    moderator_id = uuid4()
    mock_member = Mock(spec=CommunityMember)
    mock_member.reputation = 5000

    mock_tm = Mock()
    mock_member_repo = Mock()
    mock_member_repo.get_by_id.return_value = mock_member
    mock_member_repo.save.return_value = mock_member

    service = ReputationService(mock_tm)
    service.member_repo = mock_member_repo

    # Act
    service.reward_complaint_resolution_to_moderator(moderator_id)

    # Assert
    assert mock_member.reputation == 5500
