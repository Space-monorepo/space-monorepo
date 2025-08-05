from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.users.schema import LoginSchema, UserCreate, UserResponse, UserUpdate
from app.api.users.service import UserService
from app.auth.deps import get_current_user
from app.auth.schema import TokenSchema
from app.auth.security import AuthService
from app.core.database import get_db
from app.core.transaction import TransactionManager

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/users/login')
oauth2_request_form = Depends(OAuth2PasswordRequestForm)

router = APIRouter(prefix='/users', tags=['users'])


@router.post('/signup', response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def signup(user: UserCreate, session: Session = Depends(get_db)) -> UserResponse:
    with TransactionManager(session) as tm:
        user_created = UserService(tm).create_user(user)
        return UserResponse.model_validate(user_created)


@router.post('/login', response_model=TokenSchema, status_code=status.HTTP_200_OK)
def login(
    session: Session = Depends(get_db),
    login_form: OAuth2PasswordRequestForm = oauth2_request_form,
) -> TokenSchema:
    with TransactionManager(session) as tm:
        user = LoginSchema(email=login_form.username, password=login_form.password)
        token_data = AuthService(tm).login(user)
        return token_data


@router.get('/me', response_model=UserResponse, status_code=status.HTTP_200_OK)
def get_user(
    session: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
) -> UserResponse:
    with TransactionManager(session) as tm:
        user = UserService(tm).get_user(current_user.id)
        return UserResponse.model_validate(user)


@router.get('/{email}', response_model=UserResponse, status_code=status.HTTP_200_OK)
def get_user_by_email(email: str, session: Session = Depends(get_db)) -> UserResponse:
    with TransactionManager(session) as tm:
        user = UserService(tm).get_by_email(email)
        return UserResponse.model_validate(user)


@router.patch('/me', response_model=UserResponse, status_code=status.HTTP_200_OK)
def update_user(
    user: UserUpdate,
    session: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
) -> UserResponse:
    with TransactionManager(session) as tm:
        user_updated = UserService(tm).update_user(current_user.id, user)
        return UserResponse.model_validate(user_updated)


@router.delete('/me', response_model=bool, status_code=status.HTTP_200_OK)
def delete_user(
    session: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
) -> bool:
    with TransactionManager(session) as tm:
        return UserService(tm).delete_user(current_user.id)
