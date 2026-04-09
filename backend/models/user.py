"""
models/user.py
--------------
SQLAlchemy model for support agents (internal users).
An agent can be assigned to multiple tickets.
"""

from sqlalchemy import Boolean, Column, Float, Integer, JSON, String
from sqlalchemy.orm import relationship

from database.connection import Base


class User(Base):
    """Represents a support agent in the system (human or AI-powered)."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    skills = Column(JSON, nullable=False, default=list)
    is_available = Column(Boolean, default=True, nullable=False)
    department = Column(String(100), nullable=True)

    # AI agent configuration fields
    is_ai_agent = Column(Boolean, default=False, nullable=False)
    ai_model = Column(String(50), nullable=True)          # e.g. "gpt-4", "gpt-3.5-turbo"
    ai_config = Column(JSON, nullable=True)               # temperature, max_tokens, system_prompt
    knowledge_base_enabled = Column(Boolean, default=False, nullable=False)
    auto_respond = Column(Boolean, default=False, nullable=False)
    confidence_threshold = Column(Float, default=0.7, nullable=False)

    # An agent can be assigned to many tickets
    tickets = relationship("Ticket", back_populates="assigned_agent", lazy="selectin")
