"""
schemas/ticket.py
-----------------
Pydantic schemas for the Ticket resource.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from models.ticket import TicketStatus
from schemas.message import MessageOut


class TicketCreate(BaseModel):
    """Payload to create a new ticket."""

    customer_id: int


class TicketAssign(BaseModel):
    """Payload to assign a ticket to an agent."""

    agent_id: int


class TicketStatusUpdate(BaseModel):
    """Payload to update only the status of a ticket."""

    status: TicketStatus


class TicketOut(BaseModel):
    """Response schema for a ticket (without nested messages)."""

    id: int
    customer_id: int
    assigned_agent_id: Optional[int]
    status: TicketStatus
    created_at: datetime

    model_config = {"from_attributes": True}


class TicketDetailOut(TicketOut):
    """Full ticket response including all messages."""

    messages: list[MessageOut] = []
