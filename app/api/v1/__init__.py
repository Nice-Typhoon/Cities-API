from fastapi import APIRouter

from app.api.v1.endpoints.cities import router as cities_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(cities_router)
