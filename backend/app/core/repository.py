import logging
from typing import Generic, TypeVar
from uuid import UUID

from sqlalchemy.orm import DeclarativeBase, Session

from app.utils.schema import PaginationSearchParams

Model = TypeVar('Model', bound=DeclarativeBase)


class BaseRepository(Generic[Model]):
    def __init__(self, model: Generic[Model], session: Session):
        self.model = model
        self.session = session
        self.logger = logging.getLogger(__name__)

    def get_by_id(self, id: UUID) -> Model:
        model = self.session.query(self.model).filter(self.model.id == id).first()
        if model:
            self.logger.debug(
                f'Model {self.model.__qualname__} with id {id} retrieved successfully'
            )
            return model
        else:
            self.logger.warning(
                f'Model {self.model.__qualname__} with id {id} not found'
            )

    def save(self, model: Model) -> Model:
        self.session.add(model)
        self.session.flush()
        self.session.refresh(model)
        self.logger.debug(
            f'Model {self.model.__qualname__} with id {model.id} saved successfully'
        )
        return model

    def delete(self, model: Model) -> bool:
        self.session.delete(model)
        self.session.flush()
        self.logger.debug(
            f'Model {self.model.__qualname__} with id {model.id} deleted successfully'
        )
        return True

    def list_all(self, params: PaginationSearchParams) -> tuple[list[Model], int]:
        query = self.session.query(self.model)

        if params.name:
            query = query.filter(
                self.model.name.ilike(f'%{params.name}%'),
            )

        models = query.offset(params.offset).limit(params.limit).all()
        total = query.count()
        self.logger.debug(f'Listing all models for {self.model.__qualname__}')
        return models, total
