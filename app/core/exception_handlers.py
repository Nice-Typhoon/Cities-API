from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.exceptions import (
    CityAlreadyExistsError,
    CityNotFoundError,
    GeocodingNotFoundError,
    GeocodingError,
)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(CityNotFoundError)
    async def city_not_found(request: Request, exc: CityNotFoundError) -> JSONResponse:
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    @app.exception_handler(CityAlreadyExistsError)
    async def city_exists(request: Request, exc: CityAlreadyExistsError) -> JSONResponse:
        return JSONResponse(status_code=409, content={"detail": str(exc)})

    @app.exception_handler(GeocodingNotFoundError)
    async def geocoding_not_found(
        request: Request, exc: GeocodingNotFoundError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={"detail": f"City name not found in geocoding service: {exc.city_name!r}"},
        )

    @app.exception_handler(GeocodingError)
    async def geocoding_error(request: Request, exc: GeocodingError) -> JSONResponse:
        return JSONResponse(
            status_code=502,
            content={"detail": f"Geocoding service error: {exc.reason}"},
        )
