from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="USR_", env_file=".env", extra="ignore")

    APP_VERSION: str = "1.0.0"
    ENV: str = Field(default="development")

    # Database
    DATABASE_URL: str = Field(
        ...,
        description="Async PostgreSQL DSN, e.g. postgresql+asyncpg://user:pass@host/db",
        example="postgresql+asyncpg://postgres:postgres@localhost:5432/fb_users",
    )

    # JWT (must match gateway secret)
    JWT_SECRET_KEY: str = Field(..., description="256-bit JWT secret")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRY_SECONDS: int = 3600


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]


settings = get_settings()
