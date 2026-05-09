"""
CityRepository: все crud операции для orm

для геокодинга отдельный репозиторий, так как он будет обходить orm и работать напрямую с asyncpg для бОльшей скоротси
"""

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import CityAlreadyExistsError, CityNotFoundError
from app.models.city import City


class CityRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session


    async def get_by_id(self, city_id: int) -> City:
        city = await self._session.get(City, city_id)
        if city is None:
            raise CityNotFoundError(city_id)
        return city


    async def get_by_name(self, name: str) -> City | None:
        result = await self._session.execute(
            select(City).where(City.name.ilike(name))
        )
        return result.scalar_one_or_none()


    async def list_all(self, offset: int = 0, limit: int = 100) -> list[City]:
        result = await self._session.execute(
            select(City).order_by(City.name).offset(offset).limit(limit)
        )
        return list(result.scalars().all())


    async def create(
        self,
        name: str,
        latitude: float,
        longitude: float,
    ) -> City:
        existing = await self.get_by_name(name)
        if existing is not None:
            raise CityAlreadyExistsError(name)

        city = City(name=name, latitude=latitude, longitude=longitude)
        self._session.add(city)
        await self._session.flush()
        return city


    async def delete_by_id(self, city_id: int) -> None:
        result = await self._session.execute(
            delete(City).where(City.id == city_id)
        )
        if result.rowcount == 0:
            raise CityNotFoundError(city_id)
