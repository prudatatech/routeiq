"""Route management endpoints."""
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import Route
from app.schemas.schemas import RouteResponse, TokenData

router = APIRouter()


@router.get("/", response_model=List[RouteResponse])
async def list_routes(
    status: Optional[str] = Query(None),
    vehicle_id: Optional[uuid.UUID] = Query(None),
    skip: int = 0, limit: int = 50,
    db: AsyncSession = Depends(get_db),
    token: TokenData = Depends(get_current_user),
):
    from app.models.models import Vehicle
    q = select(Route)
    if token.role == "driver":
        q = q.join(Vehicle).where(Vehicle.driver_id == uuid.UUID(token.user_id))
    
    if status:
        q = q.where(Route.status == status)
    if vehicle_id:
        q = q.where(Route.vehicle_id == vehicle_id)
        
    q = q.offset(skip).limit(limit)
    result = await db.execute(q)
    return result.scalars().all()


@router.get("/{route_id}", response_model=RouteResponse)
async def get_route(
    route_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    token: TokenData = Depends(get_current_user),
):
    result = await db.execute(
        select(Route).options(joinedload(Route.vehicle)).where(Route.id == route_id)
    )
    route = result.scalar_one_or_none()
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")
        
    if token.role == "driver" and route.vehicle.driver_id != uuid.UUID(token.user_id):
        raise HTTPException(status_code=403, detail="Not authorized to view this route")
        
    return route


@router.patch("/{route_id}/status")
async def update_route_status(
    route_id: uuid.UUID,
    body: dict,
    db: AsyncSession = Depends(get_db),
    token: TokenData = Depends(get_current_user),
):
    result = await db.execute(select(Route).where(Route.id == route_id))
    route = result.scalar_one_or_none()
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")
    route.status = body.get("status", route.status)
    await db.flush()
    return {"id": str(route.id), "status": route.status}
