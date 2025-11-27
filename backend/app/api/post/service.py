import logging
from uuid import UUID

from app.api.communities.schema import CommunityMemberResponse
from app.api.communities.service import CommunityService
from app.api.notifications.service import NotificationService
from app.api.post.exceptions import (
    ComplaintNotFoundError,
    PollOptionNotFoundError,
    PollVoteAlreadyExistsError,
    PollVoteNotFoundError,
    PostLikesNotFoundError,
    PostNotFoundError,
    PostSuspendedError,
    UnexpectedPostError,
)
from app.api.post.model import (
    CampaignParticipants,
    CampaignPost,
    ComplaintConfirmation,
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
from app.api.reports.model import Report, ReportPost
from app.api.reports.schema import ReportReasonEnum, ReportTypeEnum
from app.api.reputation.schema import (
    POPULARITY_POINTS,
    PopularityActionEnum,
)
from app.api.reputation.service import ReputationService
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
        self.complaint_confirmation_repo = tm.get_complaint_confirmation_repository()
        self.campaign_repo = tm.get_campaign_post_repository()
        self.campaign_participants_repo = tm.get_campaign_participants_repository()
        self.poll_posts_repo = tm.get_poll_posts_repository()
        self.poll_options_repo = tm.get_poll_options_repository()
        self.post_likes_repo = tm.get_post_likes_repository()
        self.poll_votes_repo = tm.get_poll_votes_repository()
        self.report_repo = tm.get_report_repository()
        self.report_post_repo = tm.get_report_post_repository()
        self.community_service = CommunityService(tm)
        self.reputation_service = ReputationService(tm)

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

            member = self.community_service.get_member_association(
                post_saved.user_id, post_saved.community_id
            )
            self.reputation_service.reward_post_creation_to_member(member.id)
            return self.__map_post_to_feed_response(post_saved)
        except Exception as e:
            raise UnexpectedPostError('Unexpected error creating post') from e

    def get_post(self, post_id: UUID | str) -> PostFeedResponse:
        # Converter para UUID se for string
        if isinstance(post_id, str):
            post_id = UUID(post_id)

        post = self._get_post(post_id)

        print(f'[DEBUG] get_post - tipo do post: {post.type_post}')

        # Se for uma enquete, buscar as opções
        if post.type_post == PostTypeEnum.POLL:
            print('[DEBUG] Post é uma enquete, buscando opções...')
            poll_post = self.poll_posts_repo.get_by_id(post_id)
            if poll_post:
                print(f'[DEBUG] Poll post encontrado: {poll_post.question}')
                poll_options = self.poll_options_repo.list_by_post(post_id)
                print(
                    f'[DEBUG] Opções encontradas: {len(poll_options) if poll_options else 0}'
                )
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
                    print(
                        f'[DEBUG] Opções mapeadas: {[opt.answer for opt in option_responses]}'
                    )
                result = self.__map_post_to_feed_response(
                    post, poll_question=poll_post.question, poll_options=option_responses
                )
                print(
                    f'[DEBUG] Resultado com enquete - question: {result.poll_question}, options: {len(result.poll_options) if result.poll_options else 0}'
                )
                return result

        print('[DEBUG] Retornando post sem dados de enquete')
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

            try:
                notification_service = NotificationService(self.tm)
                recipient = post.user

                actor = self.community_service.get_member(member_id)

                if recipient and actor and recipient.id != actor.id:
                    notification_service.create_interaction_notification(
                        recipient=recipient,
                        actor=actor,
                        interaction_type='like',
                        post_title=post.title or 'sua publicação',
                    )
            except Exception as e:
                logging.warning(f'Falha ao criar notificação de like: {e}')

            author_post = self.community_service.get_member_association(
                post.user_id, post.community_id
            )
            self.reputation_service.reward_post_like_to_member(member_id, author_post.id)
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

            author_post = self.community_service.get_member_association(
                post.user_id, post.community_id
            )
            author = self.community_service.get_member(author_post.id)
            author.popularity -= POPULARITY_POINTS[PopularityActionEnum.RECEIVE_LIKE]
            author.popularity = max(0, author.popularity)
            self.community_service.member_repo.save(author)

            liker = self.community_service.get_member(member_id)
            liker.popularity -= POPULARITY_POINTS[PopularityActionEnum.LIKE]
            liker.popularity = max(0, liker.popularity)
            self.community_service.member_repo.save(liker)

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

    def report_post(
        self,
        post_id: UUID,
        reporter_id: UUID,
        community_id: UUID,
        reason: ReportReasonEnum | None = None,
        description: str | None = None,
    ) -> PostFeedResponse:
        post = self._get_post(post_id)
        if post.status == PostStatusEnum.SUSPENDED:
            raise PostSuspendedError('Post is already suspended')

        normalized_reason = reason or ReportReasonEnum.OTHER
        report_description = (
            description or 'Report submitted via quick action on the feed'
        )

        existing_report = self.report_post_repo.get_by_reporter_post_reason(
            reporter_id, post_id, normalized_reason.value
        )
        if existing_report:
            return self.__map_post_to_feed_response(post)

        try:
            report_model = Report(
                reporter_id=str(reporter_id),
                type=ReportTypeEnum.POST_REPORT.value,
                reason=normalized_reason.value,
                description=report_description,
            )
            report_saved = self.report_repo.save(report_model)
            report_post_model = ReportPost(
                report_id=str(report_saved.id),
                post_id=str(post_id),
                community_id=str(community_id or post.community_id),
            )
            self.report_post_repo.save(report_post_model)

            post.report_count += 1
            if post.report_count >= self.REPORT_THRESHOLD:
                post.status = PostStatusEnum.REPORTED

            post = self.post_repo.save(post)
            return self.__map_post_to_feed_response(post)
        except Exception as e:
            raise UnexpectedPostError('Unexpected error reporting post') from e

    def create_campaign(self, post: PostCreate) -> CampaignResponse:
        try:
            created_post = self.create_post(post)
            campaign = CampaignPost(post_id=str(created_post.id))
            campaign_saved = self.campaign_repo.save(campaign)

            member = self.community_service.get_member_association(
                created_post.user.id, created_post.community.id
            )
            # Incrementar participantes diretamente no objeto salvo
            campaign_saved.current_participants += 1
            campaign_saved = self.campaign_repo.save(campaign_saved)

            # Criar registro de participação
            campaign_participants = CampaignParticipants(
                campaign_id=created_post.id,
                member_id=member.id,
                user_id=member.user_id,
            )
            self.campaign_participants_repo.save(campaign_participants)

            self.reputation_service.reward_campaign_support_to_member(member.id)
            self.reputation_service.reward_campaign_creation_to_member(member.id)

            return CampaignResponse(
                post=self.get_post(created_post.id),
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
            self.reputation_service.reward_campaign_support_to_member(member_id)
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
            created_post = self.create_post(post)
            complaint = ComplaintPost(post_id=str(created_post.id))
            complaint_saved = self.complaint_repo.save(complaint)

            member = self.community_service.get_member_association(
                created_post.user.id, created_post.community.id
            )
            # Incrementar confirmações diretamente no objeto salvo
            complaint_saved.confirmations_count += 1
            complaint_saved = self.complaint_repo.save(complaint_saved)

            # Criar registro de confirmação para o criador
            confirmation = ComplaintConfirmation(
                post_id=created_post.id,
                member_id=member.id,
            )
            self.complaint_confirmation_repo.save(confirmation)

            self.reputation_service.reward_complaint_confirmation_to_member(member.id)
            self.reputation_service.reward_complaint_creation_to_member(member.id)

            return ComplaintResponse(
                post=self.get_post(created_post.id),
                confirmations_count=complaint_saved.confirmations_count,
                status_complaint=complaint_saved.status_complaint,
                level_complaint=complaint_saved.level_complaint,
            )
        except Exception as e:
            raise UnexpectedPostError('Unexpected error creating complaint') from e

    def confirm_complaint(self, post_id: UUID, member_id: UUID) -> ComplaintResponse:
        # Verifica se o usuário já confirmou
        if self.complaint_confirmation_repo.has_confirmed(post_id, member_id):
            # Retorna a resposta atual sem criar duplicata
            complaint = self.get_complaint(post_id)
            return ComplaintResponse(
                post=self.get_post(post_id),
                confirmations_count=complaint.confirmations_count,
                status_complaint=complaint.status_complaint,
                level_complaint=complaint.level_complaint,
            )
        try:
            confirmation = ComplaintConfirmation(
                post_id=post_id,
                member_id=member_id,
            )
            self.complaint_confirmation_repo.save(confirmation)
        except Exception as e:
            raise UnexpectedPostError('Unexpected error confirming complaint') from e
        complaint = self.get_complaint(post_id)
        complaint.confirmations_count += 1
        if complaint.confirmations_count >= self.COMPLAINT_HIGH_THRESHOLD:
            complaint.level_complaint = ComplaintLevelEnum.HIGH
        elif complaint.confirmations_count >= self.COMPLAINT_MEDIUM_THRESHOLD:
            complaint.level_complaint = ComplaintLevelEnum.MEDIUM
        else:
            complaint.level_complaint = ComplaintLevelEnum.LOW
        complaint_saved = self.complaint_repo.save(complaint)
        self.reputation_service.reward_complaint_confirmation_to_member(member_id)
        return ComplaintResponse(
            post=self.get_post(post_id),
            confirmations_count=complaint_saved.confirmations_count,
            status_complaint=complaint_saved.status_complaint,
            level_complaint=complaint_saved.level_complaint,
        )

    def has_user_confirmed_complaint(self, post_id: UUID, member_id: UUID) -> bool:
        """Verifica se o usuário já confirmou a denúncia"""
        return self.complaint_confirmation_repo.has_confirmed(post_id, member_id)

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

    def unvote_poll(self, poll_option_id: UUID, member_id: UUID) -> dict:
        try:
            poll_option = self.poll_options_repo.get_by_id(poll_option_id)
            if not poll_option:
                raise PollOptionNotFoundError('Poll option not found')

            vote = self.poll_votes_repo.member_has_voted(member_id, poll_option.post_id)

            if not vote:
                raise PollVoteNotFoundError('Poll vote not found')

            # Verificar se o voto é na opção correta
            if str(vote.poll_option_id) != str(poll_option_id):
                raise PollVoteNotFoundError('Poll vote not found for this option')

            # Decrementar contagem da opção
            poll_option.votes_count = max(0, poll_option.votes_count - 1)
            self.poll_options_repo.save(poll_option)

            # Deletar o voto
            self.poll_votes_repo.delete(vote)

            return {'message': 'Vote removed successfully'}
        except (PollVoteNotFoundError, PollOptionNotFoundError):
            raise
        except Exception as e:
            raise UnexpectedPostError('Unexpected error removing poll vote') from e
