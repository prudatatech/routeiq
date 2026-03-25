"""JWT authentication and password hashing utilities."""
from datetime import datetime, timedelta, timezone
from typing import Optional, Union

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
import bcrypt

from app.core.config import settings
from app.schemas.auth import TokenData

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


def decode_token(token: str) -> TokenData:
    """Decode and verify JWT token from either local issuer or Supabase."""
    
    # 1. Try local verification first
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        role: str = payload.get("role", "driver")
        if user_id:
            return TokenData(user_id=user_id, role=role)
    except JWTError:
        pass

    # 2. Try Supabase verification if secret is provided
    if settings.SUPABASE_JWT_SECRET:
        try:
            # Supabase tokens typically use HS256
            payload = jwt.decode(token, settings.SUPABASE_JWT_SECRET, algorithms=["HS256"], options={"verify_aud": False})
            user_id: str = payload.get("sub")
            sb_role = payload.get("role", "authenticated")
            
            # Extract email and name from user_metadata (Supabase standard)
            metadata = payload.get("user_metadata", {})
            email = payload.get("email") or metadata.get("email")
            full_name = metadata.get("full_name") or metadata.get("name")
            
            if user_id:
                return TokenData(
                    user_id=user_id, 
                    role=sb_role, 
                    email=email, 
                    full_name=full_name
                )
        except JWTError:
            pass

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, 
        detail="Invalid or expired authentication credentials"
    )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> TokenData:
    return decode_token(credentials.credentials)


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
