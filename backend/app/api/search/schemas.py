import uuid
from typing import List, Literal, Union

from pydantic import BaseModel, ConfigDict


class UserSearchResult(BaseModel):
    id: uuid.UUID | str
    name: str
    profile_image_url: str | None = None
    type: Literal['user'] = 'user'

    model_config = ConfigDict(from_attributes=True)


class PostSearchResult(BaseModel):
    id: uuid.UUID | str
    title: str
    community_id: uuid.UUID | str
    type: Literal['post'] = 'post'

    model_config = ConfigDict(from_attributes=True)


SearchResponse = List[Union[UserSearchResult, PostSearchResult]]
