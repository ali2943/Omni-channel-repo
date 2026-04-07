"""
models/ticket.py
----------------
SQLAlchemy model for support tickets.
Links a customer to an (optionally) assigned agent.
"""
from __future__ import annotations

import enum
from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum as SAEnum
from sqlalchemy.orm import relationship

from database.connection import Base


class TicketStatus(str, enum.Enum):
    """Allowed lifecycle states of a ticket."""
    open = "open"
    in_progress = "in_progress"
    closed = "closed"


class ChannelType(str, enum.Enum):
    """Communication channel through which the ticket arrived."""
    voice = "voice"
    whatsapp = "whatsapp"
    facebook = "facebook"
    instagram = "instagram"
    tiktok = "tiktok"
    linkedin = "linkedin"
    shopify = "shopify"
    webchat = "webchat"
    email = "email"


class TicketPriority(str, enum.Enum):
    """Priority level of a ticket."""
    low = "low"
    medium = "medium"
    high = "high"
    urgent = "urgent"


class Ticket(Base):
    """Represents a single support session initiated by a customer."""

    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)

    # Foreign keys
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False, index=True)
    assigned_agent_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)

    status = Column(
        SAEnum(TicketStatus, name="ticket_status"),
        default=TicketStatus.open,
        nullable=False,
    )
    channel = Column(SAEnum(ChannelType, name="channel_type"), nullable=True)
    subject = Column(String(255), nullable=True)
    priority = Column(
        SAEnum(TicketPriority, name="ticket_priority"),
        default=TicketPriority.medium,
        nullable=False,
    )
    category = Column(String(100), nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    sla_due_at = Column(DateTime(timezone=True), nullable=True)
    first_response_at = Column(DateTime(timezone=True), nullable=True)
    closed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    customer = relationship("Customer", back_populates="tickets", lazy="selectin")
    assigned_agent = relationship("User", back_populates="tickets", lazy="selectin")
    messages = relationship(
        "Message",
        back_populates="ticket",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="Message.timestamp",
    )
    tags = relationship(
        "Tag",
        secondary="ticket_tags",
        back_populates="tickets",
        lazy="selectin",
    )
