from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field


# Request схемы

class CityCreate(BaseModel):
    """В теле только название гороад"""

    name: str = Field(..., min_length=1, max_length=255, examples=["Helsinki"])


# Response схемы

class CityResponse(BaseModel):
    id: int
    name: str
    latitude: Decimal
    longitude: Decimal
    created_at: datetime
    osm_id: int
    osm_type: str

    model_config = ConfigDict(from_attributes=True)



class CityWithDistanceResponse(BaseModel):
    """Город + расстояние в метрах от точки запрса"""

    id: int
    name: str
    latitude: float
    longitude: float
    distance_m: float = Field(..., description="Distance in metres (geodesic via PostGIS)")
