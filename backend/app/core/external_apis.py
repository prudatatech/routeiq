import httpx
import logging
from typing import List, Dict, Tuple, Optional
from app.core.config import settings

logger = logging.getLogger("routeiq.apis")

class GoogleMapsService:
    def __init__(self, api_key: str = settings.GOOGLE_MAPS_API_KEY):
        self.api_key = api_key
        self.base_url = "https://maps.googleapis.com/maps/api"

    async def get_distance_matrix(self, origins: List[Tuple[float, float]], destinations: List[Tuple[float, float]]) -> Optional[Dict]:
        """Fetch distance and duration matrix from Google Maps."""
        if not self.api_key:
            return None

        origins_str = "|".join([f"{lat},{lng}" for lat, lng in origins])
        destinations_str = "|".join([f"{lat},{lng}" for lat, lng in destinations])

        params = {
            "origins": origins_str,
            "destinations": destinations_str,
            "key": self.api_key,
            "mode": "driving",
            "traffic_model": "best_guess",
            "departure_time": "now"
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{self.base_url}/distancematrix/json", params=params)
                response.raise_for_status()
                return response.json()
            except Exception as e:
                logger.error(f"Error fetching Google Distance Matrix: {e}")
                return None

    async def geocode(self, address: str) -> Optional[Dict]:
        """Convert address to lat/lng."""
        if not self.api_key:
            return None

        params = {
            "address": address,
            "key": self.api_key
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{self.base_url}/geocode/json", params=params)
                response.raise_for_status()
                data = response.json()
                if data["status"] == "OK":
                    return data["results"][0]["geometry"]["location"]
                return None
            except Exception as e:
                logger.error(f"Error geocoding address: {e}")
                return None

maps_service = GoogleMapsService()
