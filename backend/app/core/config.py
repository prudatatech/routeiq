from functools import lru_cache
from typing import List, Optional, Union

from pydantic import validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # App
    APP_NAME: str = "RouteIQ"
    APP_ENV: str = "development"
    DEBUG: bool = False
    SECRET_KEY: str = "temporary_secret_key_for_setup"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://routeiq:routeiq_pass@db:5432/routeiq"
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10

    @validator("DATABASE_URL", pre=True)
    def fix_database_url(cls, v: str) -> str:
        """Fixup for Supabase/Railway URLs to use asyncpg."""
        if v.startswith("postgres://"):
            v = v.replace("postgres://", "postgresql+asyncpg://", 1)
        elif v.startswith("postgresql://") and "+asyncpg" not in v:
            v = v.replace("postgresql://", "postgresql+asyncpg://", 1)
        return v

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_CACHE_TTL: int = 300

    # Celery
    CELERY_BROKER_URL: Optional[str] = None
    CELERY_RESULT_BACKEND: Optional[str] = None

    @validator("CELERY_BROKER_URL", pre=True, always=True)
    def set_celery_broker(cls, v: Optional[str], values: dict) -> str:
        return v or values.get("REDIS_URL", "redis://localhost:6379/0")

    @validator("CELERY_RESULT_BACKEND", pre=True, always=True)
    def set_celery_backend(cls, v: Optional[str], values: dict) -> str:
        return v or values.get("REDIS_URL", "redis://localhost:6379/0")

    # External APIs
    GOOGLE_MAPS_API_KEY: str = ""
    OPENWEATHER_API_KEY: str = ""
    TOMTOM_API_KEY: str = ""

    # AWS
    AWS_REGION: str = "ap-south-1"
    AWS_S3_BUCKET: str = ""

    # CORS
    ALLOWED_ORIGINS: Union[List[str], str] = ["*"]

    @validator("ALLOWED_ORIGINS", pre=True)
    def parse_origins(cls, v: Union[List[str], str]) -> List[str]:
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return v

    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
