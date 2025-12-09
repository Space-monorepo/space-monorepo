from typing import List, Union

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.users.model import User
from app.auth.deps import get_current_user
from app.core.database import get_db

from . import schemas
from .service import SearchService

router = APIRouter(prefix='/search', tags=['Search'])


@router.get(
    '/',
    response_model=List[Union[schemas.UserSearchResult, schemas.PostSearchResult]],
    status_code=status.HTTP_200_OK,
    summary='Realiza uma busca por usuários e posts nas comunidades do usuário',
)
def search(
    db: Session = Depends(get_db),
    q: str = Query(..., min_length=3, description='Termo a ser buscado'),
    search_service: SearchService = Depends(SearchService),
    current_user: User = Depends(get_current_user),
):
    return search_service.perform_search(db=db, query=q, current_user=current_user)
