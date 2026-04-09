"""
models/agent_knowledge.py
-------------------------
SQLAlchemy models for AI agent knowledge management and response auditing.
"""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, LargeBinary, String, Text
from sqlalchemy.orm import relationship

from database.connection import Base


class AgentKnowledgeBase(Base):
    """Stores knowledge documents associated with an AI agent."""

    __tablename__ = "agent_knowledge_bases"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    category = Column(String(100), nullable=True, default="General")

    # Raw embedding bytes (numpy array serialised with numpy.save / numpy.load)
    embedding = Column(LargeBinary, nullable=True)
    embedding_model = Column(String(50), nullable=True, default="text-embedding-3-small")

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    agent = relationship("User", backref="knowledge_bases")


class AgentResponse(Base):
    """Audit trail of every AI-generated response."""

    __tablename__ = "agent_responses"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id", ondelete="CASCADE"), nullable=False, index=True)

    customer_query = Column(Text, nullable=False)
    ai_response = Column(Text, nullable=False)
    confidence_score = Column(Float, nullable=True)
    sources_used = Column(Text, nullable=True)  # JSON-encoded list of knowledge base IDs

    # "pending" | "approved" | "rejected"
    human_review_status = Column(String(20), default="pending", nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    agent = relationship("User")
    ticket = relationship("Ticket")
