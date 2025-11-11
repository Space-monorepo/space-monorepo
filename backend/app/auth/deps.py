import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.api.comment.service import CommentService
from app.api.communities.exceptions import CommunityMemberNotFoundError
from app.api.communities.model import CommunityMember
from app.api.communities.service import CommunityService
from app.api.post.service import PostService
from app.api.users.model import User
from app.api.users.service import UserService
from app.core.config import settings
from app.core.database import get_db
from app.core.transaction import TransactionManager

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/users/login')


def get_current_user(
    session: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> User:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except jwt.ExpiredSignatureError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail='Token expired.'
        ) from e
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail='Token invalid.'
        ) from e
    email = payload.get('sub')
    with TransactionManager(session) as tm:
        user = UserService(tm).get_by_email(email, flag=None)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail='User not found.'
        )
    return user


def require_roles(allowed_roles: list[str]):
    def role_checker(
        community_id: str,
        session: Session = Depends(get_db),
        user: User = Depends(get_current_user),
    ) -> CommunityMember:
        with TransactionManager(session) as tm:
            try:
                member = CommunityService(tm).get_member_association(
                    user.id, community_id
                )
            except CommunityMemberNotFoundError:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, detail='User not allowed.'
                )
        if allowed_roles == ['member']:
            return member
        if member.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail='User not allowed.'
            )
        return member

    return role_checker


def require_post_owner(
    post_id: str,
    session: Session = Depends(get_db),
    member: CommunityMember = Depends(require_roles(['member'])),
) -> CommunityMember:
    with TransactionManager(session) as tm:
        post = PostService(tm).get_post(post_id)
    if str(post.user.id) != str(member.user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail='User not allowed.'
        )
    return member


def require_comment_owner(
    comment_id: str,
    session: Session = Depends(get_db),
    member: CommunityMember = Depends(require_roles(['member'])),
) -> CommunityMember:
    with TransactionManager(session) as tm:
        comment = CommentService(tm).get_comment(comment_id)
    if str(comment.member.id) != str(member.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail='User not allowed.'
        )
    return member
