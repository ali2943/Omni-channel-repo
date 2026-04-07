"""
services/ticket_service.py
--------------------------
Business logic for Ticket operations.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.ticket import Ticket, TicketStatus, TicketPriority
from schemas.ticket import TicketCreate, TicketStatusUpdate

# SLA windows keyed by priority
_SLA_HOURS: dict[TicketPriority, int] = {
    TicketPriority.urgent: 1,
    TicketPriority.high: 4,
    TicketPriority.medium: 8,
    TicketPriority.low: 24,
}

# Priority sort order (lower number = higher urgency)
_PRIORITY_ORDER = {
    TicketPriority.urgent: 0,
    TicketPriority.high: 1,
    TicketPriority.medium: 2,
    TicketPriority.low: 3,
}


async def create_ticket(db: AsyncSession, payload: TicketCreate) -> Ticket:
    """Create and persist a new ticket, computing SLA due date from priority."""
    now = datetime.now(timezone.utc)
    sla_hours = _SLA_HOURS.get(payload.priority, 8)
    ticket = Ticket(
        customer_id=payload.customer_id,
        channel=payload.channel,
        subject=payload.subject,
        priority=payload.priority,
        sla_due_at=now + timedelta(hours=sla_hours),
    )
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
    """Assign a ticket to an agent; set first_response_at if not already set."""
    ticket = await get_ticket_by_id(db, ticket_id)
    if ticket is None:
        return None
    ticket.assigned_agent_id = agent_id
    ticket.status = TicketStatus.in_progress
    if ticket.first_response_at is None:
        ticket.first_response_at = datetime.now(timezone.utc)
    await db.flush()
    await db.refresh(ticket)
    return ticket


async def update_ticket_status(
    db: AsyncSession, ticket_id: int, payload: TicketStatusUpdate
) -> Ticket | None:
    """Update the status of an existing ticket; set closed_at when closing."""
    ticket = await get_ticket_by_id(db, ticket_id)
    if ticket is None:
        return None
    ticket.status = payload.status
    if payload.status == TicketStatus.closed and ticket.closed_at is None:
        ticket.closed_at = datetime.now(timezone.utc)
    await db.flush()
    await db.refresh(ticket)
    return ticket


async def get_queue(db: AsyncSession) -> list[Ticket]:
    """Return open, unassigned tickets ordered by priority urgency then created_at."""
    result = await db.execute(
        select(Ticket).where(
            Ticket.status == TicketStatus.open,
            Ticket.assigned_agent_id.is_(None),
        )
    )
    tickets = list(result.scalars().all())
    tickets.sort(
        key=lambda t: (_PRIORITY_ORDER.get(t.priority, 99), t.created_at)
    )
    return tickets
