from typing import List, Union

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db

from . import schemas
from .service import SearchService  # << Importe a classe, não a instância

router = APIRouter(prefix='/search', tags=['Search'])


@router.get(
    '/',
    # O response_model deve ser uma lista dos seus schemas de resultado
    response_model=List[Union[schemas.UserSearchResult, schemas.PostSearchResult]],
    status_code=status.HTTP_200_OK,
    summary='Realiza uma busca por usuários e posts',
)
def search(
    db: Session = Depends(get_db),
    q: str = Query(..., min_length=3, description='Termo a ser buscado'),
    # Peça ao FastAPI para criar e injetar uma instância do SearchService
    search_service: SearchService = Depends(SearchService),
):
    return search_service.perform_search(db=db, query=q)
