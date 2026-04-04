import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import async_db_url, get_db, get_engine, initialize_database
from config import (
    ENABLE_API_DOCS,
    SERVICE_HOST,
    SERVICE_PORT,
    SERVICE_REFRESH,
    SERVICE_WORKERS,
)
from models import Submission
from routers.api_v1 import router as api_v1_router


def _as_int(value: Any, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _as_bool(value: Any, default: bool = False) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


SERVICE_PORT = _as_int(SERVICE_PORT, 8080)
SERVICE_REFRESH = _as_bool(SERVICE_REFRESH, False)
SERVICE_WORKERS = _as_int(SERVICE_WORKERS, 8)
SERVICE_HOST = SERVICE_HOST or "0.0.0.0"
ENABLE_API_DOCS = _as_bool(ENABLE_API_DOCS, True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for FastAPI application."""
    try:
        if not async_db_url.startswith("postgresql+asyncpg://"):
            raise RuntimeError(
                "URL_DATABASE/URL_DATABASE must resolve to a postgresql+asyncpg:// URL"
            )
        await initialize_database()
        logging.info("Database initialized successfully")
    except Exception as e:
        logging.exception("Failed to initialize database")
        raise e
    try:
        yield
    finally:
        try:
            engine = get_engine()
            await engine.dispose()
            logging.info("Database connections closed successfully")
        except Exception:
            logging.exception("Error during database cleanup")


app = FastAPI(
    lifespan=lifespan,
    docs_url="/docs" if ENABLE_API_DOCS else None,
    redoc_url="/redoc" if ENABLE_API_DOCS else None,
    openapi_url="/openapi.json" if ENABLE_API_DOCS else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Retry-After"],
)


@app.get("/health")
async def health() -> dict[str, str]:
	return {
		"status": "healthy"
	}

app.include_router(api_v1_router)

if __name__ == "__main__":
    import uvicorn
    import create_db as create_db_module

    asyncio.run(create_db_module.main())

    uvicorn_kwargs = {
        "app": "main:app",
        "host": SERVICE_HOST,
        "port": SERVICE_PORT,
        "reload": SERVICE_REFRESH,
        "workers": 1 if SERVICE_REFRESH else max(1, SERVICE_WORKERS),
    }

    uvicorn.run(**uvicorn_kwargs)
