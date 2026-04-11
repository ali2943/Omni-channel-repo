"""
schemas/customer.py
-------------------
Pydantic schemas for the Customer resource.
"""

from typing import Optional

from pydantic import BaseModel, EmailStr


class CustomerCreate(BaseModel):
    """Payload required to create a new customer."""

    name: str
    email: EmailStr
    phone: Optional[str] = None


class CustomerOut(BaseModel):
    """Response schema returned to the client for a customer."""

    id: int
    name: str
    email: str
    phone: Optional[str] = None
    created_at: str

    model_config = {"from_attributes": True}
