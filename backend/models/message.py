"""
models/message.py
-----------------
SQLAlchemy model for messages exchanged within a ticket.
Each message belongs to exactly one ticket and is sent by either
an agent or a customer (discriminated by `sender_type`).
"""

import enum
from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Enum as SAEnum
from sqlalchemy.orm import relationship

from database.connection import Base


class SenderType(str, enum.Enum):
    """Indicates who authored a message."""

    agent = "agent"
    customer = "customer"


class Message(Base):
    """A single message within a support ticket conversation."""

    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)

    # Foreign key to the parent ticket
    ticket_id = Column(Integer, ForeignKey("tickets.id"), nullable=False, index=True)

    sender_type = Column(
        SAEnum(SenderType, name="sender_type"),
        nullable=False,
    )
    content = Column(Text, nullable=False)
    timestamp = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationship back to ticket
    ticket = relationship("Ticket", back_populates="messages", lazy="selectin")
