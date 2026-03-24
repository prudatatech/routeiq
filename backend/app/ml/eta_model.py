"""
ETA Prediction Model (Lightweight Physics-based for RouteIQ Free Tier).
Uses distance, traffic density, and weather to estimate arrival times.
"""
from __future__ import annotations

import logging
import math
from datetime import datetime, timezone
from typing import Optional

logger = logging.getLogger("routeiq.eta")


class ETAPredictor:
    """
    Lightweight ETA predictor for memory-constrained environments.
    Uses physics-based estimation with traffic and weather factors.
    """

    MODEL_VERSION = "1.0.0-physics-lean"

    def predict(
        self,
        distance_km: float,
        traffic_density: float = 0.5,
        weather_severity: float = 0.0,
        vehicle_type: str = "truck",
        historical_avg_speed_kmph: float = 45.0,
        timestamp: Optional[datetime] = None,
    ) -> dict:
        """
        Returns predicted ETA estimate using base physics.
        """
        ts = timestamp or datetime.now(timezone.utc)
        hour = ts.hour

        predicted_minutes = self._physics_estimate(
            distance_km, traffic_density, weather_severity,
            hour, historical_avg_speed_kmph,
        )

        # Uncertainty: widen CI with traffic and weather
        uncertainty = max(2.0, predicted_minutes * 0.1 * (1 + traffic_density + weather_severity))

        return {
            "estimated_minutes": round(predicted_minutes, 1),
            "confidence_interval_low": round(max(1.0, predicted_minutes - uncertainty), 1),
            "confidence_interval_high": round(predicted_minutes + uncertainty, 1),
            "model_version": self.MODEL_VERSION,
            "impacts": {
                "traffic": "moderate" if traffic_density > 0.4 else "low",
                "weather": "moderate" if weather_severity > 0.4 else "low"
            }
        }

    def _physics_estimate(
        self,
        distance_km: float,
        traffic_density: float,
        weather_severity: float,
        hour: int,
        base_speed: float,
    ) -> float:
        """Physics-based estimate: adjust speed by traffic, weather, time-of-day."""
        # Speed reduction factors
        traffic_factor = 1 - (traffic_density * 0.6)       # up to 60% speed reduction
        weather_factor = 1 - (weather_severity * 0.3)      # up to 30%
        peak_factor = 0.75 if hour in range(8, 11) or hour in range(17, 21) else 1.0

        effective_speed = base_speed * traffic_factor * weather_factor * peak_factor
        effective_speed = max(5.0, effective_speed)  # minimum 5 km/h

        return (distance_km / effective_speed) * 60


# Singleton
eta_predictor = ETAPredictor()
