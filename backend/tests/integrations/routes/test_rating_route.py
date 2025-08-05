import uuid
from fastapi import status

from app.api.rating.model import Rating
from app.api.rating.schema import RatingCreate, RatingUpdate


def test_create_rating_route(authenticate_client, community_member_on_db):
    rating_create = RatingCreate(
        user_id=community_member_on_db.user_id,
        community_id=community_member_on_db.community_id,
        rating=5,
        title='Excellent Community!',
        description='Great experience with this community',
    )

    response = authenticate_client.post(
        f'/ratings/{community_member_on_db.community_id}/create-rating',
        json=rating_create.model_dump(mode='json'),
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    
    response_data = response.json()
    assert response_data['rating'] == rating_create.rating
    assert response_data['title'] == rating_create.title
    assert response_data['description'] == rating_create.description
    assert response_data['user_id'] == str(rating_create.user_id)
    assert response_data['community_id'] == str(rating_create.community_id)
    assert response_data['id'] is not None
    assert response_data['created_at'] is not None
    assert response_data['updated_at'] is not None


def test_create_rating_without_description_route(authenticate_client, community_member_on_db):
    rating_create = RatingCreate(
        user_id=community_member_on_db.user_id,
        community_id=community_member_on_db.community_id,
        rating=3,
        title='Average Community',
        description=None,
    )

    response = authenticate_client.post(
        f'/ratings/{community_member_on_db.community_id}/create-rating',
        json=rating_create.model_dump(mode='json'),
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    
    response_data = response.json()
    assert response_data['rating'] == rating_create.rating
    assert response_data['title'] == rating_create.title
    assert response_data['description'] is None
    assert response_data['user_id'] == str(rating_create.user_id)
    assert response_data['community_id'] == str(rating_create.community_id)


def test_create_rating_minimum_rating_route(authenticate_client, community_member_on_db):
    rating_create = RatingCreate(
        user_id=community_member_on_db.user_id,
        community_id=community_member_on_db.community_id,
        rating=1,  # Minimum allowed rating
        title='Poor Community',
        description='Not a good experience',
    )

    response = authenticate_client.post(
        f'/ratings/{community_member_on_db.community_id}/create-rating',
        json=rating_create.model_dump(mode='json'),
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    
    response_data = response.json()
    assert response_data['rating'] == 1
    assert response_data['title'] == rating_create.title


def test_create_rating_maximum_rating_route(authenticate_client, community_member_on_db):
    rating_create = RatingCreate(
        user_id=community_member_on_db.user_id,
        community_id=community_member_on_db.community_id,
        rating=5,  # Maximum allowed rating
        title='Perfect Community',
        description='Excellent experience',
    )

    response = authenticate_client.post(
        f'/ratings/{community_member_on_db.community_id}/create-rating',
        json=rating_create.model_dump(mode='json'),
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    
    response_data = response.json()
    assert response_data['rating'] == 5
    assert response_data['title'] == rating_create.title


def test_create_rating_duplicate_returns_conflict(authenticate_client, rating_on_db):
    rating_create = RatingCreate(
        user_id=rating_on_db.user_id,
        community_id=rating_on_db.community_id,
        rating=4,
        title='Another Rating',
        description='This should fail',
    )

    response = authenticate_client.post(
        f'/ratings/{rating_on_db.community_id}/create-rating',
        json=rating_create.model_dump(mode='json'),
    )
    
    assert response.status_code == status.HTTP_409_CONFLICT
    assert 'already rated' in response.json()['message']


def test_create_rating_invalid_rating_returns_validation_error(authenticate_client, community_member_on_db):
    rating_create_data = {
        'user_id': str(community_member_on_db.user_id),
        'community_id': str(community_member_on_db.community_id),
        'rating': 6,  # Invalid rating (> 5)
        'title': 'Invalid Rating',
        'description': 'This should fail',
    }

    response = authenticate_client.post(
        f'/ratings/{community_member_on_db.community_id}/create-rating',
        json=rating_create_data,
    )
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_create_rating_empty_title_returns_validation_error(authenticate_client, community_member_on_db):
    rating_create_data = {
        'user_id': str(community_member_on_db.user_id),
        'community_id': str(community_member_on_db.community_id),
        'rating': 5,
        'title': '',  # Empty title
        'description': 'This should fail',
    }

    response = authenticate_client.post(
        f'/ratings/{community_member_on_db.community_id}/create-rating',
        json=rating_create_data,
    )
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_get_rating_route(authenticate_client, rating_on_db):
    response = authenticate_client.get(
        f'/ratings/{rating_on_db.community_id}/rating/{rating_on_db.id}'
    )
    
    assert response.status_code == status.HTTP_200_OK
    
    response_data = response.json()
    assert response_data['id'] == str(rating_on_db.id)
    assert response_data['rating'] == rating_on_db.rating
    assert response_data['title'] == rating_on_db.title
    assert response_data['description'] == rating_on_db.description
    assert response_data['user_id'] == str(rating_on_db.user_id)
    assert response_data['community_id'] == str(rating_on_db.community_id)
    assert response_data['created_at'] is not None
    assert response_data['updated_at'] is not None


def test_get_rating_not_found_route(authenticate_client, community_member_on_db):
    non_existent_id = uuid.uuid4()
    
    response = authenticate_client.get(
        f'/ratings/{community_member_on_db.community_id}/rating/{non_existent_id}'
    )
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert 'not found' in response.json()['message']


def test_list_ratings_by_community_route(authenticate_client, rating_on_db):
    response = authenticate_client.get(
        f'/ratings/{rating_on_db.community_id}/list-ratings'
    )
    
    assert response.status_code == status.HTTP_200_OK
    
    response_data = response.json()
    assert response_data['total'] == 1
    assert response_data['has_more'] is False
    assert response_data['current_offset'] == 0
    assert response_data['current_limit'] == 10
    assert len(response_data['items']) == 1
    
    # Check that the rating belongs to the community
    assert response_data['items'][0]['community_id'] == str(rating_on_db.community_id)


def test_list_ratings_by_community_with_pagination_route(authenticate_client, rating_on_db):
    response = authenticate_client.get(
        f'/ratings/{rating_on_db.community_id}/list-ratings?offset=0&limit=1'
    )
    
    assert response.status_code == status.HTTP_200_OK
    
    response_data = response.json()
    assert response_data['total'] == 1
    assert response_data['has_more'] is False
    assert response_data['current_offset'] == 0
    assert response_data['current_limit'] == 1
    assert len(response_data['items']) == 1


def test_list_ratings_by_community_empty_route(authenticate_client, community_member_on_db):
    response = authenticate_client.get(
        f'/ratings/{community_member_on_db.community_id}/list-ratings'
    )
    
    assert response.status_code == status.HTTP_200_OK
    
    response_data = response.json()
    assert response_data['total'] == 0
    assert response_data['has_more'] is False
    assert len(response_data['items']) == 0


def test_update_rating_route(authenticate_client, rating_on_db):
    rating_update = RatingUpdate(
        rating=4,
        title='Updated Title',
        description='Updated description'
    )

    response = authenticate_client.patch(
        f'/ratings/{rating_on_db.community_id}/rating/{rating_on_db.id}',
        json=rating_update.model_dump(mode='json'),
    )
    
    assert response.status_code == status.HTTP_200_OK
    
    response_data = response.json()
    assert response_data['id'] == str(rating_on_db.id)
    assert response_data['rating'] == rating_update.rating
    assert response_data['title'] == rating_update.title
    assert response_data['description'] == rating_update.description


def test_update_rating_partial_route(authenticate_client, rating_on_db):
    original_title = rating_on_db.title
    original_description = rating_on_db.description
    
    rating_update = RatingUpdate(rating=2)  # Only update rating

    response = authenticate_client.patch(
        f'/ratings/{rating_on_db.community_id}/rating/{rating_on_db.id}',
        json=rating_update.model_dump(mode='json'),
    )
    
    assert response.status_code == status.HTTP_200_OK
    
    response_data = response.json()
    assert response_data['rating'] == 2
    assert response_data['title'] == original_title  # Should remain unchanged
    assert response_data['description'] == original_description  # Should remain unchanged


def test_update_rating_not_found_route(authenticate_client, community_member_on_db):
    non_existent_id = uuid.uuid4()
    rating_update = RatingUpdate(rating=3, title='Updated Title')

    response = authenticate_client.patch(
        f'/ratings/{community_member_on_db.community_id}/rating/{non_existent_id}',
        json=rating_update.model_dump(mode='json'),
    )
    
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert 'Unexpected error' in response.json()['message']


def test_update_rating_invalid_rating_returns_validation_error(authenticate_client, rating_on_db):
    rating_update_data = {
        'rating': 0,  # Invalid rating (< 1)
        'title': 'Updated Title',
    }

    response = authenticate_client.patch(
        f'/ratings/{rating_on_db.community_id}/rating/{rating_on_db.id}',
        json=rating_update_data,
    )
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_delete_rating_route(session_sql, authenticate_client, rating_on_db):
    response = authenticate_client.delete(
        f'/ratings/{rating_on_db.community_id}/rating/{rating_on_db.id}'
    )
    
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Verify the rating was deleted from the database
    rating_db = session_sql.query(Rating).filter(Rating.id == rating_on_db.id).first()
    assert rating_db is None

    # Verify trying to get the deleted rating returns 404
    get_response = authenticate_client.get(
        f'/ratings/{rating_on_db.community_id}/rating/{rating_on_db.id}'
    )
    assert get_response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_rating_not_found_route(authenticate_client, community_member_on_db):
    non_existent_id = uuid.uuid4()

    response = authenticate_client.delete(
        f'/ratings/{community_member_on_db.community_id}/rating/{non_existent_id}'
    )
    
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert 'Unexpected error' in response.json()['message']


def test_create_rating_unauthorized_returns_401(client_sql, community_member_on_db):
    rating_create = RatingCreate(
        user_id=community_member_on_db.user_id,
        community_id=community_member_on_db.community_id,
        rating=5,
        title='Unauthorized Rating',
        description='This should fail',
    )

    response = client_sql.post(
        f'/ratings/{community_member_on_db.community_id}/create-rating',
        json=rating_create.model_dump(mode='json'),
    )
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_rating_unauthorized_returns_401(client_sql, rating_on_db):
    response = client_sql.get(
        f'/ratings/{rating_on_db.community_id}/rating/{rating_on_db.id}'
    )
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_list_ratings_unauthorized_returns_401(client_sql, community_on_db):
    response = client_sql.get(
        f'/ratings/{community_on_db.id}/list-ratings'
    )
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_update_rating_unauthorized_returns_401(client_sql, rating_on_db):
    rating_update = RatingUpdate(rating=4, title='Updated Title')

    response = client_sql.patch(
        f'/ratings/{rating_on_db.community_id}/rating/{rating_on_db.id}',
        json=rating_update.model_dump(mode='json'),
    )
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_delete_rating_unauthorized_returns_401(client_sql, rating_on_db):
    response = client_sql.delete(
        f'/ratings/{rating_on_db.community_id}/rating/{rating_on_db.id}'
    )
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
