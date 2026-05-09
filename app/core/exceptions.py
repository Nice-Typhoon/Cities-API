class AppError(Exception):
    """Базовая ошибка приложения"""


class CityNotFoundError(AppError):
    def __init__(self, identifier: str | int) -> None:
        self.identifier = identifier
        super().__init__(f"City not found: {identifier!r}")


class CityAlreadyExistsError(AppError):
    def __init__(self, name: str) -> None:
        self.name = name
        super().__init__(f"City already exists: {name!r}")


class GeocodingError(AppError):
    def __init__(self, city_name: str, reason: str) -> None:
        self.city_name = city_name
        self.reason = reason
        super().__init__(f"Failed to geocode {city_name!r}: {reason}")


class GeocodingNotFoundError(GeocodingError):
    def __init__(self, city_name: str) -> None:
        super().__init__(city_name, "no results from geocoding API")
