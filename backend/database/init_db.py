"""
database/init_db.py
-------------------
Utility script to create all database tables on startup.
Call `init_models()` from main.py during application startup.
"""

from database.connection import engine, Base

# Import all models so that SQLAlchemy registers them with Base.metadata
import models.user        # noqa: F401
import models.customer    # noqa: F401
import models.ticket      # noqa: F401
import models.message     # noqa: F401


async def init_models() -> None:
    """Create all tables if they don't already exist."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
