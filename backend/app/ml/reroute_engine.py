"""
Dynamic Re-Optimization Engine
Monitors active routes and triggers re-routing when delay thresholds are exceeded.
"""
from __future__ import annotations

import asyncio
import logging
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import List, Optional

from app.core.redis import cache_get, cache_set
from app.ml.vrp_solver import Location, VehicleConfig, solve_vrp_ortools

logger = logging.getLogger("routeiq.reroute")

REROUTE_DELAY_THRESHOLD_MINUTES = 10   # reroute if delay > 10 min
REROUTE_COOLDOWN_SECONDS = 300          # don't reroute same vehicle for 5 min


@dataclass
class TrafficEvent:
    event_id: str
    lat: float
    lng: float
    radius_km: float
    severity: float          # 0-1
    event_type: str          # "jam", "accident", "closure", "weather"
    started_at: datetime


@dataclass
class RerouteDecision:
    vehicle_id: str
    trigger: str
    old_eta_minutes: float
    new_eta_minutes: float
    saved_minutes: float
    new_stop_sequence: List[str]
    rerouted_at: datetime


class DynamicRerouteEngine:
    """
    Listens for traffic/weather events and decides whether to reroute active vehicles.
    In production this runs as a Celery periodic task or a background asyncio task.
    """

    def __init__(self):
        self._active_events: List[TrafficEvent] = []

    async def process_traffic_event(self, event: TrafficEvent) -> List[RerouteDecision]:
        """Called when a new traffic event is received (webhook / polling)."""
        self._active_events.append(event)
        decisions = []

        # In production: query DB for vehicles on routes near event radius
        # Here we illustrate the decision logic
        affected_routes = await self._find_affected_routes(event)

        for route_id, vehicle_id, remaining_stops, current_eta in affected_routes:
            if await self._is_on_cooldown(vehicle_id):
                logger.debug(f"Vehicle {vehicle_id} on cooldown, skipping")
                continue

            decision = await self._reroute_vehicle(
                vehicle_id=vehicle_id,
                route_id=route_id,
                remaining_stops=remaining_stops,
                current_eta=current_eta,
                event=event,
            )

            if decision:
                decisions.append(decision)
                await self._set_cooldown(vehicle_id)

        return decisions

    async def _find_affected_routes(self, event: TrafficEvent):
        """
        Returns list of (route_id, vehicle_id, remaining_stops, eta_minutes)
        for routes that pass within event.radius_km of the event location.
        Stub — replace with DB query using PostGIS or Haversine filter.
        """
        return []  # Populated from DB in production

    async def _reroute_vehicle(
        self,
        vehicle_id: str,
        route_id: str,
        remaining_stops: List[Location],
        current_eta: float,
        event: TrafficEvent,
    ) -> Optional[RerouteDecision]:
        """Re-solve VRP for remaining stops, avoiding congested area."""
        if not remaining_stops:
            return None

        traffic_multiplier = 1 + event.severity * 0.8  # up to 80% slowdown

        solution = solve_vrp_ortools(
            locations=remaining_stops,
            vehicles=[VehicleConfig(id=vehicle_id, capacity_kg=9999, start_location=remaining_stops[0])],
            max_solve_seconds=10,
            traffic_factor=traffic_multiplier,
        )

        if not solution.routes:
            return None

        new_route = solution.routes[0]
        new_eta = new_route.total_duration_minutes

        if current_eta - new_eta < REROUTE_DELAY_THRESHOLD_MINUTES:
            logger.debug(f"Reroute for {vehicle_id} saves only {current_eta - new_eta:.1f} min, skipping")
            return None

        logger.info(
            f"Rerouting vehicle {vehicle_id}: "
            f"old_eta={current_eta:.1f}min new_eta={new_eta:.1f}min "
            f"saved={current_eta - new_eta:.1f}min"
        )

        return RerouteDecision(
            vehicle_id=vehicle_id,
            trigger=f"{event.event_type} at ({event.lat:.4f},{event.lng:.4f})",
            old_eta_minutes=current_eta,
            new_eta_minutes=new_eta,
            saved_minutes=round(current_eta - new_eta, 1),
            new_stop_sequence=new_route.stop_ids,
            rerouted_at=datetime.now(timezone.utc),
        )

    async def _is_on_cooldown(self, vehicle_id: str) -> bool:
        key = f"reroute_cooldown:{vehicle_id}"
        return await cache_get(key) is not None

    async def _set_cooldown(self, vehicle_id: str) -> None:
        key = f"reroute_cooldown:{vehicle_id}"
        await cache_set(key, "1", ttl=REROUTE_COOLDOWN_SECONDS)


# Singleton
reroute_engine = DynamicRerouteEngine()
