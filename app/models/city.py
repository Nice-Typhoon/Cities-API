from datetime import datetime
from sqlalchemy import DateTime, Index, Numeric, String, func, BigInteger
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class City(Base):
    """храним город и его WGS-84 координаты"""

    __tablename__ = "cities"

    id: Mapped[int] = mapped_column(BigInteger(), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)

    #хранит как NUMERIC, но и FLOAT тоже пойдет
    latitude: Mapped[float] = mapped_column(Numeric(9, 6), nullable=False)
    longitude: Mapped[float] = mapped_column(Numeric(9, 6), nullable=False)
    osm_id: Mapped[int] = mapped_column(BigInteger(), nullable=False)
    osm_type: Mapped[str] = mapped_column(String(), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    #Пространственный индекс PostGIS будет создан в миграции (migrations/)
    #Дефолтный индекс b-tree
    __table_args__ = (
        Index("ix_cities_name_lower", func.lower(name)),
        Index("ix_cities_osm_id_type", osm_id, osm_type),
    )

    def __repr__(self) -> str:
        return f"<City id={self.id} name={self.name!r}>"
