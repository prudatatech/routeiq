"""Telemetry endpoints — live GPS & vehicle data ingestion."""
import uuid
from typing import List
from fastapi import APIRouter, Depends, Query, HTTPException
from supabase import Client
from app.core.database import get_db
from app.core.security import get_current_user
from app.core.redis import cache_set
from app.schemas.schemas import TelemetryCreate, TelemetryResponse, TokenData

router = APIRouter()


@router.post("/", response_model=TelemetryResponse, status_code=201)
async def ingest_telemetry(
    payload: TelemetryCreate,
    db: Client = Depends(get_db),
    token: TokenData = Depends(get_current_user),
):
    # Check authorization
    v_res = db.table("vehicles").select("*").eq("id", str(payload.vehicle_id)).maybe_single().execute()
    vehicle = v_res.data
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
        
    if token.role == "driver" and vehicle.get("driver_id") != token.user_id:
        raise HTTPException(status_code=403, detail="Not authorized for this vehicle")

    # Insert telemetry
    t_res = db.table("telemetry").insert(payload.model_dump()).execute()
    if not t_res.data:
        raise HTTPException(status_code=500, detail="Failed to save telemetry")

    # Update vehicle live position
    db.table("vehicles").update({
        "latitude": payload.latitude,
        "longitude": payload.longitude
    }).eq("id", str(payload.vehicle_id)).execute()

    # Cache latest position for WebSocket broadcast
    await cache_set(
        f"vehicle:live:{payload.vehicle_id}",
        {"lat": payload.latitude, "lng": payload.longitude, "speed": payload.speed_kmph},
        ttl=120,
    )

    return t_res.data[0]


@router.get("/{vehicle_id}/history", response_model=List[TelemetryResponse])
async def telemetry_history(
    vehicle_id: uuid.UUID,
    limit: int = Query(100, ge=1, le=1000),
    db: Client = Depends(get_db),
    token: TokenData = Depends(get_current_user),
):
    if token.role == "driver":
        v_res = db.table("vehicles").select("driver_id").eq("id", str(vehicle_id)).maybe_single().execute()
        if not v_res.data or v_res.data.get("driver_id") != token.user_id:
            raise HTTPException(status_code=403, detail="Not authorized to view this history")

    result = db.table("telemetry") \
               .select("*") \
               .eq("vehicle_id", str(vehicle_id)) \
               .order("timestamp", desc=True) \
               .limit(limit) \
               .execute()
    
    return result.data or []


@router.get("/{vehicle_id}/live")
async def live_position(
    vehicle_id: uuid.UUID, 
    db: Client = Depends(get_db),
    token: TokenData = Depends(get_current_user)
):
    if token.role == "driver":
        v_res = db.table("vehicles").select("driver_id").eq("id", str(vehicle_id)).maybe_single().execute()
        if not v_res.data or v_res.data.get("driver_id") != token.user_id:
            raise HTTPException(status_code=403, detail="Not authorized to view live data")

    from app.core.redis import cache_get
    data = await cache_get(f"vehicle:live:{vehicle_id}")
    return data or {"error": "No live data available"}
