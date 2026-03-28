from pydantic_settings import BaseSettings
from pydantic import field_validator
from functools import lru_cache


class Settings(BaseSettings):
    database_url: str
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"
    resend_api_key: str = ""
    environment: str = "development"

    @field_validator("database_url")
    @classmethod
    def fix_db_url(cls, v: str) -> str:
        # Neon gives postgresql:// but asyncpg needs postgresql+asyncpg://
        v = v.replace("postgresql://", "postgresql+asyncpg://", 1)
        # asyncpg doesn't support channel_binding
        v = v.replace("&channel_binding=require", "")
        v = v.replace("?channel_binding=require&", "?")
        v = v.replace("?channel_binding=require", "")
        # asyncpg uses ssl=require not sslmode=require
        v = v.replace("sslmode=require", "ssl=require")
        return v

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
