from datetime import datetime

from pydantic import BaseModel, ConfigDict


class TokenSchema(BaseModel):
    access_token: str
    exp: datetime

    model_config = ConfigDict(
        title='Token Data',
        str_strip_whitespace=True,
        json_schema_extra={
            'example': {'access_token': 'secret_key', 'exp': '2024-12-01'}
        },
    )
