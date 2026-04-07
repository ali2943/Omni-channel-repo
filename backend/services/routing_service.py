"""
services/routing_service.py
----------------------------
Skill-based ticket routing and queue management.
"""
from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.ticket import Ticket, TicketStatus
from models.user import User
from services.ticket_service import assign_ticket, get_queue


async def get_routing_queue(db: AsyncSession) -> list[Ticket]:
    """Return open, unassigned tickets ordered by priority then age."""
    return await get_queue(db)


async def auto_assign_ticket(
    db: AsyncSession, ticket_id: int
) -> Ticket | None:
    """
    Find the best available agent for a ticket and assign it.

    Selection criteria (in order):
    1. Agent must be available (is_available=True).
    2. Agent's skills should include the ticket's channel or category
       (falls back to any available agent if none match).
    3. Among qualifying agents, pick the one with fewest open/in-progress tickets.

    Returns the updated Ticket, or None if the ticket is not found or no
    agents are available.
    """
    # Fetch the target ticket
    result = await db.execute(select(Ticket).where(Ticket.id == ticket_id))
    ticket = result.scalars().first()
    if ticket is None:
        return None

    # Gather all available agents
    result = await db.execute(select(User).where(User.is_available.is_(True)))
    available_agents = list(result.scalars().all())
    if not available_agents:
        return None

    # Determine the skill hint from channel or category
    skill_hint: str | None = None
    if ticket.channel is not None:
        skill_hint = ticket.channel.value
    elif ticket.category is not None:
        skill_hint = ticket.category.lower()

    # Filter agents by skill hint; fall back to all available agents
    skilled_agents = [
        a for a in available_agents
        if skill_hint and skill_hint in (a.skills or [])
    ]
    candidate_pool = skilled_agents if skilled_agents else available_agents

    # Count open tickets per agent
    open_counts_result = await db.execute(
        select(Ticket.assigned_agent_id, func.count(Ticket.id).label("cnt"))
        .where(
            Ticket.assigned_agent_id.in_([a.id for a in candidate_pool]),
            Ticket.status.in_([TicketStatus.open, TicketStatus.in_progress]),
        )
        .group_by(Ticket.assigned_agent_id)
    )
    open_counts: dict[int, int] = {
        row.assigned_agent_id: row.cnt for row in open_counts_result
    }

    # Pick the agent with the fewest open tickets
    best_agent = min(candidate_pool, key=lambda a: open_counts.get(a.id, 0))

    return await assign_ticket(db, ticket_id, best_agent.id)
