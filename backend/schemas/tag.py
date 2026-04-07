"""
schemas/tag.py
--------------
Pydantic schemas for the Tag resource.
"""

from pydantic import BaseModel


class TagCreate(BaseModel):
    """Payload to create a tag."""
    name: str


class TagOut(BaseModel):
    """Response schema for a tag."""
    id: int
    name: str

    model_config = {"from_attributes": True}
