"""Vehicle management endpoints."""
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from supabase import Client
from app.core.database import get_db
from app.core.security import get_current_user, require_role
from app.core.redis import cache_get, cache_set
from app.schemas.schemas import TokenData, VehicleCreate, VehicleResponse, VehicleUpdate, FleetSummary

router = APIRouter()


@router.get("/", response_model=List[VehicleResponse])
async def list_vehicles(
    status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Client = Depends(get_db),
    token: TokenData = Depends(get_current_user),
):
    cache_key = f"vehicles:list:{token.user_id}:{status}:{skip}:{limit}"
    cached = await cache_get(cache_key)
    if cached:
        return cached

    query = db.table("vehicles").select("*")

    if token.role == "driver":
        query = query.eq("driver_id", token.user_id)
    elif status:
        query = query.eq("status", status)

    result = query.range(skip, skip + limit - 1).execute()
    data = result.data or []
    await cache_set(cache_key, data, ttl=30)
    return data


@router.post("/", response_model=VehicleResponse, status_code=201)
async def create_vehicle(
    payload: VehicleCreate,
    db: Client = Depends(get_db),
    _: TokenData = Depends(require_role("admin", "manager")),
):
    result = db.table("vehicles").insert(payload.model_dump()).execute()
    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to create vehicle")
    return result.data[0]


@router.get("/summary", response_model=FleetSummary)
async def fleet_summary(
    db: Client = Depends(get_db),
    _: TokenData = Depends(get_current_user),
):
    result = db.table("vehicles").select("status").execute()
    vehicles = result.data or []

    counts: dict = {}
    for v in vehicles:
        s = v.get("status", "unknown")
        counts[s] = counts.get(s, 0) + 1

    total = sum(counts.values())
    return FleetSummary(
        total=total,
        active=counts.get("on_route", 0),
        idle=counts.get("idle", 0) + counts.get("available", 0),
        maintenance=counts.get("maintenance", 0),
        offline=counts.get("offline", 0),
    )


@router.get("/{vehicle_id}", response_model=VehicleResponse)
async def get_vehicle(
    vehicle_id: uuid.UUID,
    db: Client = Depends(get_db),
    token: TokenData = Depends(get_current_user),
):
    result = db.table("vehicles").select("*").eq("id", str(vehicle_id)).maybe_single().execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    vehicle = result.data
    if token.role == "driver" and vehicle.get("driver_id") != token.user_id:
        raise HTTPException(status_code=403, detail="Not authorized to view this vehicle")

    return vehicle


@router.patch("/{vehicle_id}", response_model=VehicleResponse)
async def update_vehicle(
    vehicle_id: uuid.UUID,
    payload: VehicleUpdate,
    db: Client = Depends(get_db),
    _: TokenData = Depends(require_role("admin", "manager")),
):
    existing = db.table("vehicles").select("id").eq("id", str(vehicle_id)).maybe_single().execute()
    if not existing.data:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    update_data = {k: v for k, v in payload.model_dump().items() if v is not None}
    result = db.table("vehicles").update(update_data).eq("id", str(vehicle_id)).execute()
    if not result.data:
        raise HTTPException(status_code=500, detail="Update failed")
    return result.data[0]


@router.delete("/{vehicle_id}", status_code=204)
async def delete_vehicle(
    vehicle_id: uuid.UUID,
    db: Client = Depends(get_db),
    _: TokenData = Depends(require_role("admin")),
):
    existing = db.table("vehicles").select("id").eq("id", str(vehicle_id)).maybe_single().execute()
    if not existing.data:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    db.table("vehicles").delete().eq("id", str(vehicle_id)).execute()
