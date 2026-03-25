"""Route management endpoints."""
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from supabase import Client
from app.core.database import get_db
from app.core.security import get_current_user
from app.schemas.schemas import RouteResponse, TokenData

router = APIRouter()


@router.get("/", response_model=List[RouteResponse])
async def list_routes(
    status: Optional[str] = Query(None),
    vehicle_id: Optional[uuid.UUID] = Query(None),
    skip: int = 0,
    limit: int = 50,
    db: Client = Depends(get_db),
    token: TokenData = Depends(get_current_user),
):
    if token.role == "driver":
        # Get vehicle IDs assigned to this driver
        v_result = db.table("vehicles").select("id").eq("driver_id", token.user_id).execute()
        vehicle_ids = [v["id"] for v in (v_result.data or [])]
        if not vehicle_ids:
            return []
        query = db.table("routes").select("*").in_("vehicle_id", vehicle_ids)
    else:
        query = db.table("routes").select("*")

    if status:
        query = query.eq("status", status)
    if vehicle_id:
        query = query.eq("vehicle_id", str(vehicle_id))

    result = query.range(skip, skip + limit - 1).execute()
    return result.data or []


@router.get("/{route_id}", response_model=RouteResponse)
async def get_route(
    route_id: uuid.UUID,
    db: Client = Depends(get_db),
    token: TokenData = Depends(get_current_user),
):
    result = db.table("routes").select("*, vehicles(driver_id)").eq("id", str(route_id)).maybe_single().execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Route not found")

    route = result.data
    if token.role == "driver":
        vehicle = (route.get("vehicles") or {})
        if vehicle.get("driver_id") != token.user_id:
            raise HTTPException(status_code=403, detail="Not authorized to view this route")

    return route


@router.patch("/{route_id}/status")
async def update_route_status(
    route_id: uuid.UUID,
    body: dict,
    db: Client = Depends(get_db),
    token: TokenData = Depends(get_current_user),
):
    result = db.table("routes").select("id").eq("id", str(route_id)).maybe_single().execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Route not found")

    new_status = body.get("status")
    update_result = db.table("routes").update({"status": new_status}).eq("id", str(route_id)).execute()
    if not update_result.data:
        raise HTTPException(status_code=500, detail="Update failed")
    return {"id": str(route_id), "status": new_status}
