"""Pydantic schemas for request/response validation."""
from __future__ import annotations
import uuid
from datetime import datetime
from typing import Any, List, Optional
from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------
class TokenData(BaseModel):
    user_id: str
    role: str = "driver"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    role: str


class RefreshRequest(BaseModel):
    refresh_token: str


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------
class UserCreate(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=2, max_length=255)
    password: str = Field(min_length=8)
    role: str = Field(default="driver", pattern="^(superadmin|admin|manager|driver)$")


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    email: str
    full_name: str
    role: str
    is_active: bool
    created_at: datetime


# ---------------------------------------------------------------------------
# Vehicles
# ---------------------------------------------------------------------------
class VehicleCreate(BaseModel):
    plate_number: str = Field(min_length=4, max_length=20)
    vehicle_type: str = Field(pattern="^(truck|van|bike|car)$")
    capacity_kg: float = Field(gt=0, le=50000)
    fuel_type: str = "diesel"
    fuel_capacity_liters: float = Field(gt=0, le=1000, default=60.0)
    fuel_efficiency_kmpl: float = Field(gt=0, le=100, default=12.0)


class VehicleUpdate(BaseModel):
    status: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    driver_id: Optional[uuid.UUID] = None


class VehicleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    plate_number: str
    vehicle_type: str
    capacity_kg: float
    status: str
    fuel_type: Optional[str] = None
    fuel_capacity_liters: Optional[float] = None
    fuel_efficiency_kmpl: Optional[float] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    driver_id: Optional[uuid.UUID] = None
    created_at: datetime


# ---------------------------------------------------------------------------
# Route Optimization
# ---------------------------------------------------------------------------
class OptimizationRequest(BaseModel):
    depot_id: uuid.UUID
    vehicle_ids: List[uuid.UUID] = Field(min_length=1, max_length=100)
    delivery_point_ids: List[uuid.UUID] = Field(min_length=1, max_length=500)
    algorithm: str = Field(default="ortools", pattern="^(ortools|genetic|reinforcement)$")
    consider_traffic: bool = True
    consider_weather: bool = True
    max_solve_time_seconds: int = Field(default=30, ge=5, le=300)


class RouteStopSchema(BaseModel):
    delivery_point_id: uuid.UUID
    sequence: int
    estimated_arrival: Optional[datetime] = None
    latitude: float
    longitude: float
    address: str


class RouteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    vehicle_id: uuid.UUID
    status: str
    total_distance_km: float
    total_duration_minutes: float
    estimated_fuel_liters: float
    optimization_score: Optional[float] = None
    waypoints: List[Any]
    stops: List[RouteStopSchema] = []
    created_at: datetime


class OptimizationResponse(BaseModel):
    job_id: str
    status: str = "queued"
    routes: List[RouteResponse] = []
    total_distance_km: float = 0
    total_fuel_liters: float = 0
    estimated_savings_pct: float = 0
    solve_time_seconds: Optional[float] = None
    message: str = ""


# ---------------------------------------------------------------------------
# ETA Prediction
# ---------------------------------------------------------------------------
class ETARequest(BaseModel):
    vehicle_id: uuid.UUID
    origin_lat: float = Field(ge=-90, le=90)
    origin_lng: float = Field(ge=-180, le=180)
    destination_lat: float = Field(ge=-90, le=90)
    destination_lng: float = Field(ge=-180, le=180)
    distance_km: float = Field(gt=0)
    current_traffic_density: float = Field(ge=0, le=1, default=0.5)


class ETAResponse(BaseModel):
    vehicle_id: uuid.UUID
    estimated_minutes: float
    confidence_interval_low: float
    confidence_interval_high: float
    traffic_impact_minutes: float
    weather_impact_minutes: float
    model_version: str


# ---------------------------------------------------------------------------
# Telemetry
# ---------------------------------------------------------------------------
class TelemetryCreate(BaseModel):
    vehicle_id: uuid.UUID
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    speed_kmph: float = Field(ge=0, le=300)
    heading: float = Field(ge=0, le=360)
    fuel_level_pct: float = Field(ge=0, le=100)
    engine_temp: Optional[float] = None
    odometer_km: Optional[float] = None


class TelemetryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    vehicle_id: uuid.UUID
    timestamp: datetime
    latitude: float
    longitude: float
    speed_kmph: float
    fuel_level_pct: float


# ---------------------------------------------------------------------------
# Dashboard / Analytics
# ---------------------------------------------------------------------------
class KPIResponse(BaseModel):
    active_vehicles: int
    on_time_rate_pct: float
    fuel_cost_today: float
    fuel_saved_pct: float
    total_deliveries_today: int
    avg_eta_accuracy_pct: float
    rerouting_events_today: int


class FleetSummary(BaseModel):
    total: int
    active: int
    idle: int
    maintenance: int
    offline: int


# ---------------------------------------------------------------------------
# Pagination
# ---------------------------------------------------------------------------
class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    size: int
    pages: int
