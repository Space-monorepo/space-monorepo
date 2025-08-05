from typing import Generic, TypeVar
from app.api.post.schemas import PostTypeEnum

from pydantic import BaseModel, Field, ConfigDict

T = TypeVar('T')

class PaginationSearchParams(BaseModel):
    name: str | None = Field(None, description="The filters to apply to the search")
    status: str | None = Field(None, description="The filters to apply to the search")
    status_campaign: list[str] | None = Field(None, description="The filters to apply to the search")
    type_post: PostTypeEnum | None = Field(None, description="The filters to apply to the search")
    offset: int | None = Field(0, description="The offset to apply to the search")
    limit: int | None = Field(10, description="The limit to apply to the search")
    
    model_config = ConfigDict(
        title='Paginated Search Params',
        from_attributes=True,
        json_schema_extra={
            'example': {
                'name': 'example name',
                'status': 'example status',
                'type_post': PostTypeEnum.CAMPAIGN,
                'offset': 0,
                'limit': 10,
            }
        }
    )


class PaginationResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    has_more: bool
    current_offset: int
    current_limit: int
    
    model_config = ConfigDict(
        title='Pagination Response',
        from_attributes=True,
        json_schema_extra={
            'example': {
                'items': [],
                'total': 0,
                'has_more': False,
                'current_offset': 0,
                'current_limit': 10,
            }
        }
    )


class ErrorResponse(BaseModel):
    message: str
    error_type: str
    details: dict = Field(default_factory=dict)

    model_config = ConfigDict(
        title='Error Response',
        from_attributes=True,
        json_schema_extra={
            'example': {
                'message': 'Error message',
                'error_type': 'Error type',
                'details': {}
            }
        }
    )
