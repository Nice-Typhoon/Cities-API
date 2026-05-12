from dataclasses import dataclass
from typing import Protocol

import httpx
from app.core.config import Settings
from app.core.exceptions import GeocodingError, GeocodingNotFoundError


@dataclass(frozen=True, slots=True)
class Coordinates:
    latitude: float
    longitude: float


class GeocodingService(Protocol):
    async def geocode(self, city_name: str) -> tuple[Coordinates, dict]:
        """Return coordinates for *city_name* or raise GeocodingError."""
        ...


class NominatimGeocodingService:
    """
    бесплатный геокодер от  OpenStreetMap - Nominatim:

    https://nominatim.org/release-docs/latest/api/Search/

    Nominatim требует user agent с описанием, наприммер своего проекта
    """

    def __init__(self, client: httpx.AsyncClient, settings: Settings) -> None:
        self._client = client
        self._settings = settings

    async def geocode(self, city_name: str) -> tuple[Coordinates, dict]:
        try:
            response = await self._client.get(
                f"{self._settings.geocoding_base_url}/search",
                params={
                    "q": city_name,
                    "format": "json",
                    "limit": 1,
                    "featuretype": "city",
                },
                headers={"User-Agent": self._settings.geocoding_user_agent},
                timeout=self._settings.geocoding_timeout,
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise GeocodingError(city_name, f"HTTP {exc.response.status_code}") from exc
        except httpx.RequestError as exc:
            raise GeocodingError(city_name, str(exc)) from exc

        results: list[dict] = response.json()
        if not results:
            raise GeocodingNotFoundError(city_name)

        first = results[0]
        return Coordinates(
            latitude=float(first["lat"]),
            longitude=float(first["lon"]),
        ), {'osm_id': first['osm_id'], 'osm_type': first['osm_type'], 'name': first['name']}
