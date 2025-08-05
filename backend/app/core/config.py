from pydantic import ConfigDict
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    TEST_MODE: bool
    RESET_DB: bool
    MONGO_URI: str
    MONGO_INITDB_DATABASE: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    DATABASE_URL: str
    DATABASE_URL_TEST: str

    @property
    def active_database_url(self) -> str:
        return self.DATABASE_URL_TEST if self.TEST_MODE else self.DATABASE_URL

    model_config = ConfigDict(env_file='.env', env_file_encoding='utf-8', extra='allow')


settings = Settings()

print(f"MONGO_URI: {settings.MONGO_URI}")
print(f"MONGO_INITDB_DATABASE: {settings.MONGO_INITDB_DATABASE}")