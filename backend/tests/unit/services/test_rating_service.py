import uuid
import pytest

from app.api.rating.model import Rating
from app.api.rating.schema import RatingCreate, RatingUpdate
from app.api.rating.service import RatingService
from app.api.rating.exceptions import (
    RatingNotFoundError,
    RatingAlreadyExistsError,
    UnexpectedRatingError
)
from app.api.communities.exceptions import CommunityNotFoundError, CommunityMemberNotFoundError
from app.utils.schema import PaginationSearchParams


def test_create_rating_service(session_sql, transaction_manager, community_member_on_db):
    rating_create = RatingCreate(
        user_id=community_member_on_db.user_id,
        community_id=community_member_on_db.community_id,
        rating=5,
        title='Excellent Community!',
        description='Great experience with this community',
    )

    rating = RatingService(transaction_manager).create_rating(rating_create)
    
    assert rating.id is not None
    assert rating.rating == 5
    assert rating.title == 'Excellent Community!'
    assert rating.description == 'Great experience with this community'
    assert rating.user_id == community_member_on_db.user_id
    assert rating.community_id == community_member_on_db.community_id

    rating_db = session_sql.query(Rating).filter(Rating.id == rating.id).first()
    assert rating_db is not None
    assert rating_db.rating == 5
    assert rating_db.title == 'Excellent Community!'
    assert rating_db.user_id == community_member_on_db.user_id
    assert rating_db.community_id == community_member_on_db.community_id


def test_create_rating_without_description_service(session_sql, transaction_manager, community_member_on_db):
    rating_create = RatingCreate(
        user_id=community_member_on_db.user_id,
        community_id=community_member_on_db.community_id,
        rating=3,
        title='Average Community',
        description=None,
    )

    rating = RatingService(transaction_manager).create_rating(rating_create)
    
    assert rating.id is not None
    assert rating.rating == 3
    assert rating.title == 'Average Community'
    assert rating.description is None
    assert rating.user_id == community_member_on_db.user_id
    assert rating.community_id == community_member_on_db.community_id

    rating_db = session_sql.query(Rating).filter(Rating.id == rating.id).first()
    assert rating_db is not None
    assert rating_db.rating == 3
    assert rating_db.description is None


def test_create_rating_minimum_rating_service(session_sql, transaction_manager, community_member_on_db):
    rating_create = RatingCreate(
        user_id=community_member_on_db.user_id,
        community_id=community_member_on_db.community_id,
        rating=1,
        title='Poor Community',
        description='Not a good experience',
    )

    rating = RatingService(transaction_manager).create_rating(rating_create)
    
    assert rating.id is not None
    assert rating.rating == 1
    assert rating.title == 'Poor Community'

    rating_db = session_sql.query(Rating).filter(Rating.id == rating.id).first()
    assert rating_db is not None
    assert rating_db.rating == 1


def test_create_rating_maximum_rating_service(session_sql, transaction_manager, community_member_on_db):
    rating_create = RatingCreate(
        user_id=community_member_on_db.user_id,
        community_id=community_member_on_db.community_id,
        rating=5,
        title='Perfect Community',
        description='Excellent experience',
    )

    rating = RatingService(transaction_manager).create_rating(rating_create)
    
    assert rating.id is not None
    assert rating.rating == 5
    assert rating.title == 'Perfect Community'

    rating_db = session_sql.query(Rating).filter(Rating.id == rating.id).first()
    assert rating_db is not None
    assert rating_db.rating == 5


def test_create_rating_duplicate_raises_exception(transaction_manager, rating_on_db):
    rating_create = RatingCreate(
        user_id=rating_on_db.user_id,
        community_id=rating_on_db.community_id,
        rating=4,
        title='Another Rating',
        description='This should fail',
    )

    with pytest.raises(RatingAlreadyExistsError, match='User has already rated this community'):
        RatingService(transaction_manager).create_rating(rating_create)


def test_create_rating_community_not_found_raises_exception(transaction_manager, user_on_db):
    rating_create = RatingCreate(
        user_id=user_on_db.id,
        community_id=uuid.uuid4(),
        rating=5,
        title='Test Rating',
        description='This should fail',
    )

    with pytest.raises(CommunityNotFoundError, match='Community with id .* not found'):
        RatingService(transaction_manager).create_rating(rating_create)


def test_create_rating_user_not_member_raises_exception(transaction_manager, user_on_db, community_on_db):
    rating_create = RatingCreate(
        user_id=user_on_db.id,
        community_id=community_on_db.id,
        rating=5,
        title='Test Rating',
        description='This should fail',
    )

    with pytest.raises(CommunityMemberNotFoundError, match='User with id .* not found in community with id .*'):
        RatingService(transaction_manager).create_rating(rating_create)


def test_get_rating_service(transaction_manager, rating_on_db):
    rating = RatingService(transaction_manager).get_rating(rating_on_db.id)
    
    assert rating is not None
    assert rating.id == rating_on_db.id
    assert rating.rating == rating_on_db.rating
    assert rating.title == rating_on_db.title
    assert rating.description == rating_on_db.description
    assert rating.user_id == rating_on_db.user_id
    assert rating.community_id == rating_on_db.community_id


def test_get_rating_not_found_raises_exception(transaction_manager):
    non_existent_id = uuid.uuid4()
    
    with pytest.raises(RatingNotFoundError, match='Rating not found'):
        RatingService(transaction_manager).get_rating(non_existent_id)


def test_list_ratings_by_community_service(transaction_manager, rating_on_db):
    params = PaginationSearchParams(offset=0, limit=10)
    
    ratings = RatingService(transaction_manager).list_ratings_by_community(
        rating_on_db.community_id, params
    )
    
    assert ratings is not None
    assert ratings.items is not None
    assert len(ratings.items) == 1
    assert ratings.total == 1
    assert ratings.has_more is False
    assert ratings.current_offset == 0
    assert ratings.current_limit == 10
    
    assert ratings.items[0].community_id == rating_on_db.community_id


def test_list_ratings_by_community_with_pagination_service(transaction_manager, rating_on_db):
    params = PaginationSearchParams(offset=0, limit=1)
    
    ratings = RatingService(transaction_manager).list_ratings_by_community(
        rating_on_db.community_id, params
    )
    
    assert ratings is not None
    assert ratings.items is not None
    assert len(ratings.items) == 1
    assert ratings.total == 1
    assert ratings.has_more is False
    assert ratings.current_offset == 0
    assert ratings.current_limit == 1


def test_list_ratings_by_community_empty_service(transaction_manager, community_on_db):
    params = PaginationSearchParams(offset=0, limit=10)
    
    ratings = RatingService(transaction_manager).list_ratings_by_community(
        community_on_db.id, params
    )
    
    assert ratings is not None
    assert ratings.items is not None
    assert len(ratings.items) == 0
    assert ratings.total == 0
    assert ratings.has_more is False


def test_update_rating_service(session_sql, transaction_manager, rating_on_db):
    rating_update = RatingUpdate(
        rating=4,
        title='Updated Title',
        description='Updated description'
    )
    
    rating = RatingService(transaction_manager).update_rating(rating_on_db.id, rating_update)
    
    assert rating is not None
    assert rating.rating == 4
    assert rating.title == 'Updated Title'
    assert rating.description == 'Updated description'
    assert rating.id == rating_on_db.id

    rating_db = session_sql.query(Rating).filter(Rating.id == rating_on_db.id).first()
    assert rating_db is not None
    assert rating_db.rating == 4
    assert rating_db.title == 'Updated Title'
    assert rating_db.description == 'Updated description'


def test_update_rating_partial_service(session_sql, transaction_manager, rating_on_db):
    original_title = rating_on_db.title
    original_description = rating_on_db.description
    
    rating_update = RatingUpdate(rating=2)
    
    rating = RatingService(transaction_manager).update_rating(rating_on_db.id, rating_update)
    
    assert rating is not None
    assert rating.rating == 2
    assert rating.title == original_title
    assert rating.description == original_description

    rating_db = session_sql.query(Rating).filter(Rating.id == rating_on_db.id).first()
    assert rating_db is not None
    assert rating_db.rating == 2
    assert rating_db.title == original_title
    assert rating_db.description == original_description


def test_update_rating_set_description_to_none_service(session_sql, transaction_manager, rating_on_db):
    original_description = rating_on_db.description
    rating_update = RatingUpdate(description=None)
    
    rating = RatingService(transaction_manager).update_rating(rating_on_db.id, rating_update)
    
    assert rating is not None
    assert rating.description == original_description

    rating_db = session_sql.query(Rating).filter(Rating.id == rating_on_db.id).first()
    assert rating_db is not None
    assert rating_db.description == original_description


def test_update_rating_not_found_raises_exception(transaction_manager):
    non_existent_id = uuid.uuid4()
    rating_update = RatingUpdate(rating=3, title='Updated Title')
    
    with pytest.raises(UnexpectedRatingError, match='Unexpected error updating rating'):
        RatingService(transaction_manager).update_rating(non_existent_id, rating_update)


def test_delete_rating_service(session_sql, transaction_manager, rating_on_db):
    result = RatingService(transaction_manager).delete_rating(rating_on_db.id)
    
    assert result is True

    rating_db = session_sql.query(Rating).filter(Rating.id == rating_on_db.id).first()
    assert rating_db is None


def test_delete_rating_not_found_raises_exception(transaction_manager):
    non_existent_id = uuid.uuid4()
    
    with pytest.raises(UnexpectedRatingError, match='Unexpected error deleting rating'):
        RatingService(transaction_manager).delete_rating(non_existent_id)
