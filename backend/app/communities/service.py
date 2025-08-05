from uuid import UUID
from app.communities.model import Community, CommunityMember
from app.communities.schema import (
    CommunityCreate,
    CommunityResponse,
    CommunityUpdate,
    CommunityMemberRoleEnum
)
from app.communities.exceptions import (
    CommunityNotFoundError,
    UnexpectedCommunityError,
    UnexpectedCommunityMemberError,
    CommunityMemberNotFoundError,
    CommunityMemberAlreadyExistsError
)
from app.core.transaction import TransactionManager
from app.users.service import UserService
from app.utils.schema import PaginationResponse, PaginationSearchParams
from app.communities.schema import CommunityMemberResponse, CommunityMemberCreate, CommunityRelated


class CommunityService:
    def __init__(self, tm: TransactionManager):
        self.tm = tm
        self.community_repo = tm.get_community_repository()
        self.member_repo = tm.get_member_repository()
        self.user_service = UserService(tm)

    @staticmethod
    def _map_member_to_response(member: CommunityMember) -> CommunityMemberResponse:
        return CommunityMemberResponse(
            user_id=member.user_id,
            community_id=member.community_id,
            user=member.user,
            community=CommunityRelated(id=member.community.id, name=member.community.name),
            role=member.role,
            status_participation=member.status_participation,
            reputation=member.reputation,
            entered_in=member.entered_in
        )

    def get_community(self, id: UUID) -> Community:
        community = self.community_repo.get_by_id(id)
        if not community:
            raise CommunityNotFoundError(f'Community with id {id} not found')
        return community

    def create_community(self, community: CommunityCreate) -> Community:
        try:
            community_model = Community(**community.model_dump())
            community = self.community_repo.save(community_model)
            return community
        except Exception as e:
            raise UnexpectedCommunityError(f'Unexpected error: {e}') from e

    def list_communities(
        self, params: PaginationSearchParams) -> PaginationResponse[CommunityResponse]:
        communities, total = self.community_repo.list_all(params)
        communities = [
            CommunityResponse.model_validate(community) for community in communities
        ]
        return PaginationResponse(
            items=communities,
            total=total,
            has_more=total > (params.offset or 0) + (params.limit or 10),
            current_offset=params.offset or 0,
            current_limit=params.limit or 10,
        )

    def list_user_communities(
        self, user_id: UUID, params: PaginationSearchParams
    ) -> PaginationResponse[CommunityResponse]:
        communities, total = self.member_repo.list_communities_by_user(user_id, params)
        communities_response = [
            CommunityResponse.model_validate(community) for community in communities
        ]
        return PaginationResponse(
            items=communities_response,
            total=total,
            has_more=total > (params.offset or 0) + (params.limit or 10),
            current_offset=params.offset or 0,
            current_limit=params.limit or 10,
        )

    def update_community(self, community_id: UUID, community_update: CommunityUpdate) -> Community:
        community = self.get_community(community_id)
        for key, value in community_update.model_dump(exclude_unset=True).items():
            setattr(community, key, value)
        try:
            community = self.community_repo.save(community)
            return community
        except Exception as e:
            raise UnexpectedCommunityError(f'Unexpected error: {e}') from e

    def delete_community(self, community_id: UUID) -> bool:
        community = self.get_community(community_id)
        try:
            result = self.community_repo.delete(community)
            return result
        except Exception as e:
            raise UnexpectedCommunityError(f'Unexpected error: {e}') from e

    def list_members(
        self, community_id: UUID, params: PaginationSearchParams
    ) -> PaginationResponse[CommunityMemberResponse]:
        self.get_community(community_id)
        members, total = self.member_repo.list_members(community_id, params)

        members_response = [self._map_member_to_response(member) for member in members]

        return PaginationResponse(
            items=members_response,
            total=total,
            has_more=total > (params.offset or 0) + (params.limit or 10),
            current_offset=params.offset or 0,
            current_limit=params.limit or 10,
        )

    def get_member_association(self, user_id: UUID, community_id: UUID) -> CommunityMember:
        self.get_community(community_id)
        self.user_service.get_user(user_id)
        member_assocation = self.member_repo.get_member_association(user_id, community_id)
        if not member_assocation:
            raise CommunityMemberNotFoundError(f'User with id {user_id} not found in community with id {community_id}.')
        return member_assocation

    def list_moderators(self, community_id: UUID, params: PaginationSearchParams) -> PaginationResponse[CommunityMemberResponse]:
        self.get_community(community_id)
        moderators, total = self.member_repo.list_moderators(community_id, params)

        moderators_response = [self._map_member_to_response(moderator) for moderator in moderators]

        return PaginationResponse(
            items=moderators_response,
            total=total,
            has_more=total > (params.offset or 0) + (params.limit or 10),
            current_offset=params.offset or 0,
            current_limit=params.limit or 10,
        )
    
    def get_member(self, member_id: UUID) -> CommunityMember:
        member = self.member_repo.get_by_id(member_id)
        if not member:
            raise CommunityMemberNotFoundError(f'Community member with id {member_id} not found')
        return member

    def create_member(self, member_data: CommunityMemberCreate) -> CommunityMemberResponse:
        self.get_community(member_data.community_id)
        self.user_service.get_user(member_data.user_id)
        if self.member_repo.member_exists(member_data.user_id, member_data.community_id):
            raise CommunityMemberAlreadyExistsError(
                f'User with id {member_data.user_id} is already a member of community {member_data.community_id}'
            )
        try:
            member_model = CommunityMember(**member_data.model_dump())
            saved_member = self.member_repo.save(member_model)
            return self._map_member_to_response(saved_member)
        except Exception as e:
            raise UnexpectedCommunityMemberError(f'Unexpected error creating member: {e}')

    def remove_member(self, member_id: UUID) -> bool:
        member = self.get_member(member_id)
        try:
            result = self.member_repo.delete(member)
            return result
        except Exception as e:
            raise UnexpectedCommunityMemberError(f'Unexpected error removing member: {e}') from e

    def update_member_role(self, member_id: UUID, new_role: CommunityMemberRoleEnum) -> CommunityMemberResponse:
        member = self.get_member(member_id)
        member.role = new_role
        try:
            updated_member = self.member_repo.save(member)
            return self._map_member_to_response(updated_member)
        except Exception as e:
            raise UnexpectedCommunityMemberError(f'Unexpected error updating member role: {e}') from e
