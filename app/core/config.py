from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    #БД
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "cities_db"
    db_user: str = "postgres"
    db_password: str = "postgres"
    db_pool_size: int = 20
    db_max_overflow: int = 10
    db_pool_timeout: int = 30

    #Внешний API для геокодинга- Nominatim от OpenStreetMap.
    # он бесплатный и не нужен ключ, надо только указывать user agent, делать таймауты
    # и не запрашивать повторно одни и теже города
    geocoding_base_url: str = "https://nominatim.openstreetmap.org"
    geocoding_timeout: float = 10.0
    geocoding_user_agent: str = "CitiesAPI/1.0"

    # App
    app_title: str = "Cities API"
    app_version: str = "1.0.0"
    debug: bool = False

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    @property
    def database_url_raw(self) -> str:
        """Сырой asyncpg DSN для прямого использования без sqlalchemy"""
        return (
            f"postgresql://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
