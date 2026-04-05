"""
models/ticket.py
----------------
SQLAlchemy model for support tickets.
Links a customer to an (optionally) assigned agent.
"""

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
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

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
