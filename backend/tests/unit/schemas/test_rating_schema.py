import uuid
from datetime import datetime

import pytest
from pydantic import ValidationError

from app.api.rating.schema import (
    RatingBase,
    RatingCreate,
    RatingUpdate,
    RatingResponse,
)


def test_rating_base_schema():
    rating = RatingBase(
        rating=5,
        title='Excellent Community!',
        description='Loved the experience and the members.',
    )

    expected_data = {
        'rating': 5,
        'title': 'Excellent Community!',
        'description': 'Loved the experience and the members.',
    }

    assert rating.model_dump() == expected_data


def test_rating_base_without_description():
    rating = RatingBase(
        rating=4,
        title='Good Community',
    )

    expected_data = {
        'rating': 4,
        'title': 'Good Community',
        'description': None,
    }

    assert rating.model_dump() == expected_data


def test_rating_base_minimum_rating():
    rating = RatingBase(
        rating=1,  # Minimum allowed rating
        title='Poor Community',
        description='Not satisfied',
    )

    expected_data = {
        'rating': 1,
        'title': 'Poor Community',
        'description': 'Not satisfied',
    }

    assert rating.model_dump() == expected_data


def test_rating_base_maximum_rating():
    rating = RatingBase(
        rating=5,  # Maximum allowed rating
        title='Perfect Community',
        description='Absolutely amazing',
    )

    expected_data = {
        'rating': 5,
        'title': 'Perfect Community',
        'description': 'Absolutely amazing',
    }

    assert rating.model_dump() == expected_data


def test_rating_create_schema():
    user_id = str(uuid.uuid4())
    community_id = str(uuid.uuid4())

    rating = RatingCreate(
        user_id=user_id,
        community_id=community_id,
        rating=5,
        title='Excellent Community!',
        description='Loved the experience and the members.',
    )

    expected_data = {
        'user_id': user_id,
        'community_id': community_id,
        'rating': 5,
        'title': 'Excellent Community!',
        'description': 'Loved the experience and the members.',
    }

    assert rating.model_dump() == expected_data


def test_rating_create_without_description():
    user_id = str(uuid.uuid4())
    community_id = str(uuid.uuid4())

    rating = RatingCreate(
        user_id=user_id,
        community_id=community_id,
        rating=3,
        title='Average Community',
    )

    expected_data = {
        'user_id': user_id,
        'community_id': community_id,
        'rating': 3,
        'title': 'Average Community',
        'description': None,
    }

    assert rating.model_dump() == expected_data


def test_rating_update_schema_complete():
    rating = RatingUpdate(
        rating=4,
        title='Updated Rating',
        description='Updated description',
    )

    expected_data = {
        'rating': 4,
        'title': 'Updated Rating',
        'description': 'Updated description',
    }

    assert rating.model_dump() == expected_data


def test_rating_update_partial_rating_only():
    rating = RatingUpdate(rating=2)

    expected_data = {
        'rating': 2,
        'title': None,
        'description': None,
    }

    assert rating.model_dump() == expected_data


def test_rating_update_partial_title_only():
    rating = RatingUpdate(title='New Title')

    expected_data = {
        'rating': None,
        'title': 'New Title',
        'description': None,
    }

    assert rating.model_dump() == expected_data


def test_rating_update_partial_description_only():
    rating = RatingUpdate(description='New description')

    expected_data = {
        'rating': None,
        'title': None,
        'description': 'New description',
    }

    assert rating.model_dump() == expected_data


def test_rating_update_empty():
    rating = RatingUpdate()

    expected_data = {
        'rating': None,
        'title': None,
        'description': None,
    }

    assert rating.model_dump() == expected_data


def test_rating_response_schema():
    rating_id = uuid.uuid4()
    user_id = uuid.uuid4()
    community_id = uuid.uuid4()
    created_at = datetime.now()
    updated_at = datetime.now()

    rating = RatingResponse(
        id=rating_id,
        user_id=user_id,
        community_id=community_id,
        rating=5,
        title='Excellent Community!',
        description='Loved the experience and the members.',
        created_at=created_at,
        updated_at=updated_at,
    )

    expected_data = {
        'id': rating_id,
        'user_id': user_id,
        'community_id': community_id,
        'rating': 5,
        'title': 'Excellent Community!',
        'description': 'Loved the experience and the members.',
        'created_at': created_at,
        'updated_at': updated_at,
    }

    assert rating.model_dump() == expected_data


def test_rating_response_without_description():
    rating_id = uuid.uuid4()
    user_id = uuid.uuid4()
    community_id = uuid.uuid4()
    created_at = datetime.now()
    updated_at = datetime.now()

    rating = RatingResponse(
        id=rating_id,
        user_id=user_id,
        community_id=community_id,
        rating=3,
        title='Average Community',
        description=None,
        created_at=created_at,
        updated_at=updated_at,
    )

    expected_data = {
        'id': rating_id,
        'user_id': user_id,
        'community_id': community_id,
        'rating': 3,
        'title': 'Average Community',
        'description': None,
        'created_at': created_at,
        'updated_at': updated_at,
    }

    assert rating.model_dump() == expected_data


# Validation Error Tests
def test_rating_base_invalid_rating_below_minimum():
    with pytest.raises(ValidationError) as exc_info:
        RatingBase(
            rating=0,  # Below minimum (1)
            title='Invalid Rating',
        )

    errors = exc_info.value.errors()
    assert any(error['type'] == 'greater_than_equal' for error in errors)
    assert any(error['input'] == 0 for error in errors)


def test_rating_base_invalid_rating_above_maximum():
    with pytest.raises(ValidationError) as exc_info:
        RatingBase(
            rating=6,  # Above maximum (5)
            title='Invalid Rating',
        )

    errors = exc_info.value.errors()
    assert any(error['type'] == 'less_than_equal' for error in errors)
    assert any(error['input'] == 6 for error in errors)


def test_rating_base_invalid_empty_title():
    with pytest.raises(ValidationError) as exc_info:
        RatingBase(
            rating=5,
            title='',  # Empty string
        )

    errors = exc_info.value.errors()
    assert any(error['type'] == 'string_too_short' for error in errors)


def test_rating_base_invalid_title_too_long():
    long_title = 'a' * 256  # Exceeds max_length of 255

    with pytest.raises(ValidationError) as exc_info:
        RatingBase(
            rating=5,
            title=long_title,
        )

    errors = exc_info.value.errors()
    assert any(error['type'] == 'string_too_long' for error in errors)


def test_rating_base_invalid_description_too_long():
    long_description = 'a' * 1001  # Exceeds max_length of 1000

    with pytest.raises(ValidationError) as exc_info:
        RatingBase(
            rating=5,
            title='Valid Title',
            description=long_description,
        )

    errors = exc_info.value.errors()
    assert any(error['type'] == 'string_too_long' for error in errors)


def test_rating_base_missing_required_rating():
    with pytest.raises(ValidationError) as exc_info:
        RatingBase(title='Missing Rating')

    errors = exc_info.value.errors()
    assert any(error['type'] == 'missing' and 'rating' in str(error) for error in errors)


def test_rating_base_missing_required_title():
    with pytest.raises(ValidationError) as exc_info:
        RatingBase(rating=5)

    errors = exc_info.value.errors()
    assert any(error['type'] == 'missing' and 'title' in str(error) for error in errors)


def test_rating_create_invalid_missing_user_id():
    community_id = uuid.uuid4()

    with pytest.raises(ValidationError) as exc_info:
        RatingCreate(
            community_id=community_id,
            rating=5,
            title='Test Rating',
        )

    errors = exc_info.value.errors()
    assert any(
        error['type'] == 'missing' and 'user_id' in str(error) for error in errors
    )


def test_rating_create_invalid_missing_community_id():
    user_id = uuid.uuid4()

    with pytest.raises(ValidationError) as exc_info:
        RatingCreate(
            user_id=user_id,
            rating=5,
            title='Test Rating',
        )

    errors = exc_info.value.errors()
    assert any(
        error['type'] == 'missing' and 'community_id' in str(error) for error in errors
    )


def test_rating_update_invalid_rating_below_minimum():
    with pytest.raises(ValidationError) as exc_info:
        RatingUpdate(rating=0)  # Below minimum (1)

    errors = exc_info.value.errors()
    assert any(error['type'] == 'greater_than_equal' for error in errors)


def test_rating_update_invalid_rating_above_maximum():
    with pytest.raises(ValidationError) as exc_info:
        RatingUpdate(rating=6)  # Above maximum (5)

    errors = exc_info.value.errors()
    assert any(error['type'] == 'less_than_equal' for error in errors)


def test_rating_update_invalid_empty_title():
    with pytest.raises(ValidationError) as exc_info:
        RatingUpdate(title='')  # Empty string

    errors = exc_info.value.errors()
    assert any(error['type'] == 'string_too_short' for error in errors)


def test_rating_update_invalid_title_too_long():
    long_title = 'a' * 256  # Exceeds max_length of 255

    with pytest.raises(ValidationError) as exc_info:
        RatingUpdate(title=long_title)

    errors = exc_info.value.errors()
    assert any(error['type'] == 'string_too_long' for error in errors)


def test_rating_update_invalid_description_too_long():
    long_description = 'a' * 1001  # Exceeds max_length of 1000

    with pytest.raises(ValidationError) as exc_info:
        RatingUpdate(description=long_description)

    errors = exc_info.value.errors()
    assert any(error['type'] == 'string_too_long' for error in errors)


def test_rating_response_invalid_missing_id():
    user_id = uuid.uuid4()
    community_id = uuid.uuid4()

    with pytest.raises(ValidationError) as exc_info:
        RatingResponse(
            user_id=user_id,
            community_id=community_id,
            rating=5,
            title='Test Rating',
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

    errors = exc_info.value.errors()
    assert any(error['type'] == 'missing' and 'id' in str(error) for error in errors)


def test_rating_response_invalid_missing_user_id():
    rating_id = uuid.uuid4()
    community_id = uuid.uuid4()

    with pytest.raises(ValidationError) as exc_info:
        RatingResponse(
            id=rating_id,
            community_id=community_id,
            rating=5,
            title='Test Rating',
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

    errors = exc_info.value.errors()
    assert any(
        error['type'] == 'missing' and 'user_id' in str(error) for error in errors
    )


def test_rating_response_invalid_missing_community_id():
    rating_id = uuid.uuid4()
    user_id = uuid.uuid4()

    with pytest.raises(ValidationError) as exc_info:
        RatingResponse(
            id=rating_id,
            user_id=user_id,
            rating=5,
            title='Test Rating',
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

    errors = exc_info.value.errors()
    assert any(
        error['type'] == 'missing' and 'community_id' in str(error) for error in errors
    )


def test_rating_response_invalid_missing_timestamps():
    rating_id = uuid.uuid4()
    user_id = uuid.uuid4()
    community_id = uuid.uuid4()

    with pytest.raises(ValidationError) as exc_info:
        RatingResponse(
            id=rating_id,
            user_id=user_id,
            community_id=community_id,
            rating=5,
            title='Test Rating',
        )

    errors = exc_info.value.errors()
    assert any(
        error['type'] == 'missing' and 'created_at' in str(error) for error in errors
    )
    assert any(
        error['type'] == 'missing' and 'updated_at' in str(error) for error in errors
    )
