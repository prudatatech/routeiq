"""JWT authentication and password hashing utilities."""
from datetime import datetime, timedelta, timezone
from typing import Optional, Union

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import bcrypt
import httpx
from jose import JWTError, jwt
from supabase import Client
from app.core.config import settings
from app.core.database import get_db
from app.schemas.auth import TokenData

# Global JWKS cache
_jwks_cache = None
_jwks_last_fetch = None

async def get_jwks():
    """Fetch and cache Supabase JWKS for asymmetric verification (ES256)."""
    global _jwks_cache, _jwks_last_fetch

    now = datetime.now(timezone.utc)
    if _jwks_cache and _jwks_last_fetch and (now - _jwks_last_fetch).days < 1:
        return _jwks_cache

    if not settings.SUPABASE_JWKS_URL:
        return None

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(settings.SUPABASE_JWKS_URL)
            response.raise_for_status()
            _jwks_cache = response.json()
            _jwks_last_fetch = now
            return _jwks_cache
    except Exception:
        return _jwks_cache  # Return old cache as fallback


bearer_scheme = HTTPBearer()


def hash_password(password: str) -> str:
    pw_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pw_bytes, salt).decode("utf-8")


def verify_password(plain: Union[str, bytes], hashed: Union[str, bytes]) -> bool:
    try:
        if isinstance(plain, str):
            plain = plain.encode("utf-8")
        if isinstance(hashed, str):
            hashed = hashed.encode("utf-8")
        return bcrypt.checkpw(plain, hashed)
    except Exception:
        return False


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


async def decode_token(token: str) -> TokenData:
    """Decode JWT — tries local HMAC, Supabase symmetric, then JWKS."""

    # 1. Local HMAC
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = payload.get("sub")
        if user_id:
            return TokenData(user_id=user_id, role=payload.get("role", "driver"))
    except JWTError:
        pass

    # 2. Supabase Symmetric (HS256)
    if settings.SUPABASE_JWT_SECRET:
        try:
            payload = jwt.decode(
                token, settings.SUPABASE_JWT_SECRET,
                algorithms=["HS256"], options={"verify_aud": False}
            )
            user_id = payload.get("sub")
            metadata = payload.get("user_metadata", {})
            if user_id:
                return TokenData(
                    user_id=user_id,
                    role=payload.get("role", "authenticated"),
                    email=payload.get("email") or metadata.get("email"),
                    full_name=metadata.get("full_name") or metadata.get("name"),
                )
        except JWTError:
            pass

    # 3. Supabase JWKS (ES256/RS256)
    jwks = await get_jwks()
    if jwks:
        try:
            payload = jwt.decode(
                token, jwks,
                algorithms=["ES256", "RS256"], options={"verify_aud": False}
            )
            user_id = payload.get("sub")
            metadata = payload.get("user_metadata", {})
            if user_id:
                return TokenData(
                    user_id=user_id,
                    role=payload.get("role", "authenticated"),
                    email=payload.get("email") or metadata.get("email"),
                    full_name=metadata.get("full_name") or metadata.get("name"),
                )
        except JWTError:
            pass

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired authentication credentials",
    )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Client = Depends(get_db),
) -> TokenData:
    token_data = await decode_token(credentials.credentials)

    # Fetch the local role from our users table via Supabase client
    try:
        import uuid
        user_uuid = str(uuid.UUID(token_data.user_id))
        result = db.table("users").select("id,role,full_name,email").eq("id", user_uuid).maybe_single().execute()
        if result.data:
            token_data.role = result.data.get("role", token_data.role)
            token_data.full_name = result.data.get("full_name", token_data.full_name)
            token_data.email = result.data.get("email", token_data.email)
    except Exception:
        pass  # Fall back to token claims

    return token_data


def require_role(*roles: str):
    """Dependency factory for role-based access control."""
    async def role_checker(
        token_data: TokenData = Depends(get_current_user),
    ) -> TokenData:
        if token_data.role == "superadmin":
            return token_data
        if token_data.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{token_data.role}' not authorized. Required: {roles}",
            )
        return token_data
    return role_checker
