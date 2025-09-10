import os

from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ENVIRONMENT: str

    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    DATABASE_URL: str

    MONGO_URI: str | None = None
    MONGO_INITDB_DATABASE: str | None = None
    RESET_DB: bool | None = None

    model_config = ConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore',
    )


env = os.getenv('ENVIRONMENT', 'development')
env_file = f'.env.{env}' if env != 'development' else '.env'

settings = Settings(_env_file=env_file)
