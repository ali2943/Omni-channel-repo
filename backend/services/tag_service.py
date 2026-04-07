"""
services/tag_service.py
-----------------------
Business logic for Tag operations.
"""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.tag import Tag
from services.ticket_service import get_ticket_by_id


async def get_or_create_tag(db: AsyncSession, name: str) -> Tag:
    """Return the tag with the given name, creating it if necessary."""
    result = await db.execute(select(Tag).where(Tag.name == name))
    tag = result.scalars().first()
    if tag is None:
        tag = Tag(name=name)
        db.add(tag)
        await db.flush()
        await db.refresh(tag)
    return tag


async def add_tag_to_ticket(
    db: AsyncSession, ticket_id: int, tag_name: str
) -> "Ticket | None":  # noqa: F821
    """Add a tag (by name) to a ticket. Returns the updated ticket or None."""
    from models.ticket import Ticket  # local import to avoid circularity
    ticket = await get_ticket_by_id(db, ticket_id)
    if ticket is None:
        return None
    tag = await get_or_create_tag(db, tag_name)
    if tag not in ticket.tags:
        ticket.tags.append(tag)
        await db.flush()
        await db.refresh(ticket)
    return ticket


async def remove_tag_from_ticket(
    db: AsyncSession, ticket_id: int, tag_id: int
) -> "Ticket | None":  # noqa: F821
    """Remove a tag from a ticket by tag ID. Returns the updated ticket or None."""
    ticket = await get_ticket_by_id(db, ticket_id)
    if ticket is None:
        return None
    ticket.tags = [t for t in ticket.tags if t.id != tag_id]
    await db.flush()
    await db.refresh(ticket)
    return ticket


async def list_tags(db: AsyncSession) -> list[Tag]:
    """Return all tags."""
    result = await db.execute(select(Tag).order_by(Tag.name))
    return list(result.scalars().all())
