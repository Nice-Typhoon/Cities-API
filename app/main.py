from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

import asyncpg
import httpx
from fastapi import FastAPI

from app.api.v1 import api_router
from app.core.config import Settings, get_settings
from app.core.dependencies import AppState
from app.core.exception_handlers import register_exception_handlers
from app.db.database import build_asyncpg_pool, build_engine, build_session_factory


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings: Settings = get_settings()

    engine = build_engine(settings)
    session_factory = build_session_factory(engine)
    asyncpg_pool: asyncpg.Pool = await build_asyncpg_pool(settings)
    http_client = httpx.AsyncClient()

    app.state.app_state = AppState(
        session_factory=session_factory,
        asyncpg_pool=asyncpg_pool,
        http_client=http_client,
        settings=settings,
    )

    yield

    await http_client.aclose()
    await asyncpg_pool.close()
    await engine.dispose()


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.app_title,
        version=settings.app_version,
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    register_exception_handlers(app)
    app.include_router(api_router)

    @app.get("/health", tags=["health"])
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
