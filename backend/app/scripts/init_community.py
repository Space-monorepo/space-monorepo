import app.core.init_db

from app.core.database import get_db
from app.api.communities.model import Community, CommunityMember
from app.api.users.model import User
from app.api.users.service import UserService
from app.api.users.schema import UserCreate
from app.core.transaction import TransactionManager


def init_community():
    db = next(get_db())
    with TransactionManager(db) as tm:
        try:
            user = UserCreate(
                name='Space',
                email='space@space.com',
                hashed_password='spacepassword123',
            )
            user = UserService(tm).create_user(user)
            print(f'User {user.name} created successfully')

            community = Community(
                name='Space',
                description='Space is a community for space enthusiasts.',
                type_community='company',
            )
            db.add(community)
            db.commit()
            db.refresh(community)
            print(f'Community {community.name} created successfully')

            community_member = CommunityMember(
                user_id=user.id,
                community_id=community.id,
                role='admin',
            )
            db.add(community_member)
            db.commit()
            db.refresh(community_member)
            print(f'Community {community.name} member {user.name} created successfully')
        except Exception as e:
            print(f'Error creating community: {e}')
        finally:
            db.close()


if __name__ == '__main__':
    init_community()
