from app.core.exceptions import CityAlreadyExistsError, CityNotFoundError
from app.models.city import City
from app.repositories.city_repository import CityRepository
from app.repositories.geo_repository import GeoRepository, NearestCity
from app.services.geocoding import GeocodingService


class CityService:
    def __init__(
        self,
        city_repo: CityRepository,
        geo_repo: GeoRepository,
        geocoding: GeocodingService,
    ) -> None:
        self._city_repo = city_repo
        self._geo_repo = geo_repo
        self._geocoding = geocoding


    async def get_city(self, city_id: int) -> City:
        return await self._city_repo.get_by_id(city_id)


    async def list_cities(self, offset: int = 0, limit: int = 100) -> list[City]:
        return await self._city_repo.list_all(offset=offset, limit=limit)


    async def find_nearest(
        self,
        latitude: float,
        longitude: float,
        limit: int = 2,
    ) -> list[NearestCity]:
        return await self._geo_repo.find_nearest(latitude, longitude, limit)


    async def add_city(self, name: str) -> City:
        """
        геокодируется через api openstreetmap и потом сохранятеся в бд

        Raises:
            CityAlreadyExistsError: если город с таким именм уже существует
            GeocodingError: если внешний api не работает
            GeocodingNotFoundError: если по названию ничего не было найдено
        """
        is_exists = await self._city_repo.if_exists(name)
        if is_exists:
            raise CityAlreadyExistsError(name)

        coordinates = await self._geocoding.geocode(name)
        return await self._city_repo.create(
            name=name,
            latitude=coordinates.latitude,
            longitude=coordinates.longitude,
        )


    async def remove_city(self, city_id: int) -> None:
        """поднимется CityNotFoundError если города не будет"""

        await self._city_repo.delete_by_id(city_id)
