"""
schemas/user.py
---------------
Pydantic schemas for the User (agent) resource.
"""

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    """Payload required to create a new agent."""

    name: str
    email: EmailStr


class UserLogin(BaseModel):
    """Payload for a simple agent login check."""

    email: EmailStr


class UserOut(BaseModel):
    """Response schema returned to the client for an agent."""

    id: int
    name: str
    email: str

    model_config = {"from_attributes": True}
