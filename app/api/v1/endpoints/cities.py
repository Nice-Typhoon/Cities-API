from fastapi import APIRouter, Depends,Query,status, Path
from typing import Annotated
from app.core.dependencies import get_city_service
from app.schemas.city import (
    CityCreate,
    CityResponse,
    CityWithDistanceResponse,
)
from app.services.city_service import CityService

router = APIRouter(prefix="/cities", tags=["cities"])


@router.get(
    "/nearest",
    response_model=list[CityWithDistanceResponse],
    summary="Find N nearest cities to a coordinate",
)
async def get_nearest_cities(
    latitude: float = Query(..., ge=-90.0, le=90.0, description="Query latitude"),
    longitude: float = Query(..., ge=-180.0, le=180.0, description="Query longitude"),
    limit: int = Query(2, ge=1, le=100, description="Number of results"),
    service: CityService = Depends(get_city_service),
) -> list[CityWithDistanceResponse]:
    results = await service.find_nearest(latitude, longitude, limit)
    return [
        CityWithDistanceResponse(
            id=r.id,
            name=r.name,
            latitude=r.latitude,
            longitude=r.longitude,
            distance_m=r.distance_m,
        )
        for r in results
    ]


@router.get("", response_model=list[CityResponse], summary="List all cities")
async def list_cities(
    offset: int = Query(0, ge=0, lt=2**63),
    limit: int = Query(100, ge=1, le=1000),
    service: CityService = Depends(get_city_service),
) -> list[CityResponse]:
    cities = await service.list_cities(offset=offset, limit=limit)
    return [CityResponse.model_validate(c) for c in cities]


@router.get("/{city_id}", response_model=CityResponse, summary="Get a city by ID")
async def get_city(
    city_id: Annotated[int, Path(gt=0, lt=2**63)],
    service: CityService = Depends(get_city_service),
) -> CityResponse:
    city = await service.get_city(city_id)
    return CityResponse.model_validate(city)


@router.post(
    "",
    response_model=CityResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a new city",
)
async def create_city(
    body: CityCreate,
    service: CityService = Depends(get_city_service),
) -> CityResponse:
    city = await service.add_city(body.name)
    return CityResponse.model_validate(city)


@router.delete("/{city_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a city")
async def delete_city(
    city_id: Annotated[int, Path(gt=0, lt=2**63)],
    service: CityService = Depends(get_city_service),
) -> None:
    await service.remove_city(city_id)
