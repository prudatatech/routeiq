"""Authentication endpoints."""
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from supabase import Client

from app.core.database import get_db
from app.core.security import (
    create_access_token, create_refresh_token,
    decode_token, hash_password, verify_password,
    get_current_user,
)
from app.schemas.auth import TokenData
from app.schemas.schemas import LoginRequest, TokenResponse, UserCreate, UserResponse

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(payload: UserCreate, db: Client = Depends(get_db)):
    existing = db.table("users").select("id").eq("email", payload.email).execute()
    if existing.data:
        raise HTTPException(status_code=400, detail="Email already registered")

    user_data = {
        "email": payload.email,
        "full_name": payload.full_name,
        "hashed_password": hash_password(payload.password),
        "role": payload.role,
        "is_active": True,
    }
    result = db.table("users").insert(user_data).execute()
    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to create user")
    return result.data[0]


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, db: Client = Depends(get_db)):
    result = db.table("users").select("*").eq("email", payload.email).maybe_single().execute()
    user = result.data

    if not user or not verify_password(payload.password, user["hashed_password"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    if not user.get("is_active", True):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account disabled")

    db.table("users").update({"last_login": datetime.now(timezone.utc).isoformat()}).eq("id", user["id"]).execute()

    token_data = {"sub": str(user["id"]), "role": user["role"]}
    return TokenResponse(
        access_token=create_access_token(token_data),
        refresh_token=create_refresh_token(token_data),
        role=user["role"],
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh(body: dict, db: Client = Depends(get_db)):
    token = body.get("refresh_token")
    if not token:
        raise HTTPException(status_code=400, detail="refresh_token required")

    token_data = await decode_token(token)
    result = db.table("users").select("*").eq("id", token_data.user_id).maybe_single().execute()
    user = result.data

    if not user or not user.get("is_active", True):
        raise HTTPException(status_code=401, detail="User not found or inactive")

    td = {"sub": str(user["id"]), "role": user["role"]}
    return TokenResponse(
        access_token=create_access_token(td),
        refresh_token=create_refresh_token(td),
        role=user["role"],
    )


@router.post("/sync", response_model=UserResponse)
async def sync_user(
    db: Client = Depends(get_db),
    token_data: TokenData = Depends(get_current_user),
):
    """Sync Supabase User to local public.users table."""
    import uuid as uuid_lib

    try:
        user_uuid = str(uuid_lib.UUID(token_data.user_id))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID format in token")

    # 1. Lookup by Supabase UUID
    result = db.table("users").select("*").eq("id", user_uuid).maybe_single().execute()
    if result.data:
        return result.data

    # 2. Lookup by email to bind existing account
    if token_data.email:
        email_result = db.table("users").select("*").eq("email", token_data.email).maybe_single().execute()
        if email_result.data:
            # Update the existing user's ID to Supabase UUID
            try:
                update_result = db.table("users").update({"id": user_uuid}).eq("email", token_data.email).execute()
                if update_result.data:
                    return update_result.data[0]
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Identity binding failed: {str(e)}")

    # 3. Create new user — first user gets admin role
    count_result = db.table("users").select("id", count="exact").execute()
    user_count = count_result.count or 0
    default_role = "admin" if user_count == 0 else "driver"

    new_user = {
        "id": user_uuid,
        "email": token_data.email or f"{user_uuid}@auth.supabase",
        "full_name": token_data.full_name or "New User",
        "hashed_password": "SUPABASE_AUTH_EXTERNAL",
        "role": default_role,
        "is_active": True,
    }
    try:
        create_result = db.table("users").insert(new_user).execute()
        if not create_result.data:
            raise HTTPException(status_code=500, detail="Database sync failed")
        return create_result.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database sync failed: {str(e)}")


@router.post("/logout")
async def logout():
    return {"message": "Logged out successfully"}
