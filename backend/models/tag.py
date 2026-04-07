"""
models/tag.py
-------------
SQLAlchemy model for ticket tags and the ticket_tags association table.
"""
from __future__ import annotations

from sqlalchemy import Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship

from database.connection import Base

# Association table – plain Table, not a mapped class
ticket_tags = Table(
    "ticket_tags",
    Base.metadata,
    Column("ticket_id", Integer, ForeignKey("tickets.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True),
)


class Tag(Base):
    """A label that can be attached to one or more tickets."""

    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)

    tickets = relationship(
        "Ticket",
        secondary="ticket_tags",
        back_populates="tags",
        lazy="selectin",
    )
