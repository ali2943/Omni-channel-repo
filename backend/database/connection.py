"""
database/connection.py
----------------------
Sets up the async SQLAlchemy engine and session factory for PostgreSQL.
Provides a `get_db` dependency for injecting database sessions into routes,
and a `get_db_context` helper for use outside of FastAPI's DI system.

Environment variables
---------------------
DATABASE_URL : str
    Full async connection URL, e.g.
    ``postgresql+asyncpg://user:password@host:5432/dbname``.
    Falls back to a local development default when not set.
DB_POOL_SIZE : int
    Number of persistent connections kept in the pool (default: 5).
DB_MAX_OVERFLOW : int
    Extra connections allowed above *pool_size* under peak load (default: 10).
DB_ECHO : bool
    When ``"true"`` (case-insensitive), SQLAlchemy logs every SQL statement.
    Useful during development; leave unset in production.
"""

from __future__ import annotations

import os
from typing import AsyncGenerator

from dotenv import load_dotenv

# Load variables from a .env file in the backend directory (if present).
# This must happen before any os.getenv() call reads DATABASE_URL etc.
load_dotenv()

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _parse_int_env(name: str, default: int) -> int:
    """Read *name* from the environment and parse it as an integer.

    Raises a :class:`ValueError` with a clear message if the value is present
    but cannot be interpreted as a whole number.
    """
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        return int(raw)
    except ValueError:
        raise ValueError(
            f"Environment variable {name!r} must be an integer, got {raw!r}."
        ) from None


# ---------------------------------------------------------------------------
# Database URL – override via environment variable in production
# ---------------------------------------------------------------------------
DATABASE_URL: str = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/omnichannel",
)

# ---------------------------------------------------------------------------
# Engine (connection pool shared across the application)
# ---------------------------------------------------------------------------
engine = create_async_engine(
    DATABASE_URL,
    # Set DB_ECHO=true to log every SQL statement (development only).
    echo=os.getenv("DB_ECHO", "false").lower() == "true",
    # Verify connections before handing them back from the pool.
    pool_pre_ping=True,
    # Persistent connections kept alive in the pool.
    pool_size=_parse_int_env("DB_POOL_SIZE", 5),
    # Additional connections allowed above pool_size during traffic spikes.
    max_overflow=_parse_int_env("DB_MAX_OVERFLOW", 10),
)

# ---------------------------------------------------------------------------
# Session factory
# ---------------------------------------------------------------------------
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    # Explicitly disable auto-commit so callers always control transaction boundaries.
    autocommit=False,
    # Explicitly disable auto-flush so callers decide when to write pending state.
    autoflush=False,
    # Keep objects usable after commit without re-fetching from the DB.
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
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Yield a transactional database session for use as a FastAPI dependency.

    Commits on success and rolls back automatically on any unhandled exception,
    ensuring every request leaves the database in a consistent state.

    Usage::

        @router.get("/items")
        async def list_items(db: AsyncSession = Depends(get_db)):
            ...
    """
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
