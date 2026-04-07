"""
schemas/ticket.py
-----------------
Pydantic schemas for the Ticket resource.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from models.ticket import TicketStatus, ChannelType, TicketPriority
from schemas.message import MessageOut
from schemas.tag import TagOut


class TicketCreate(BaseModel):
    """Payload to create a new ticket."""
    customer_id: int
    channel: Optional[ChannelType] = None
    subject: Optional[str] = None
    priority: TicketPriority = TicketPriority.medium


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
    channel: Optional[ChannelType]
    subject: Optional[str]
    priority: TicketPriority
    category: Optional[str]
    created_at: datetime
    sla_due_at: Optional[datetime]
    first_response_at: Optional[datetime]
    closed_at: Optional[datetime]
    tags: list[TagOut] = []

    model_config = {"from_attributes": True}


class TicketDetailOut(TicketOut):
    """Full ticket response including all messages."""
    messages: list[MessageOut] = []
