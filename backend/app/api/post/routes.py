from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.communities.model import CommunityMember
from app.api.communities.schema import CommunityMemberResponse
from app.api.post.schemas import (
    CampaignParticipantsResponse,
    CampaignResponse,
    ComplaintResponse,
    PollCreate,
    PollResponse,
    PollVoteResponse,
    PostCreate,
    PostFeedResponse,
    PostResponse,
    PostUpdate,
)
from app.api.post.service import PostService
from app.api.users.schema import UserResponse
from app.auth.deps import get_current_user, require_post_owner, require_roles
from app.core.database import get_db
from app.core.transaction import TransactionManager
from app.utils.schema import PaginationResponse, PaginationSearchParams

router = APIRouter(prefix='/posts', tags=['posts'])


@router.get(
    '/{community_id}/post/{post_id}',
    response_model=PostResponse,
    status_code=status.HTTP_200_OK,
)
def get_post(
    post_id: str,
    session: Session = Depends(get_db),
    _: CommunityMember = Depends(require_roles(['member'])),
) -> PostResponse:
    with TransactionManager(session) as tm:
        return PostService(tm).get_post(post_id)


@router.get(
    '/{community_id}/user/{user_id}/list-posts',
    response_model=PaginationResponse[PostResponse],
    status_code=status.HTTP_200_OK,
)
def list_posts_by_user(
    user_id: str,
    params: PaginationSearchParams = Depends(PaginationSearchParams),
    session: Session = Depends(get_db),
    _: CommunityMember = Depends(require_roles(['member'])),
) -> PaginationResponse[PostResponse]:
    with TransactionManager(session) as tm:
        return PostService(tm).list_posts_by_user(user_id, params)


@router.get(
    '/{community_id}/community/list-posts',
    response_model=PaginationResponse[PostResponse],
    status_code=status.HTTP_200_OK,
)
def list_posts_by_community(
    community_id: str,
    params: PaginationSearchParams = Depends(PaginationSearchParams),
    session: Session = Depends(get_db),
    _: CommunityMember = Depends(require_roles(['admin', 'moderator'])),
) -> PaginationResponse[PostResponse]:
    with TransactionManager(session) as tm:
        posts = PostService(tm).list_posts_by_community(community_id, params)
        return posts


@router.post(
    '/{community_id}/create-announcement',
    response_model=PostResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_announcement(
    post: PostCreate,
    session: Session = Depends(get_db),
    _: CommunityMember = Depends(require_roles(['moderator', 'admin'])),
) -> PostResponse:
    with TransactionManager(session) as tm:
        return PostService(tm).create_post(post)


@router.get('/feed', response_model=PaginationResponse[PostFeedResponse])
def get_user_feed(
    session: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
    params: PaginationSearchParams = Depends(PaginationSearchParams),
) -> PaginationResponse[PostFeedResponse]:
    with TransactionManager(session) as tm:
        return PostService(tm).get_user_feed(current_user.id, params)


@router.patch(
    '/{community_id}/post/{post_id}',
    response_model=PostFeedResponse,
    status_code=status.HTTP_200_OK,
)
def update_post(
    community_id: str,
    post_id: str,
    post: PostUpdate,
    session: Session = Depends(get_db),
    current_member: CommunityMember = Depends(require_roles(['member'])),
) -> PostFeedResponse:
    if post.content and not require_post_owner(post_id, session, current_member):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail='User not allowed.'
        )
    if post.status and current_member.role not in {'admin', 'moderator'}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail='User not allowed.'
        )
    with TransactionManager(session) as tm:
        return PostService(tm).update_post(post_id, post)


@router.delete('/{community_id}/post/{post_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    post_id: str,
    session: Session = Depends(get_db),
    current_member: CommunityMember = Depends(require_roles(['member'])),
):
    if not require_post_owner(post_id, session, current_member):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail='User not allowed.'
        )
    with TransactionManager(session) as tm:
        PostService(tm).delete_post(post_id)


@router.post(
    '/{community_id}/post/{post_id}/like',
    response_model=PostFeedResponse,
    status_code=status.HTTP_200_OK,
)
def like_post(
    post_id: str,
    session: Session = Depends(get_db),
    current_member: CommunityMember = Depends(require_roles(['member'])),
) -> PostFeedResponse:
    with TransactionManager(session) as tm:
        return PostService(tm).like_post(post_id, current_member.id)


@router.post(
    '/{community_id}/post/{post_id}/unlike',
    response_model=PostFeedResponse,
    status_code=status.HTTP_200_OK,
)
def unlike_post(
    post_id: str,
    session: Session = Depends(get_db),
    current_member: CommunityMember = Depends(require_roles(['member'])),
) -> PostFeedResponse:
    with TransactionManager(session) as tm:
        return PostService(tm).unlike_post(post_id, current_member.id)


@router.get(
    '/{community_id}/post/{post_id}/list-likes',
    response_model=list[CommunityMemberResponse],
    status_code=status.HTTP_200_OK,
)
def list_likes_post(
    post_id: str,
    session: Session = Depends(get_db),
    _: CommunityMember = Depends(require_roles(['member'])),
) -> list[CommunityMemberResponse]:
    with TransactionManager(session) as tm:
        return PostService(tm).list_likes_post(post_id)


@router.patch(
    '/{community_id}/post/{post_id}/report',
    response_model=PostFeedResponse,
    status_code=status.HTTP_200_OK,
)
def report_post(
    post_id: str,
    session: Session = Depends(get_db),
    _: CommunityMember = Depends(require_roles(['member'])),
) -> PostFeedResponse:
    with TransactionManager(session) as tm:
        return PostService(tm).report_post(post_id)


@router.post(
    '/{community_id}/post/campaign',
    response_model=CampaignResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_campaign(
    post: PostCreate,
    session: Session = Depends(get_db),
    _: CommunityMember = Depends(require_roles(['member'])),
) -> CampaignResponse:
    with TransactionManager(session) as tm:
        return PostService(tm).create_campaign(post)


@router.post(
    '/{community_id}/post/{post_id}/campaign/participate', status_code=status.HTTP_200_OK
)
def participate_campaign(
    post_id: str,
    session: Session = Depends(get_db),
    current_member: CommunityMember = Depends(require_roles(['member'])),
) -> CampaignParticipantsResponse:
    with TransactionManager(session) as tm:
        campaign_participants = PostService(tm).participate_campaign(
            post_id, current_member.id
        )
        return CampaignParticipantsResponse.model_validate(campaign_participants)


@router.get(
    '/post/list-user-campaigns',
    response_model=PaginationResponse[CampaignResponse],
    status_code=status.HTTP_200_OK,
)
def list_user_campaigns(
    params: PaginationSearchParams = Depends(PaginationSearchParams),
    session: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
) -> PaginationResponse[CampaignResponse]:
    with TransactionManager(session) as tm:
        return PostService(tm).list_user_campaigns_subscriptions(current_user.id, params)


@router.post(
    '/{community_id}/post/complaint',
    response_model=ComplaintResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_complaint(
    post: PostCreate,
    session: Session = Depends(get_db),
    _: CommunityMember = Depends(require_roles(['member'])),
) -> ComplaintResponse:
    with TransactionManager(session) as tm:
        return PostService(tm).create_complaint(post)


@router.post(
    '/{community_id}/complaint/{post_id}/confirm',
    response_model=ComplaintResponse,
    status_code=status.HTTP_200_OK,
)
def confirm_complaint(
    post_id: str,
    session: Session = Depends(get_db),
    _: CommunityMember = Depends(require_roles(['member'])),
) -> ComplaintResponse:
    with TransactionManager(session) as tm:
        return PostService(tm).confirm_complaint(post_id)


@router.post(
    '/{community_id}/post/poll',
    response_model=PollResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_poll(
    poll: PollCreate,
    session: Session = Depends(get_db),
    _: CommunityMember = Depends(require_roles(['admin', 'moderator'])),
) -> PollResponse:
    with TransactionManager(session) as tm:
        return PostService(tm).create_poll(poll)


@router.patch(
    '/{community_id}/post/poll-options/{poll_option_id}/vote',
    response_model=PollVoteResponse,
    status_code=status.HTTP_200_OK,
)
def vote_poll(
    poll_option_id: str,
    session: Session = Depends(get_db),
    member: CommunityMember = Depends(require_roles(['member'])),
) -> PollVoteResponse:
    with TransactionManager(session) as tm:
        return PostService(tm).vote_poll(poll_option_id, member.id)
