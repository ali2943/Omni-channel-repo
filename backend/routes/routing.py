"""
routes/routing.py
-----------------
Ticket routing endpoints.

GET  /routing/queue                   – open unassigned ticket queue
POST /routing/auto-assign/{ticket_id} – skill-based auto-assignment
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db
from schemas.ticket import TicketOut
from services import routing_service

router = APIRouter(prefix="/routing", tags=["Routing"])


@router.get("/queue", response_model=list[TicketOut])
async def get_queue(db: AsyncSession = Depends(get_db)) -> list[TicketOut]:
    """Return open, unassigned tickets ordered by priority then age."""
    return await routing_service.get_routing_queue(db)


@router.post("/auto-assign/{ticket_id}", response_model=TicketOut)
async def auto_assign(
    ticket_id: int,
    db: AsyncSession = Depends(get_db),
) -> TicketOut:
    """Automatically assign a ticket to the best available agent."""
    ticket = await routing_service.auto_assign_ticket(db, ticket_id)
    if ticket is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found or no available agents.",
        )
    return ticket
