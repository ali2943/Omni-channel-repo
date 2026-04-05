"""
services/ticket_service.py
--------------------------
Business logic for Ticket operations.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.ticket import Ticket, TicketStatus
from schemas.ticket import TicketCreate, TicketStatusUpdate


async def create_ticket(db: AsyncSession, payload: TicketCreate) -> Ticket:
    """Create and persist a new ticket for the given customer."""
    ticket = Ticket(customer_id=payload.customer_id)
    db.add(ticket)
    await db.flush()
    await db.refresh(ticket)
    return ticket


async def get_all_tickets(db: AsyncSession) -> list[Ticket]:
    """Return all tickets ordered by creation date (newest first)."""
    result = await db.execute(select(Ticket).order_by(Ticket.created_at.desc()))
    return list(result.scalars().all())


async def get_ticket_by_id(db: AsyncSession, ticket_id: int) -> Ticket | None:
    """Return a ticket by primary key including its messages, or None."""
    result = await db.execute(select(Ticket).where(Ticket.id == ticket_id))
    return result.scalars().first()


async def assign_ticket(
    db: AsyncSession, ticket_id: int, agent_id: int
) -> Ticket | None:
    """Assign a ticket to an agent and update its status to in_progress."""
    ticket = await get_ticket_by_id(db, ticket_id)
    if ticket is None:
        return None
    ticket.assigned_agent_id = agent_id
    ticket.status = TicketStatus.in_progress
    await db.flush()
    await db.refresh(ticket)
    return ticket


async def update_ticket_status(
    db: AsyncSession, ticket_id: int, payload: TicketStatusUpdate
) -> Ticket | None:
    """Update the status of an existing ticket."""
    ticket = await get_ticket_by_id(db, ticket_id)
    if ticket is None:
        return None
    ticket.status = payload.status
    await db.flush()
    await db.refresh(ticket)
    return ticket
