from functools import lru_cache
from typing import List, Optional, Union

from pydantic import field_validator
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

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def fix_database_url(cls, v: str) -> str:
        """Fixup for Supabase/Railway URLs to use asyncpg and IPv4."""
        if not v:
            return v
            
        # 1. Standardize protocol for asyncpg
        if v.startswith("postgres://"):
            v = v.replace("postgres://", "postgresql+asyncpg://", 1)
        elif v.startswith("postgresql://") and "+asyncpg" not in v:
            v = v.replace("postgresql://", "postgresql+asyncpg://", 1)

        # 2. Fix IPv6 'Network is unreachable' on Railway by using IPv4 Pooler
        # If it's a standard Supabase hostname like db.xxx.supabase.co
        import re
        match = re.search(r"db\.([a-z0-9]+)\.supabase\.co", v)
        if match:
            project_id = match.group(1)
            # Replace hostname with IPv4 pooler host (defaulting to us-east-1)
            # and update username to 'postgres.[project_id]' as required by the pooler
            v = v.replace(f"db.{project_id}.supabase.co", "aws-0-us-east-1.pooler.supabase.com")
            
            # Ensure the username matches the pooler requirement
            if f"postgres.{project_id}" not in v:
                v = v.replace("postgres:", f"postgres.{project_id}:", 1)
                
            # Note: Do not add sslmode=require here as asyncpg doesn't support it as a kwarg
                
        return v

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_CACHE_TTL: int = 300

    # Celery
    CELERY_BROKER_URL: Optional[str] = None
    CELERY_RESULT_BACKEND: Optional[str] = None

    @field_validator("CELERY_BROKER_URL", "CELERY_RESULT_BACKEND", mode="before")
    @classmethod
    def set_celery_defaults(cls, v: Optional[str], info) -> str:
        # In Pydantic v2, we use info.data to access other fields, but for simplicity
        # if v is None, we return a fallback.
        return v or "redis://localhost:6379/0"

    # External APIs
    GOOGLE_MAPS_API_KEY: str = ""
    SUPABASE_SERVICE_ROLE_KEY: str = ""
    SUPABASE_JWT_SECRET: str = ""
    SUPABASE_JWKS_URL: str = "https://xgihvwtiaqkpusrdvclk.supabase.co/auth/v1/.well-known/jwks.json"
    OPENWEATHER_API_KEY: str = ""
    TOMTOM_API_KEY: str = ""

    # AWS
    AWS_REGION: str = "ap-south-1"
    AWS_S3_BUCKET: str = ""

    # CORS
    ALLOWED_ORIGINS: Union[List[str], str] = ["*"]

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_origins(cls, v: Union[List[str], str]) -> List[str]:
        if isinstance(v, str):
            if v == "*":
                return ["*"]
            return [i.strip() for i in v.split(",")]
        return v

    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
