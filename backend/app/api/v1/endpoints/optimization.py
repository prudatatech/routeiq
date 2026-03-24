"""Route optimization endpoints using VRP solver."""

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user, require_role
from app.ml.vrp_solver import Location, VehicleConfig, solve_vrp_ortools
from app.models.models import DeliveryPoint, Depot, Route, RouteStop, Vehicle
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
    db: AsyncSession = Depends(get_db),
    token: TokenData = Depends(require_role("admin", "manager")),
):
    """
    1️⃣ Load depot, vehicles, delivery points
    2️⃣ Run OR-Tools VRP solver
    3️⃣ Save optimized routes
    4️⃣ Return optimized plan
    """

    # -----------------------------
    # Load depot
    # -----------------------------
    if payload.depot_id and str(payload.depot_id) != '00000000-0000-0000-0000-000000000001':
        depot_result = await db.execute(select(Depot).where(Depot.id == payload.depot_id))
    else:
        depot_result = await db.execute(select(Depot).limit(1))
    depot = depot_result.scalar_one_or_none()
    if not depot:
        raise HTTPException(status_code=404, detail="Depot not found")

    # -----------------------------
    # Load vehicles
    # -----------------------------
    if payload.vehicle_ids:
        v_result = await db.execute(select(Vehicle).where(Vehicle.id.in_(payload.vehicle_ids)))
    else:
        v_result = await db.execute(select(Vehicle).where(Vehicle.status.in_(["available", "idle"])).limit(5))
    vehicles = v_result.scalars().all()
    if not vehicles:
        raise HTTPException(status_code=404, detail="No available vehicles found")

    # -----------------------------
    # Load delivery points
    # -----------------------------
    if payload.delivery_point_ids:
        dp_result = await db.execute(select(DeliveryPoint).where(DeliveryPoint.id.in_(payload.delivery_point_ids)))
    else:
        dp_result = await db.execute(select(DeliveryPoint).where(DeliveryPoint.status == "pending").limit(20))
    delivery_points = dp_result.scalars().all()
    if not delivery_points:
        raise HTTPException(status_code=404, detail="No pending delivery points found")

    # -----------------------------
    # Build solver input
    # -----------------------------
    depot_loc = Location(
        id=str(depot.id),
        lat=depot.latitude,
        lng=depot.longitude,
    )

    locations = [depot_loc]

    for dp in delivery_points:
        locations.append(
            Location(
                id=str(dp.id),
                lat=dp.latitude,
                lng=dp.longitude,
                demand_kg=dp.demand_kg,
                time_window_start=getattr(dp, "time_window_start", 0) or 0,
                time_window_end=getattr(dp, "time_window_end", 1440) or 1440,
                service_time=dp.service_time_minutes,
            )
        )

    vehicle_configs = [
        VehicleConfig(
            id=str(v.id),
            capacity_kg=v.capacity_kg,
            start_location=depot_loc,
        )
        for v in vehicles
    ]

    # -----------------------------
    # Run VRP solver (Now async)
    # -----------------------------
    solution = await solve_vrp_ortools(
        locations=locations,
        vehicles=vehicle_configs,
        max_solve_seconds=payload.max_solve_time_seconds,
        traffic_factor=1.3 if payload.consider_traffic else 1.0,
    )

    route_responses = []

    # -----------------------------
    # Save routes to DB
    # -----------------------------
    for opt_route in solution.routes:
        if not opt_route.stop_ids:
            continue

        route = Route(
            vehicle_id=uuid.UUID(opt_route.vehicle_id),
            depot_id=depot.id,
            status="pending",
            total_distance_km=opt_route.total_distance_km,
            total_duration_minutes=opt_route.total_duration_minutes,
            estimated_fuel_liters=opt_route.estimated_fuel_liters,

            # ✅ REQUIRED FIELDS FOR DB
            waypoints=[],   # prevents NOT NULL error
            optimization_score=opt_route.efficiency_score or 0,
        )

        db.add(route)
        await db.flush()   # ensures route.id is available

        # Save stops
        for seq, stop_id in enumerate(opt_route.stop_ids):
            stop = RouteStop(
                route_id=route.id,
                delivery_point_id=uuid.UUID(stop_id),
                sequence=seq,
                status="pending"
            )
            db.add(stop)

        # Build API response
        route_responses.append(
            RouteResponse(
                id=route.id,
                vehicle_id=route.vehicle_id,
                status=route.status,
                total_distance_km=route.total_distance_km,
                total_duration_minutes=route.total_duration_minutes,
                estimated_fuel_liters=route.estimated_fuel_liters,
                optimization_score=route.optimization_score,
                waypoints=route.waypoints,
                stops=[],
                created_at=datetime.now(timezone.utc),
            )
        )

    # -----------------------------
    # Return response
    # -----------------------------
    return OptimizationResponse(
        job_id=str(uuid.uuid4()),
        status="completed",
        routes=route_responses,
        total_distance_km=solution.total_distance_km,
        total_fuel_liters=solution.total_fuel_liters,
        estimated_savings_pct=solution.savings_vs_naive_pct,
        solve_time_seconds=solution.solve_time_seconds,
        message=f"Optimized {len(route_responses)} routes in {solution.solve_time_seconds:.2f}s",
    )


# ------------------------------------------------------------------
# ETA prediction endpoint
# ------------------------------------------------------------------
@router.post("/eta")
async def predict_eta(
    payload: dict,
    _: TokenData = Depends(get_current_user),
):
    """Quick ETA prediction."""
    from app.ml.eta_model import eta_predictor

    return eta_predictor.predict(
        distance_km=payload.get("distance_km", 10),
        traffic_density=payload.get("traffic_density", 0.5),
        weather_severity=payload.get("weather_severity", 0.0),
        vehicle_type=payload.get("vehicle_type", "truck"),
    )