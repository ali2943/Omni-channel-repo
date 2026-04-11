"""
models/customer.py
------------------
SQLAlchemy model for customers who open support tickets.
A customer can have multiple tickets.
"""

from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

from database.connection import Base


class Customer(Base):
    """Represents an external customer contacting support."""

    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone = Column(String(50), nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # A customer can open many tickets
    tickets = relationship("Ticket", back_populates="customer", lazy="selectin")
