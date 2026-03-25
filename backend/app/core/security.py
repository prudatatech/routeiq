"""JWT authentication and password hashing utilities."""
from datetime import datetime, timedelta, timezone
from typing import Optional, Union

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import bcrypt
import httpx
from jose import JWTError, jwt
from app.core.config import settings
from app.core.database import get_db
from app.models.models import User
from app.schemas.auth import TokenData

# Global JWKS cache
_jwks_cache = None
_jwks_last_fetch = None

async def get_jwks():
    """Fetch and cache Supabase JWKS for asymmetric verification (ES256)."""
    global _jwks_cache, _jwks_last_fetch
    
    # Refresh cache once daily
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
    except Exception as e:
        # If fetch fails but we have old cache, use it as fallback
        if _jwks_cache:
            return _jwks_cache
        return None

bearer_scheme = HTTPBearer()


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    pw_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pw_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(plain: Union[str, bytes], hashed: Union[str, bytes]) -> bool:
    """Verify a password against a hash using bcrypt."""
    try:
        if isinstance(plain, str):
            plain = plain.encode('utf-8')
        if isinstance(hashed, str):
            hashed = hashed.encode('utf-8')
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
    """Decode and verify JWT token from either local issuer, Supabase Symmetric, or Supabase JWKS."""
    
    # 1. Try local verification (HMAC)
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        role: str = payload.get("role", "driver")
        if user_id:
            return TokenData(user_id=user_id, role=role)
    except JWTError:
        pass

    # 2. Try Supabase Symmetric Verification (HS256)
    if settings.SUPABASE_JWT_SECRET:
        try:
            payload = jwt.decode(token, settings.SUPABASE_JWT_SECRET, algorithms=["HS256"], options={"verify_aud": False})
            user_id: str = payload.get("sub")
            sb_role = payload.get("role", "authenticated")
            metadata = payload.get("user_metadata", {})
            email = payload.get("email") or metadata.get("email")
            full_name = metadata.get("full_name") or metadata.get("name")
            if user_id:
                return TokenData(user_id=user_id, role=sb_role, email=email, full_name=full_name)
        except JWTError:
            pass

    # 3. Try Supabase JWKS (Asymmetric ES256/RS256)
    jwks = await get_jwks()
    if jwks:
        try:
            # We use options={"verify_aud": False} because Supabase uses project-specific audiences
            payload = jwt.decode(token, jwks, algorithms=["ES256", "RS256"], options={"verify_aud": False})
            user_id: str = payload.get("sub")
            sb_role = payload.get("role", "authenticated")
            metadata = payload.get("user_metadata", {})
            email = payload.get("email") or metadata.get("email")
            full_name = metadata.get("full_name") or metadata.get("name")
            if user_id:
                return TokenData(user_id=user_id, role=sb_role, email=email, full_name=full_name)
        except JWTError:
            pass

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, 
        detail="Invalid or expired authentication credentials"
    )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db)
) -> TokenData:
    token_data = await decode_token(credentials.credentials)
    
    # Supabase roles in tokens are generic ('authenticated').
    # We must fetch the local role from our 'users' table.
    import uuid
    try:
        user_uuid = uuid.UUID(token_data.user_id)
    except ValueError:
        return token_data # Fallback if not a UUID
        
    result = await db.execute(select(User).where(User.id == user_uuid))
    user = result.scalar_one_or_none()
    
    if user:
        # Override token info with DB info
        token_data.role = str(user.role)
        token_data.full_name = user.full_name
        token_data.email = user.email
    
    return token_data


def require_role(*roles: str):
    """Dependency factory for role-based access control."""
    async def role_checker(token_data: TokenData = Depends(get_current_user)) -> TokenData:
        # Superadmin has access to everything
        if token_data.role == "superadmin":
            return token_data
            
        if token_data.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{token_data.role}' not authorized. Required: {roles}",
            )
        return token_data
    return role_checker
