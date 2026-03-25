"""Dashboard analytics endpoints."""
import uuid
from datetime import datetime, timezone, date
from fastapi import APIRouter, Depends
from supabase import Client
from app.core.database import get_db
from app.core.security import get_current_user
from app.schemas.schemas import KPIResponse, TokenData

router = APIRouter()


@router.get("/kpis", response_model=KPIResponse)
async def get_kpis(
    db: Client = Depends(get_db),
    token: TokenData = Depends(get_current_user),
):
    """Aggregate KPIs for admin/manager dashboard using Supabase client."""
    today = datetime.combine(date.today(), datetime.min.time()).replace(tzinfo=timezone.utc).isoformat()
    
    # 1. Active Vehicles Count
    v_query = db.table("vehicles").select("id", count="exact").eq("status", "on_route")
    if token.role == "driver":
        v_query = v_query.eq("driver_id", token.user_id)
    
    v_result = v_query.execute()
    active_vehicles = v_result.count or 0

    # 2. Routes Today
    r_query = db.table("routes").select("*").gte("created_at", today)
    if token.role == "driver":
        # Get vehicle IDs for driver
        v_ids_result = db.table("vehicles").select("id").eq("driver_id", token.user_id).execute()
        v_ids = [v["id"] for v in (v_ids_result.data or [])]
        if not v_ids:
            routes_today = []
        else:
            r_query = r_query.in_("vehicle_id", v_ids)
            r_result = r_query.execute()
            routes_today = r_result.data or []
    else:
        r_result = r_query.execute()
        routes_today = r_result.data or []

    total_deliveries = len(routes_today)
    completed = sum(1 for r in routes_today if r.get("status") == "completed")
    on_time_rate = (completed / total_deliveries * 100) if total_deliveries > 0 else 0.0
    
    fuel_today = sum((r.get("estimated_fuel_liters") or 0.0) for r in routes_today) * 95  # ₹95/L
    
    avg_score = sum((r.get("optimization_score") or 0.8) for r in routes_today) / max(1, len(routes_today))
    fuel_saved_pct = avg_score * 20  # up to 20% based on optimization score
    
    if total_deliveries == 0:
        on_time_rate = 100.0
        avg_score = 1.0

    return KPIResponse(
        active_vehicles=active_vehicles,
        on_time_rate_pct=round(on_time_rate, 1),
        fuel_cost_today=round(fuel_today, 2),
        fuel_saved_pct=round(fuel_saved_pct, 1),
        total_deliveries_today=total_deliveries,
        avg_eta_accuracy_pct=round(on_time_rate * 0.95, 1),
        rerouting_events_today=max(0, total_deliveries // 8),
    )
