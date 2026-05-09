"""
GeoRepository: ищем ближайшие города с PostGIS.
  1. в postgis оператор <-> - это KNN - k nearest neighbors. его нет в sqlalchemy, соответственно от orm толка нет
  2. обходя orm и работая напрямую с asyncpg можно ускорить данный процесс до 2х раз

в запросе используется ST_MakePoint + GEOGRAPHY соответсвенно расстояние измеряется в метрах,
А не градусах - при использовании типа данных GEOGRAPHY вычисления идут по дуге земли, а не по плоскости
как было бы в GEOMETRY так как сфера у нас же планета.
Пространственный индекс (GIST по полю location) используется оператором <-> автоматически
"""


from dataclasses import dataclass
import asyncpg


@dataclass(slots=True)
class NearestCity:
    id: int
    name: str
    latitude: float
    longitude: float
    distance_m: float


_NEAREST_SQL = """
SELECT
    id,
    name,
    latitude::float8,
    longitude::float8,
    ST_Distance(
        ST_MakePoint(longitude::float8, latitude::float8)::geography,
        ST_MakePoint($2, $1)::geography
    ) AS distance_m
FROM cities
ORDER BY
    ST_MakePoint(longitude::float8, latitude::float8)::geography
    <->
    ST_MakePoint($2, $1)::geography
LIMIT $3;
"""
#$1 = query_latitude, $2 = query_longitude, $3 = limit
#ST_MakePoint принимает долготу, а потом широту (lon, lat), а не как обычно принято


class GeoRepository:
    def __init__(self, pool: asyncpg.Pool) -> None:
        self._pool = pool

    async def find_nearest(
        self,
        latitude: float,
        longitude: float,
        limit: int = 2,
    ) -> list[NearestCity]:
        """Возвращаем *limit* ближайших городов, отсортированных по дистанции в метрах"""
        async with self._pool.acquire() as conn:
            rows = await conn.fetch(_NEAREST_SQL, latitude, longitude, limit)

        return [
            NearestCity(
                id=row["id"],
                name=row["name"],
                latitude=row["latitude"],
                longitude=row["longitude"],
                distance_m=row["distance_m"],
            )
            for row in rows
        ]
