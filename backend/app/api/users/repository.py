from sqlalchemy.orm import Session

from app.api.users.model import User
from app.core.repository import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, db: Session):
        super().__init__(User, db)
        self.db = db

    def get_by_email(self, email: str) -> User | bool:
        return self.db.query(User).filter(User.email == email).first()
