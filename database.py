import os
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

try:
    from config import URL_DATABASE
except Exception:
    URL_DATABASE = None

from models import Base


# Convert PostgreSQL URL from psycopg2 format to asyncpg format
# Example: postgresql:// -> postgresql+asyncpg://
def get_async_db_url(url: str) -> str:
    """
    Converts a PostgreSQL URL from psycopg2 format to asyncpg format.

    This function takes a database URL and converts it to the format required by asyncpg
    if it's a PostgreSQL URL. If the URL already uses the asyncpg format or is for a
    different database type, it's returned unchanged.

    Args:
        url: The database URL string to convert

    Returns:
        The converted URL with the asyncpg driver prefix if applicable, otherwise the original URL
    """
    if not url:
        raise RuntimeError(
            "Database URL is missing. Set URL_DATABASE (preferred) or URL_DATABASE in environment."
        )

    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+asyncpg://")
    return url


raw_db_url = os.getenv("URL_DATABASE") or URL_DATABASE or os.getenv("URL_DATABASE")
async_db_url = get_async_db_url(raw_db_url)

# Global variable to store the engine
async_engine: AsyncEngine | None = None


async def initialize_database():
    """
    Initializes the database by checking if it exists and creating the engine.
    This should be called at application startup.
    """
    global async_engine, AsyncSessionLocal

    if async_engine is not None:
        return async_engine

    # Create async engine
    async_engine = create_async_engine(async_db_url, echo=False, pool_pre_ping=True)

    AsyncSessionLocal = async_sessionmaker(
        bind=async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False,
    )

    return async_engine



def get_engine():
    """
    Returns the async engine. If not initialized, raises an error.
    """
    if async_engine is None:
        raise RuntimeError(
            "Database not initialized. Call initialize_database() first."
        )
    return async_engine



# Create async session factory - will be initialized after engine creation
AsyncSessionLocal: async_sessionmaker[AsyncSession] | None = None


def get_session_factory():
    """
    Returns the async session factory. Creates it if not already initialized.
    """
    global AsyncSessionLocal
    if AsyncSessionLocal is None:
        raise RuntimeError(
            "Session factory not initialized. Call initialize_database() first."
        )
    return AsyncSessionLocal


# Dependency to get async DB session
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency function to get an async database session.

    This function creates and yields an async database session using the AsyncSessionLocal
    factory. It ensures that the session is properly closed after use, even if an exception
    occurs during the request handling.

    Yields:
        AsyncSession: An async SQLAlchemy session for database operations
    """
    session_factory = get_session_factory()
    async with session_factory() as session:
        yield session
