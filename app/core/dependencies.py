from collections.abc import AsyncGenerator
from dataclasses import dataclass

import asyncpg
import httpx
from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.config import Settings, get_settings
from app.repositories.city_repository import CityRepository
from app.repositories.geo_repository import GeoRepository
from app.services.city_service import CityService
from app.services.geocoding import NominatimGeocodingService


@dataclass
class AppState:
    session_factory: async_sessionmaker[AsyncSession]
    asyncpg_pool: asyncpg.Pool
    http_client: httpx.AsyncClient
    settings: Settings


def get_app_state(request: Request) -> AppState:
    return request.app.state.app_state  # type: ignore[return-value]


async def get_db_session(
    state: AppState = Depends(get_app_state),
) -> AsyncGenerator[AsyncSession, None]:
    async with state.session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


#Зависимости репозиториев

def get_city_repository(
    session: AsyncSession = Depends(get_db_session),
) -> CityRepository:
    return CityRepository(session)


def get_geo_repository(
    state: AppState = Depends(get_app_state),
) -> GeoRepository:
    return GeoRepository(state.asyncpg_pool)


def get_geocoding_service(
    state: AppState = Depends(get_app_state),
) -> NominatimGeocodingService:
    return NominatimGeocodingService(state.http_client, state.settings)


#сервисные зависимости

def get_city_service(
    city_repo: CityRepository = Depends(get_city_repository),
    geo_repo: GeoRepository = Depends(get_geo_repository),
    geocoding: NominatimGeocodingService = Depends(get_geocoding_service),
) -> CityService:
    return CityService(city_repo, geo_repo, geocoding)
