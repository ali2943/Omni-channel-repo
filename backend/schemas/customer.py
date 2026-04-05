"""
schemas/customer.py
-------------------
Pydantic schemas for the Customer resource.
"""

from pydantic import BaseModel, EmailStr


class CustomerCreate(BaseModel):
    """Payload required to create a new customer."""

    name: str
    email: EmailStr


class CustomerOut(BaseModel):
    """Response schema returned to the client for a customer."""

    id: int
    name: str
    email: str

    model_config = {"from_attributes": True}
