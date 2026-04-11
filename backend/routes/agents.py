"""
routes/agents.py
----------------
HTTP endpoints for agent (User) management.

POST /agents/                        – create a new agent
POST /agents/login                   – simple email-based login
GET  /agents/                        – list all agents
GET  /agents/{id}                    – fetch a single agent
PUT  /agents/{id}/skills             – update agent skills
PUT  /agents/{id}/availability       – update agent availability
"""
from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db
from schemas.user import UserCreate, UserLogin, UserOut
from services import user_service

router = APIRouter(prefix="/agents", tags=["Agents"])
logger = logging.getLogger(__name__)


class SkillsUpdate(BaseModel):
    skills: list[str]


class AvailabilityUpdate(BaseModel):
    is_available: bool


@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def create_agent(
    payload: UserCreate,
    db: AsyncSession = Depends(get_db),
) -> UserOut:
    """Register a new support agent."""
    try:
        existing = await user_service.get_agent_by_email(db, payload.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An agent with this email already exists.",
            )
        agent = await user_service.create_agent(db, payload)
        logger.info("Created agent id=%d email=%s", agent.id, agent.email)
        return agent
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to create agent: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not create agent. Please try again or contact support.",
        ) from exc


@router.post("/login", response_model=UserOut)
async def login_agent(
    payload: UserLogin,
    db: AsyncSession = Depends(get_db),
) -> UserOut:
    """Simple email-based login – returns the agent if found."""
    agent = await user_service.get_agent_by_email(db, payload.email)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No agent found with this email.",
        )
    return agent


@router.get("/", response_model=list[UserOut])
async def list_agents(db: AsyncSession = Depends(get_db)) -> list[UserOut]:
    """Return all agents."""
    return await user_service.list_agents(db)


@router.get("/{agent_id}", response_model=UserOut)
async def get_agent(
    agent_id: int,
    db: AsyncSession = Depends(get_db),
) -> UserOut:
    """Retrieve a single agent by ID."""
    agent = await user_service.get_agent_by_id(db, agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found.",
        )
    return agent


@router.put("/{agent_id}/skills", response_model=UserOut)
async def update_skills(
    agent_id: int,
    payload: SkillsUpdate,
    db: AsyncSession = Depends(get_db),
) -> UserOut:
    """Update the skills list for an agent."""
    agent = await user_service.update_agent_skills(db, agent_id, payload.skills)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found.",
        )
    return agent


@router.put("/{agent_id}/availability", response_model=UserOut)
async def update_availability(
    agent_id: int,
    payload: AvailabilityUpdate,
    db: AsyncSession = Depends(get_db),
) -> UserOut:
    """Update the availability status for an agent."""
    agent = await user_service.update_agent_availability(
        db, agent_id, payload.is_available
    )
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found.",
        )
    return agent
