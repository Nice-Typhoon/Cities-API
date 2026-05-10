import pytest
from unittest.mock import AsyncMock

from app.core.exceptions import CityAlreadyExistsError, CityNotFoundError, GeocodingNotFoundError
from app.models.city import City
from app.repositories.geo_repository import NearestCity
from app.services.city_service import CityService
from app.services.geocoding import Coordinates


def _make_service(
    cities: list[City] | None = None,
    nearest: list[NearestCity] | None = None,
    geocode_result: Coordinates | None = None,
    geocode_raises: Exception | None = None,
) -> CityService:
    city_repo = AsyncMock()
    geo_repo = AsyncMock()
    geocoding = AsyncMock()

    city_repo.list_all.return_value = cities or []
    city_repo.get_by_id.return_value = (cities or [City(id=1, name="X", latitude=0, longitude=0)])[0]
    city_repo.get_by_name.return_value = None
    city_repo.create.return_value = City(id=99, name="Test", latitude=1.0, longitude=2.0)
    geo_repo.find_nearest.return_value = nearest or []

    if geocode_raises:
        geocoding.geocode.side_effect = geocode_raises
    else:
        geocoding.geocode.return_value = geocode_result or Coordinates(1.0, 2.0)

    return CityService(city_repo, geo_repo, geocoding)


@pytest.mark.asyncio
async def test_list_cities_returns_all():
    cities = [
        City(id=1, name="Helsinki", latitude=60.1, longitude=24.9),
        City(id=2, name="Tampere", latitude=61.5, longitude=23.8),
    ]
    service = _make_service(cities=cities)
    result = await service.list_cities()
    assert len(result) == 2
    assert result[0].name == "Helsinki"


@pytest.mark.asyncio
async def test_add_city_geocodes_and_persists():
    service = _make_service(geocode_result=Coordinates(60.17, 24.94))
    city = await service.add_city("Helsinki")
    service._geocoding.geocode.assert_awaited_once_with("Helsinki")
    service._city_repo.create.assert_awaited_once_with(
        name="Helsinki", latitude=60.17, longitude=24.94
    )
    assert city.id == 99


@pytest.mark.asyncio
async def test_add_city_propagates_geocoding_error():
    service = _make_service(geocode_raises=GeocodingNotFoundError("Unknown"))
    with pytest.raises(GeocodingNotFoundError):
        await service.add_city("Unknown")


@pytest.mark.asyncio
async def test_add_city_propagates_duplicate_error():
    service = _make_service()
    service._city_repo.create.side_effect = CityAlreadyExistsError("Helsinki")
    with pytest.raises(CityAlreadyExistsError):
        await service.add_city("Helsinki")


@pytest.mark.asyncio
async def test_remove_city_calls_repo():
    service = _make_service()
    await service.remove_city(1)
    service._city_repo.delete_by_id.assert_awaited_once_with(1)


@pytest.mark.asyncio
async def test_remove_city_not_found_raises():
    service = _make_service()
    service._city_repo.delete_by_id.side_effect = CityNotFoundError(999)
    with pytest.raises(CityNotFoundError):
        await service.remove_city(999)


@pytest.mark.asyncio
async def test_find_nearest_delegates_to_geo_repo():
    nearest = [
        NearestCity(id=1, name="A", latitude=1.0, longitude=2.0, distance_m=100.0),
        NearestCity(id=2, name="B", latitude=3.0, longitude=4.0, distance_m=200.0),
    ]
    service = _make_service(nearest=nearest)
    result = await service.find_nearest(60.0, 25.0, limit=2)
    assert len(result) == 2
    assert result[0].distance_m == 100.0
    assert result[1].name == "B"
    service._geo_repo.find_nearest.assert_awaited_once_with(60.0, 25.0, 2)
