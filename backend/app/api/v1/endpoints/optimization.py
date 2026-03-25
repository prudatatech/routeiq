"""Route optimization endpoints using VRP solver."""
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from supabase import Client
from app.core.database import get_db
from app.core.security import get_current_user, require_role
from app.ml.vrp_solver import Location, VehicleConfig, solve_vrp_ortools
from app.schemas.schemas import (
    OptimizationRequest,
    OptimizationResponse,
    RouteResponse,
    TokenData,
)

router = APIRouter()


@router.post("/", response_model=OptimizationResponse)
async def optimize_routes(
    payload: OptimizationRequest,
    background_tasks: BackgroundTasks,
    db: Client = Depends(get_db),
    token: TokenData = Depends(require_role("admin", "manager")),
):
    """Migrated to Supabase client - Load data, solve VRP, and save result."""

    # 1. Load depot
    if payload.depot_id and str(payload.depot_id) != '00000000-0000-0000-0000-000000000001':
        depot_res = db.table("depots").select("*").eq("id", str(payload.depot_id)).maybe_single().execute()
    else:
        depot_res = db.table("depots").select("*").limit(1).maybe_single().execute()
    
    depot = depot_res.data
    if not depot:
        raise HTTPException(status_code=404, detail="Depot not found")

    # 2. Load vehicles
    v_query = db.table("vehicles").select("*")
    if payload.vehicle_ids:
        v_query = v_query.in_("id", [str(vid) for vid in payload.vehicle_ids])
    else:
        v_query = v_query.in_("status", ["available", "idle"]).limit(5)
    
    v_res = v_query.execute()
    vehicles = v_res.data or []
    if not vehicles:
        raise HTTPException(status_code=404, detail="No available vehicles found")

    # 3. Load delivery points
    dp_query = db.table("delivery_points").select("*")
    if payload.delivery_point_ids:
        dp_query = dp_query.in_("id", [str(dpid) for dpid in payload.delivery_point_ids])
    else:
        dp_query = dp_query.eq("status", "pending").limit(20)
    
    dp_res = dp_query.execute()
    delivery_points = dp_res.data or []
    if not delivery_points:
        raise HTTPException(status_code=404, detail="No pending delivery points found")

    # 4. Build solver input
    depot_loc = Location(
        id=str(depot["id"]),
        lat=depot["latitude"],
        lng=depot["longitude"],
    )
    locations = [depot_loc]
    for dp in delivery_points:
        locations.append(
            Location(
                id=str(dp["id"]),
                lat=dp["latitude"],
                lng=dp["longitude"],
                demand_kg=dp["demand_kg"],
                time_window_start=dp.get("time_window_start") or 0,
                time_window_end=dp.get("time_window_end") or 1440,
                service_time=dp["service_time_minutes"],
            )
        )

    vehicle_configs = [
        VehicleConfig(
            id=str(v["id"]),
            capacity_kg=v["capacity_kg"],
            start_location=depot_loc,
        )
        for v in vehicles
    ]

    # 5. Run solver
    solution = await solve_vrp_ortools(
        locations=locations,
        vehicles=vehicle_configs,
        max_solve_seconds=payload.max_solve_time_seconds,
        traffic_factor=1.3 if payload.consider_traffic else 1.0,
    )

    route_responses = []

    # 6. Save routes and stops via Supabase client
    for opt_route in solution.routes:
        if not opt_route.stop_ids:
            continue

        route_data = {
            "vehicle_id": opt_route.vehicle_id,
            "depot_id": str(depot["id"]),
            "status": "pending",
            "total_distance_km": opt_route.total_distance_km,
            "total_duration_minutes": opt_route.total_duration_minutes,
            "estimated_fuel_liters": opt_route.estimated_fuel_liters,
            "waypoints": [],
            "optimization_score": opt_route.efficiency_score or 0,
        }

        r_insert = db.table("routes").insert(route_data).execute()
        if not r_insert.data:
            continue
        
        new_route = r_insert.data[0]
        route_id = new_route["id"]

        # Batch insert stops
        stops_data = [
            {
                "route_id": route_id,
                "delivery_point_id": stop_id,
                "sequence": seq,
                "status": "pending"
            }
            for seq, stop_id in enumerate(opt_route.stop_ids)
        ]
        db.table("route_stops").insert(stops_data).execute()

        route_responses.append(
            RouteResponse(
                id=route_id,
                vehicle_id=new_route["vehicle_id"],
                status=new_route["status"],
                total_distance_km=new_route["total_distance_km"],
                total_duration_minutes=new_route["total_duration_minutes"],
                estimated_fuel_liters=new_route["estimated_fuel_liters"],
                optimization_score=new_route["optimization_score"],
                waypoints=new_route["waypoints"],
                stops=[],
                created_at=datetime.now(timezone.utc),
            )
        )

    return OptimizationResponse(
        job_id=str(uuid.uuid4()),
        status="completed",
        routes=route_responses,
        total_distance_km=solution.total_distance_km,
        total_fuel_liters=solution.total_fuel_liters,
        estimated_savings_pct=solution.savings_vs_naive_pct,
        solve_time_seconds=solution.solve_time_seconds,
        message=f"Optimized {len(route_responses)} routes",
    )


@router.post("/eta")
async def predict_eta(payload: dict, _: TokenData = Depends(get_current_user)):
    from app.ml.eta_model import eta_predictor
    return eta_predictor.predict(
        distance_km=payload.get("distance_km", 10),
        traffic_density=payload.get("traffic_density", 0.5),
        weather_severity=payload.get("weather_severity", 0.0),
        vehicle_type=payload.get("vehicle_type", "truck"),
    )