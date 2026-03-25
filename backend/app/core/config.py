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
        project_id = "xgihvwtiaqkpusrdvclk" # Default for this project
        
        # Try to extract project_id from URL if present
        host_match = re.search(r"@db\.([a-z0-9]+)\.supabase\.co", v)
        if host_match:
            project_id = host_match.group(1)
            # Switch to IPv4 Pooler host to avoid Railway IPv6 issues
            v = v.replace(f"db.{project_id}.supabase.co", "aws-0-us-east-1.pooler.supabase.com")
            # Ensure port is set to pooler port if we switched hostname
            if ":5432" in v:
                v = v.replace(":5432", ":6543")

        # 3. Apply Multi-Tenancy Username Format (postgres.[project_id])
        # This is REQUIRED by Supabase pooler (port 6543)
        if "pooler.supabase.com" in v or ":6543" in v:
            if f"postgres.{project_id}" not in v:
                # Replace 'postgres' with 'postgres.[project_id]'
                # We specifically look for '://postgres:' to avoid replacing other parts
                v = v.replace("://postgres:", f"://postgres.{project_id}:", 1)
                
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
