"""
routes/agents.py
----------------
HTTP endpoints for agent (User) management.

POST /agents/          – create a new agent
POST /agents/login     – simple email-based login
GET  /agents/{id}      – fetch a single agent
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db
from schemas.user import UserCreate, UserLogin, UserOut
from services import user_service

router = APIRouter(prefix="/agents", tags=["Agents"])


@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def create_agent(
    payload: UserCreate,
    db: AsyncSession = Depends(get_db),
) -> UserOut:
    """Register a new support agent."""
    existing = await user_service.get_agent_by_email(db, payload.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An agent with this email already exists.",
        )
    agent = await user_service.create_agent(db, payload)
    return agent


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
