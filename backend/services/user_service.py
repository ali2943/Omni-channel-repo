"""
services/user_service.py
------------------------
Business logic for agent (User) operations.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.user import User
from schemas.user import UserCreate


async def create_agent(db: AsyncSession, payload: UserCreate) -> User:
    """Persist a new agent record and return it."""
    agent = User(name=payload.name, email=payload.email)
    db.add(agent)
    await db.flush()  # Populate `agent.id` without committing
    await db.refresh(agent)
    return agent


async def get_agent_by_email(db: AsyncSession, email: str) -> User | None:
    """Return the agent matching the given email, or None."""
    result = await db.execute(select(User).where(User.email == email))
    return result.scalars().first()


async def get_agent_by_id(db: AsyncSession, agent_id: int) -> User | None:
    """Return an agent by primary key, or None."""
    result = await db.execute(select(User).where(User.id == agent_id))
    return result.scalars().first()
