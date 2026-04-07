"""
models/user.py
--------------
SQLAlchemy model for support agents (internal users).
An agent can be assigned to multiple tickets.
"""

from sqlalchemy import Boolean, Column, Integer, JSON, String
from sqlalchemy.orm import relationship

from database.connection import Base


class User(Base):
    """Represents a support agent in the system."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    skills = Column(JSON, nullable=False, default=list)
    is_available = Column(Boolean, default=True, nullable=False)
    department = Column(String(100), nullable=True)

    # An agent can be assigned to many tickets
    tickets = relationship("Ticket", back_populates="assigned_agent", lazy="selectin")
