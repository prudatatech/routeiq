"""Telemetry endpoints — live GPS & vehicle data ingestion."""
import uuid
from typing import List
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import get_current_user
from app.core.redis import cache_set
from app.models.models import Telemetry, Vehicle
from app.schemas.schemas import TelemetryCreate, TelemetryResponse, TokenData

router = APIRouter()


@router.post("/", response_model=TelemetryResponse, status_code=201)
async def ingest_telemetry(
    payload: TelemetryCreate,
    db: AsyncSession = Depends(get_db),
    token: TokenData = Depends(get_current_user),
):
    # Check authorization if driver
    result = await db.execute(select(Vehicle).where(Vehicle.id == payload.vehicle_id))
    vehicle = result.scalar_one_or_none()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
        
    if token.role == "driver" and vehicle.driver_id != uuid.UUID(token.user_id):
        raise HTTPException(status_code=403, detail="Not authorized for this vehicle")

    t = Telemetry(**payload.model_dump())
    db.add(t)

    # Update vehicle live position in DB
    vehicle.latitude = payload.latitude
    vehicle.longitude = payload.longitude

    await db.flush()
    await db.refresh(t)

    # Cache latest position in Redis for WebSocket broadcast
    await cache_set(
        f"vehicle:live:{payload.vehicle_id}",
        {"lat": payload.latitude, "lng": payload.longitude, "speed": payload.speed_kmph},
        ttl=120,
    )

    return t


@router.get("/{vehicle_id}/history", response_model=List[TelemetryResponse])
async def telemetry_history(
    vehicle_id: uuid.UUID,
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
    token: TokenData = Depends(get_current_user),
):
    if token.role == "driver":
        # Check if vehicle belongs to driver
        v_result = await db.execute(select(Vehicle).where(Vehicle.id == vehicle_id))
        vehicle = v_result.scalar_one_or_none()
        if not vehicle or vehicle.driver_id != uuid.UUID(token.user_id):
            raise HTTPException(status_code=403, detail="Not authorized to view this history")

    result = await db.execute(
        select(Telemetry)
        .where(Telemetry.vehicle_id == vehicle_id)
        .order_by(desc(Telemetry.timestamp))
        .limit(limit)
    )
    return result.scalars().all()


@router.get("/{vehicle_id}/live")
async def live_position(
    vehicle_id: uuid.UUID, 
    db: AsyncSession = Depends(get_db),
    token: TokenData = Depends(get_current_user)
):
    if token.role == "driver":
        v_result = await db.execute(select(Vehicle).where(Vehicle.id == vehicle_id))
        vehicle = v_result.scalar_one_or_none()
        if not vehicle or vehicle.driver_id != uuid.UUID(token.user_id):
            raise HTTPException(status_code=403, detail="Not authorized to view live data")

    from app.core.redis import cache_get
    data = await cache_get(f"vehicle:live:{vehicle_id}")
    return data or {"error": "No live data available"}
