"""SQLAlchemy ORM models."""
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean, DateTime, Enum, Float, ForeignKey,
    Integer, String, Text, JSON, func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


def uuid_pk():
    return mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )


# ================= USERS =================
class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = uuid_pk()
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(255))
    hashed_password: Mapped[str] = mapped_column(String(255))

    role: Mapped[str] = mapped_column(
        Enum("superadmin", "admin", "manager", "driver", name="user_role"),
        default="driver",
    )

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    vehicles = relationship("Vehicle", back_populates="driver")


# ================= VEHICLES =================
class Vehicle(Base, TimestampMixin):
    __tablename__ = "vehicles"

    id: Mapped[uuid.UUID] = uuid_pk()
    plate_number: Mapped[str] = mapped_column(String(20), unique=True)

    vehicle_type: Mapped[str] = mapped_column(
        Enum("truck", "van", "bike", "car", name="vehicle_type"),
        default="truck",
    )

    capacity_kg: Mapped[float] = mapped_column(Float, default=1000)
    fuel_type: Mapped[str] = mapped_column(String(20), default="diesel")
    fuel_capacity_liters: Mapped[float] = mapped_column(Float, default=60.0)
    fuel_efficiency_kmpl: Mapped[float] = mapped_column(Float, default=12.0)

    status: Mapped[str] = mapped_column(
        Enum("available", "on_route", "idle", "maintenance", "offline", name="vehicle_status"),
        default="available",
    )

    driver_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("users.id"))

    driver = relationship("User", back_populates="vehicles")
    routes = relationship("Route", back_populates="vehicle")
    telemetry = relationship("Telemetry", back_populates="vehicle")


# ================= DEPOTS =================
class Depot(Base, TimestampMixin):
    __tablename__ = "depots"

    id: Mapped[uuid.UUID] = uuid_pk()
    name: Mapped[str] = mapped_column(String(255))
    address: Mapped[str] = mapped_column(Text)
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)


# ================= DELIVERY POINTS =================
class DeliveryPoint(Base, TimestampMixin):
    __tablename__ = "delivery_points"

    id: Mapped[uuid.UUID] = uuid_pk()
    name: Mapped[str] = mapped_column(String(255))
    address: Mapped[str] = mapped_column(Text)
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)

    demand_kg: Mapped[float] = mapped_column(Float, default=0.0)
    service_time_minutes: Mapped[int] = mapped_column(Integer, default=10)


# ================= ROUTES =================
class Route(Base, TimestampMixin):
    __tablename__ = "routes"

    id: Mapped[uuid.UUID] = uuid_pk()
    vehicle_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("vehicles.id"))
    depot_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("depots.id"))

    status: Mapped[str] = mapped_column(
        Enum("pending", "optimizing", "active", "completed", "cancelled", name="route_status"),
        default="pending",
    )

    total_distance_km: Mapped[float] = mapped_column(Float, default=0.0)
    total_duration_minutes: Mapped[float] = mapped_column(Float, default=0.0)
    estimated_fuel_liters: Mapped[float] = mapped_column(Float, default=0.0)

    # ✅ REQUIRED BY DB
    waypoints: Mapped[list] = mapped_column(JSON, default=list)
    optimization_score: Mapped[float] = mapped_column(Float, default=0.0)

    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    vehicle = relationship("Vehicle", back_populates="routes")
    stops = relationship("RouteStop", back_populates="route")


class RouteStop(Base, TimestampMixin):
    __tablename__ = "route_stops"

    id: Mapped[uuid.UUID] = uuid_pk()
    route_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("routes.id"))
    delivery_point_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("delivery_points.id"))
    sequence: Mapped[int] = mapped_column(Integer)

    route = relationship("Route", back_populates="stops")


# ================= TELEMETRY =================
class Telemetry(Base):
    __tablename__ = "telemetry"

    id: Mapped[uuid.UUID] = uuid_pk()
    vehicle_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("vehicles.id"))
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)

    vehicle = relationship("Vehicle", back_populates="telemetry")