"""Authentication endpoints."""
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import (
    create_access_token, create_refresh_token,
    decode_token, hash_password, verify_password,
    get_current_user
)
from app.models.models import User
from app.schemas.auth import TokenData
from app.schemas.schemas import LoginRequest, TokenResponse, UserCreate, UserResponse

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(payload: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == payload.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        email=payload.email,
        full_name=payload.full_name,
        hashed_password=hash_password(payload.password),
        role=payload.role,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == payload.email))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account disabled")

    user.last_login = datetime.now(timezone.utc)

    token_data = {"sub": str(user.id), "role": str(user.role)}
    return TokenResponse(
        access_token=create_access_token(token_data),
        refresh_token=create_refresh_token(token_data),
        role=str(user.role),
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh(body: dict, db: AsyncSession = Depends(get_db)):
    token = body.get("refresh_token")
    if not token:
        raise HTTPException(status_code=400, detail="refresh_token required")

    token_data = await decode_token(token)
    result = await db.execute(select(User).where(User.id == token_data.user_id))
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")

    td = {"sub": str(user.id), "role": str(user.role)}
    return TokenResponse(
        access_token=create_access_token(td),
        refresh_token=create_refresh_token(td),
        role=str(user.role),
    )


@router.post("/sync", response_model=UserResponse)
async def sync_user(
    db: AsyncSession = Depends(get_db),
    token_data: TokenData = Depends(get_current_user)
):
    """Sync Supabase User to local public.users table."""
    import uuid
    try:
        user_uuid = uuid.UUID(token_data.user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID format in token")

    result = await db.execute(select(User).where(User.id == user_uuid))
    user = result.scalar_one_or_none()
    
    if not user:
        # Create user if doesn't exist (e.g. first login via Supabase)
        # Use info from token metadata extracted in decode_token
        user = User(
            id=user_uuid,
            email=token_data.email or f"{user_uuid}@auth.supabase",
            full_name=token_data.full_name or "New User",
            hashed_password="SUPABASE_AUTH_EXTERNAL",
            role="driver", # Default role for new signups
            is_active=True
        )
        db.add(user)
        try:
            await db.flush()
            await db.refresh(user)
        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail=f"Database sync failed: {str(e)}")
    
    return user


@router.post("/logout")
async def logout():
    # With JWT, logout is handled client-side (discard tokens)
    # For full revocation: add token to Redis blocklist
    return {"message": "Logged out successfully"}
