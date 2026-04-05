"""
database/connection.py
----------------------
Sets up the async SQLAlchemy engine and session factory.
Provides a `get_db` dependency for injecting database sessions into routes.
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

# ---------------------------------------------------------------------------
# Database URL – override via environment variable in production
# ---------------------------------------------------------------------------
import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/omnichannel",
)

# ---------------------------------------------------------------------------
# Engine (connection pool shared across the application)
# ---------------------------------------------------------------------------
engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # Set to True for SQL query logging during development
    pool_pre_ping=True,
)

# ---------------------------------------------------------------------------
# Session factory
# ---------------------------------------------------------------------------
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# ---------------------------------------------------------------------------
# Declarative base – all SQLAlchemy models inherit from this
# ---------------------------------------------------------------------------
class Base(DeclarativeBase):
    pass


# ---------------------------------------------------------------------------
# FastAPI dependency: yields a DB session per request
# ---------------------------------------------------------------------------
async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


def get_db_context() -> "_DbContextManager":
    """
    Return an async context manager that yields a committed DB session.
    Use this in non-Depends contexts such as WebSocket handlers where
    FastAPI's dependency injection is not available.

    Usage::

        async with get_db_context() as db:
            await some_service_call(db, ...)
    """
    return _DbContextManager()


class _DbContextManager:
    """Async context manager wrapping a single DB session with commit/rollback."""

    async def __aenter__(self) -> AsyncSession:
        self._session = AsyncSessionLocal()
        await self._session.__aenter__()
        return self._session

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        try:
            if exc_type is None:
                await self._session.commit()
            else:
                await self._session.rollback()
        finally:
            await self._session.__aexit__(exc_type, exc_val, exc_tb)
