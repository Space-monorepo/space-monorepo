from uuid import UUID

from app.api.communities.schema import CommunityMemberResponse
from app.api.communities.service import CommunityService
from app.api.post.exceptions import (
    ComplaintNotFoundError,
    PollOptionNotFoundError,
    PollVoteAlreadyExistsError,
    PostLikesNotFoundError,
    PostNotFoundError,
    PostSuspendedError,
    UnexpectedPostError,
)
from app.api.post.model import (
    CampaignParticipants,
    CampaignPost,
    ComplaintPost,
    PollOptions,
    PollPosts,
    PollVotes,
    Post,
    PostLikes,
)
from app.api.post.schemas import (
    CampaignResponse,
    CommunityRelated,
    ComplaintLevelEnum,
    ComplaintResponse,
    PollCreate,
    PollOptionResponse,
    PollResponse,
    PollVoteResponse,
    PostAuthor,
    PostCreate,
    PostFeedResponse,
    PostResponse,
    PostStatusEnum,
    PostTypeEnum,
    PostUpdate,
)
from app.core.transaction import TransactionManager
from app.utils.schema import PaginationResponse, PaginationSearchParams

# TODO: Fazer verificação de quem pode editar (update) cada elemento do post


# ruff: noqa: PLR0904
class PostService:
    REPORT_THRESHOLD = 30
    COMPLAINT_MEDIUM_THRESHOLD = 30
    COMPLAINT_HIGH_THRESHOLD = 50

    def __init__(self, tm: TransactionManager):
        self.tm = tm
        self.post_repo = tm.get_post_repository()
        self.complaint_repo = tm.get_complaint_post_repository()
        self.campaign_repo = tm.get_campaign_post_repository()
        self.campaign_participants_repo = tm.get_campaign_participants_repository()
        self.poll_posts_repo = tm.get_poll_posts_repository()
        self.poll_options_repo = tm.get_poll_options_repository()
        self.post_likes_repo = tm.get_post_likes_repository()
        self.poll_votes_repo = tm.get_poll_votes_repository()
        self.community_service = CommunityService(tm)

    def _get_post(self, post_id: UUID) -> Post:
        post = self.post_repo.get_by_id(str(post_id))
        if not post:
            raise PostNotFoundError('Post not found')
        return post

    @staticmethod
    def __map_post_to_feed_response(
        post: Post,
        poll_question: str | None = None,
        poll_options: list[PollOptionResponse] | None = None,
    ) -> PostFeedResponse:
        return PostFeedResponse(
            id=post.id,
            community=CommunityRelated(id=post.community_id, name=post.community.name),
            user=PostAuthor(
                id=post.user_id,
                name=post.user.name,
                role=post.user_role_in_community,
                profile_picture=post.user.profile_image_url,
            ),
            type_post=post.type_post,
            title=post.title,
            content=post.content,
            image_url=post.image_url,
            status=post.status,
            likes_count=post.likes_count,
            comments_count=post.comments_count,
            report_count=post.report_count,
            created_at=post.created_at,
            updated_at=post.updated_at,
            poll_question=poll_question,
            poll_options=poll_options,
        )

    def create_post(self, post: PostCreate) -> PostResponse:
        try:
            role = self.community_service.get_member_association(
                post.user_id, post.community_id
            ).role
            post = Post(**post.model_dump())
            post.user_role_in_community = role
            post_saved = self.post_repo.save(post)
            return self.__map_post_to_feed_response(post_saved)
        except Exception as e:
            raise UnexpectedPostError('Unexpected error creating post') from e

    def get_post(self, post_id: UUID) -> PostResponse:
        post = self._get_post(post_id)
        return self.__map_post_to_feed_response(post)

    def list_posts_by_community(
        self, community_id: UUID, params: PaginationSearchParams
    ) -> PaginationResponse[PostFeedResponse]:
        posts, total = self.post_repo.list_posts_by_community(community_id, params)
        return PaginationResponse(
            items=[self.__map_post_to_feed_response(post) for post in posts],
            total=total,
            has_more=total > (params.offset or 0) + (params.limit or 10),
            current_offset=params.offset or 0,
            current_limit=params.limit or 10,
        )

    def list_posts_by_user(
        self, user_id: UUID, params: PaginationSearchParams
    ) -> PaginationResponse[PostFeedResponse]:
        posts, total = self.post_repo.list_posts_by_user(user_id, params)
        return PaginationResponse(
            items=[self.__map_post_to_feed_response(post) for post in posts],
            total=total,
            has_more=total > (params.offset or 0) + (params.limit or 10),
            current_offset=params.offset or 0,
            current_limit=params.limit or 10,
        )

    def update_post(self, post_id: UUID, post_update: PostUpdate) -> PostFeedResponse:
        post = self._get_post(post_id)
        if post_update.content:
            post.content = post_update.content
        if post_update.status:
            post.status = post_update.status
        try:
            post = self.post_repo.save(post)
            post_saved = self._get_post(post.id)
            return self.__map_post_to_feed_response(post_saved)
        except Exception as e:
            raise UnexpectedPostError('Unexpected error updating post') from e

    def delete_post(self, post_id: UUID) -> bool:
        try:
            post = self._get_post(post_id)
            return self.post_repo.delete(post)
        except Exception as e:
            raise UnexpectedPostError('Unexpected error deleting post') from e

    def get_user_feed(
        self, user_id: UUID, params: PaginationSearchParams
    ) -> PaginationResponse[PostFeedResponse]:
        feed, total = self.post_repo.get_user_feed(user_id, params)

        # Identificar posts do tipo poll e buscar dados em batch
        poll_post_ids = [
            str(post.id) for post in feed if post.type_post == PostTypeEnum.POLL
        ]
        poll_data_map: dict[str, tuple[str, list[PollOptionResponse]]] = {}

        if poll_post_ids:
            # Buscar PollPosts em batch
            for post_id_str in poll_post_ids:
                poll_post = self.poll_posts_repo.get_by_id(UUID(post_id_str))
                if poll_post:
                    # Buscar opções do poll
                    poll_options = self.poll_options_repo.list_by_post(UUID(post_id_str))
                    option_responses = []
                    if poll_options:
                        option_responses = [
                            PollOptionResponse(
                                id=option.id,
                                answer=option.answer,
                                votes_count=option.votes_count,
                            )
                            for option in poll_options
                        ]
                    poll_data_map[post_id_str] = (poll_post.question, option_responses)

        # Mapear posts incluindo dados de poll quando disponíveis
        posts = []
        for post in feed:
            post_id_str = str(post.id)
            if post.type_post == PostTypeEnum.POLL and post_id_str in poll_data_map:
                poll_question, poll_options = poll_data_map[post_id_str]
                posts.append(
                    self.__map_post_to_feed_response(
                        post, poll_question=poll_question, poll_options=poll_options
                    )
                )
            else:
                posts.append(self.__map_post_to_feed_response(post))

        return PaginationResponse(
            items=posts,
            total=total,
            has_more=total > (params.offset or 0) + (params.limit or 10),
            current_offset=params.offset or 0,
            current_limit=params.limit or 10,
        )

    def get_like(self, post_id: UUID, member_id: UUID) -> PostLikes:
        like = self.post_likes_repo.get_by_id(post_id, member_id)
        if not like:
            raise PostLikesNotFoundError('Post likes not found')
        return like

    def like_post(self, post_id: UUID, member_id: UUID) -> PostFeedResponse:
        post = self._get_post(post_id)
        post.likes_count += 1

        try:
            self.post_likes_repo.save(PostLikes(post_id=post_id, member_id=member_id))
            post = self.post_repo.save(post)
            return self.__map_post_to_feed_response(post)
        except Exception as e:
            raise UnexpectedPostError('Unexpected error liking post') from e

    def unlike_post(self, post_id: UUID, member_id: UUID) -> PostFeedResponse:
        try:
            post = self._get_post(post_id)
            like = self.get_like(post_id, member_id)
            post.likes_count -= 1
            self.post_likes_repo.delete(like)
            post = self.post_repo.save(post)
            return self.__map_post_to_feed_response(post)
        except Exception as e:
            raise UnexpectedPostError('Unexpected error unliking post') from e

    def list_likes_post(self, post_id: UUID) -> list[CommunityMemberResponse]:
        self._get_post(post_id)
        community_members = self.post_likes_repo.list_by_post(post_id)
        members_response = []
        for member in community_members:
            members_response.append(
                self.community_service._map_member_to_response(member)
            )
        return members_response

    def report_post(self, post_id: UUID) -> PostFeedResponse:
        post = self._get_post(post_id)
        if post.status == PostStatusEnum.SUSPENDED:
            raise PostSuspendedError('Post is already suspended')
        # TODO: add report service to create a report in the report table
        post.report_count += 1
        if post.report_count >= self.REPORT_THRESHOLD:
            post.status = PostStatusEnum.REPORTED
        try:
            post = self.post_repo.save(post)
            return self.__map_post_to_feed_response(post)
        except Exception as e:
            raise UnexpectedPostError('Unexpected error reporting post') from e

    def create_campaign(self, post: PostCreate) -> CampaignResponse:
        try:
            post = self.create_post(post)
            campaign = CampaignPost(post_id=str(post.id))
            campaign_saved = self.campaign_repo.save(campaign)
            return CampaignResponse(
                post=self.get_post(post.id),
                target_participants=campaign_saved.target_participants,
                current_participants=campaign_saved.current_participants,
                status_campaign=campaign_saved.status_campaign,
            )
        except Exception as e:
            raise UnexpectedPostError('Unexpected error creating campaign') from e

    def list_user_campaigns_subscriptions(
        self, user_id: UUID, params: PaginationSearchParams
    ) -> PaginationResponse[CampaignResponse]:
        campaigns, total = self.campaign_repo.list_user_campaigns_subscriptions(
            user_id, params
        )
        campaigns_response = [
            CampaignResponse(
                post=self.get_post(campaign.post_id),
                target_participants=campaign.target_participants,
                current_participants=campaign.current_participants,
                status_campaign=campaign.status_campaign,
            )
            for campaign in campaigns
        ]
        return PaginationResponse(
            items=campaigns_response,
            total=total,
            has_more=total > (params.offset or 0) + (params.limit or 10),
            current_offset=params.offset or 0,
            current_limit=params.limit or 10,
        )

    def participate_campaign(
        self, post_id: UUID, member_id: UUID
    ) -> CampaignParticipants:
        try:
            campaign = self.campaign_repo.get_by_id(post_id)
            campaign.current_participants += 1
            self.campaign_repo.save(campaign)
            member = self.community_service.get_member(member_id)
            campaign_participants = CampaignParticipants(
                campaign_id=post_id,
                member_id=member.id,
                user_id=member.user_id,
            )
            participant_saved = self.campaign_participants_repo.save(
                campaign_participants
            )
            return participant_saved
        except Exception as e:
            raise UnexpectedPostError(
                'Unexpected error participating in campaign'
            ) from e

    def list_participants_campaign(self, post_id: UUID) -> list[CommunityMemberResponse]:
        self._get_post(post_id)
        participants = self.campaign_participants_repo.list_by_post(post_id)
        return [
            self.community_service._map_member_to_response(participant)
            for participant in participants
        ]

    def get_complaint(self, post_id: UUID) -> ComplaintPost:
        complaint = self.complaint_repo.get_by_id(post_id)
        if not complaint:
            raise ComplaintNotFoundError('Complaint not found')
        return complaint

    def create_complaint(self, post: PostCreate) -> ComplaintResponse:
        try:
            post = self.create_post(post)
            complaint = ComplaintPost(post_id=str(post.id))
            complaint_saved = self.complaint_repo.save(complaint)
            return ComplaintResponse(
                post=self.get_post(post.id),
                confirmations_count=complaint_saved.confirmations_count,
                status_complaint=complaint_saved.status_complaint,
                level_complaint=complaint_saved.level_complaint,
            )
        except Exception as e:
            raise UnexpectedPostError('Unexpected error creating complaint') from e

    def confirm_complaint(self, post_id: UUID) -> ComplaintResponse:
        complaint = self.get_complaint(post_id)
        complaint.confirmations_count += 1
        if complaint.confirmations_count >= self.COMPLAINT_HIGH_THRESHOLD:
            complaint.level_complaint = ComplaintLevelEnum.HIGH
        elif complaint.confirmations_count >= self.COMPLAINT_MEDIUM_THRESHOLD:
            complaint.level_complaint = ComplaintLevelEnum.MEDIUM
        else:
            complaint.level_complaint = ComplaintLevelEnum.LOW
        complaint_saved = self.complaint_repo.save(complaint)
        return ComplaintResponse(
            post=self.get_post(post_id),
            confirmations_count=complaint_saved.confirmations_count,
            status_complaint=complaint_saved.status_complaint,
            level_complaint=complaint_saved.level_complaint,
        )

    def get_poll(self, post_id: UUID) -> PollPosts:
        try:
            poll = self.poll_posts_repo.get_by_id(post_id)
            if not poll:
                raise PostNotFoundError('Poll not found')
            return poll
        except Exception as e:
            raise UnexpectedPostError('Unexpected error getting poll') from e

    def list_poll_options(self, post_id: UUID) -> list[PollOptionResponse]:
        self._get_post(post_id)
        poll_options = self.poll_options_repo.list_by_post(post_id)
        return [
            PollOptionResponse(
                id=option.id,
                answer=option.answer,
                votes_count=option.votes_count,
            )
            for option in poll_options
        ]

    def create_poll(self, poll_create: PollCreate) -> PollResponse:
        try:
            post = self.create_post(poll_create.post)
            poll = PollPosts(post_id=str(post.id), question=poll_create.question)
            poll_saved = self.poll_posts_repo.save(poll)
            poll_options = []
            for option in poll_create.options:
                poll_option = PollOptions(post_id=str(post.id), answer=option)
                poll_option_saved = self.poll_options_repo.save(poll_option)
                poll_options.append(
                    PollOptionResponse(
                        id=poll_option_saved.id,
                        answer=poll_option_saved.answer,
                        votes_count=poll_option_saved.votes_count,
                    )
                )

            return PollResponse(
                post=self.get_post(post.id),
                question=poll_saved.question,
                options=poll_options,
            )
        except Exception as e:
            raise UnexpectedPostError('Unexpected error creating poll') from e

    def vote_poll(self, poll_option_id: UUID, member_id: UUID) -> PollVoteResponse:
        try:
            poll_option = self.poll_options_repo.get_by_id(poll_option_id)
            if not poll_option:
                raise PollOptionNotFoundError('Poll option not found')

            vote = self.poll_votes_repo.member_has_voted(member_id, poll_option.post_id)
            
            # Se já votou, verificar se é na mesma opção
            if vote:
                if str(vote.poll_option_id) == str(poll_option_id):
                    raise PollVoteAlreadyExistsError('Poll vote already exists')
                
                # Decrementar contagem da opção ANTIGA
                old_option = self.poll_options_repo.get_by_id(vote.poll_option_id)
                if old_option:
                    old_option.votes_count -= 1
                    self.poll_options_repo.save(old_option)
                
                # Deletar voto antigo
                self.poll_votes_repo.delete(vote)

            # Incrementar contagem da nova opção e criar novo voto
            poll_option.votes_count += 1
            self.poll_options_repo.save(poll_option)
            vote_saved = self.poll_votes_repo.save(
                PollVotes(
                    poll_post_id=poll_option.post_id,
                    poll_option_id=poll_option_id,
                    member_id=member_id,
                )
            )
            return PollVoteResponse(
                id=vote_saved.id,
                poll_option_id=poll_option_id,
                member_id=member_id,
                created_at=vote_saved.created_at,
            )
        except (PollVoteAlreadyExistsError, PollOptionNotFoundError):
            raise
        except Exception as e:
            raise UnexpectedPostError('Unexpected error voting poll') from e
