import os

import cloudinary
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


class CloudinarySettings(BaseSettings):
    CLOUDINARY_CLOUD_NAME: str | None = None
    CLOUDINARY_API_KEY: str | None = None
    CLOUDINARY_API_SECRET: str | None = None

    model_config = ConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore',
    )


cloudinary_settings = CloudinarySettings(_env_file=env_file)


def configure_cloudinary() -> None:
    """Configure Cloudinary with credentials from settings"""
    if cloudinary_settings.CLOUDINARY_CLOUD_NAME:
        cloudinary.config(
            cloud_name=cloudinary_settings.CLOUDINARY_CLOUD_NAME,
            api_key=cloudinary_settings.CLOUDINARY_API_KEY,
            api_secret=cloudinary_settings.CLOUDINARY_API_SECRET,
            secure=True,
        )


configure_cloudinary()
