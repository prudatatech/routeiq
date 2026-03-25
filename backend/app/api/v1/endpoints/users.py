"""User management endpoints."""
import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from supabase import Client
from app.core.database import get_db
from app.core.security import get_current_user, require_role
from app.schemas.schemas import TokenData, UserResponse, UserUpdate

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_me(token: TokenData = Depends(get_current_user), db: Client = Depends(get_db)):
    result = db.table("users").select("*").eq("id", token.user_id).maybe_single().execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="User not found")
    return result.data


@router.get("/", response_model=List[UserResponse])
async def list_users(
    db: Client = Depends(get_db),
    _: TokenData = Depends(require_role("admin", "superadmin")),
):
    result = db.table("users").select("*").execute()
    return result.data or []


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: uuid.UUID,
    payload: UserUpdate,
    db: Client = Depends(get_db),
    _: TokenData = Depends(require_role("admin", "superadmin")),
):
    existing = db.table("users").select("id").eq("id", str(user_id)).maybe_single().execute()
    if not existing.data:
        raise HTTPException(status_code=404, detail="User not found")

    update_data = {k: v for k, v in payload.model_dump().items() if v is not None}
    result = db.table("users").update(update_data).eq("id", str(user_id)).execute()
    if not result.data:
        raise HTTPException(status_code=500, detail="Update failed")
    return result.data[0]
