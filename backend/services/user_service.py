"""
services/user_service.py
------------------------
Business logic for agent (User) operations.
"""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.user import User
from schemas.user import UserCreate


async def create_agent(db: AsyncSession, payload: UserCreate) -> User:
    """Persist a new agent record and return it."""
    agent = User(
        name=payload.name,
        email=payload.email,
        skills=payload.skills,
        department=payload.department,
    )
    db.add(agent)
    await db.flush()
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


async def list_agents(db: AsyncSession) -> list[User]:
    """Return all agents."""
    result = await db.execute(select(User))
    return list(result.scalars().all())


async def update_agent_skills(
    db: AsyncSession, agent_id: int, skills: list[str]
) -> User | None:
    """Update the skills list for an agent."""
    agent = await get_agent_by_id(db, agent_id)
    if agent is None:
        return None
    agent.skills = skills
    await db.flush()
    await db.refresh(agent)
    return agent


async def update_agent_availability(
    db: AsyncSession, agent_id: int, is_available: bool
) -> User | None:
    """Update the availability flag for an agent."""
    agent = await get_agent_by_id(db, agent_id)
    if agent is None:
        return None
    agent.is_available = is_available
    await db.flush()
    await db.refresh(agent)
    return agent
