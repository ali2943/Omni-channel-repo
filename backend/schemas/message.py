"""
schemas/message.py
------------------
Pydantic schemas for the Message resource.
"""

from datetime import datetime

from pydantic import BaseModel

from models.message import SenderType


class MessageCreate(BaseModel):
    """Payload to send a new message in a ticket."""

    sender_type: SenderType
    content: str


class MessageOut(BaseModel):
    """Response schema for a single message."""

    id: int
    ticket_id: int
    sender_type: SenderType
    content: str
    timestamp: datetime

    model_config = {"from_attributes": True}
