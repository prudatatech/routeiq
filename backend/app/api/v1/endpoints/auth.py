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
    """Sync Supabase User to local public.users table.
    
    Handles both brand new users and linking existing users (by email) to 
    their new Supabase identities (by UUID).
    """
    import uuid
    from sqlalchemy import update
    
    try:
        user_uuid = uuid.UUID(token_data.user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID format in token")

    # 1. Attempt lookup by Supabase UUID
    result = await db.execute(select(User).where(User.id == user_uuid))
    user = result.scalar_one_or_none()
    
    if user:
        return user

    # 2. If not found by ID, attempt lookup by Email to 'bind' existing account
    if token_data.email:
        result = await db.execute(select(User).where(User.email == token_data.email))
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            # We found a user with this email but a different ID.
            # We'll update their ID to the Supabase UUID to bind the identities.
            # Note: This is safe as long as we handle FKs or have no active sessions for old ID.
            old_id = existing_user.id
            try:
                # We use a direct update to change the PK
                await db.execute(
                    update(User)
                    .where(User.id == old_id)
                    .values(id=user_uuid)
                )
                await db.flush()
                # Re-fetch to return the updated object
                result = await db.execute(select(User).where(User.id == user_uuid))
                return result.scalar_one()
            except Exception as e:
                await db.rollback()
                # If PK update fails (e.g. FK constraints), we fall back to creating a new user or erroring
                # For safety, we'll error out here to avoid split identities
                raise HTTPException(status_code=500, detail=f"Identity binding failed: {str(e)}")

    # 3. Create brand new user if none of the above found
    try:
        user = User(
            id=user_uuid,
            email=token_data.email or f"{user_uuid}@auth.supabase",
            full_name=token_data.full_name or "New User",
            hashed_password="SUPABASE_AUTH_EXTERNAL",
            role="driver", # Default role
            is_active=True
        )
        db.add(user)
        await db.flush()
        await db.refresh(user)
        return user
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Database sync failed: {str(e)}")


@router.post("/logout")
async def logout():
    # With JWT, logout is handled client-side (discard tokens)
    # For full revocation: add token to Redis blocklist
    return {"message": "Logged out successfully"}
