"""
routes/ai.py
------------
AI engine endpoints (keyword-based simulation).

GET  /ai/suggest-reply/{ticket_id}  – canned reply suggestions
POST /ai/classify/{ticket_id}       – classify and update ticket
POST /ai/prioritize/{ticket_id}     – set priority from content
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db
from schemas.ticket import TicketOut
from services import ai_service
from services.ticket_service import get_ticket_by_id

router = APIRouter(prefix="/ai", tags=["AI Engine"])


@router.get("/suggest-reply/{ticket_id}")
async def suggest_reply(
    ticket_id: int,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Return 3 canned reply suggestions for the ticket's content."""
    ticket = await get_ticket_by_id(db, ticket_id)
    if ticket is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found.")
    content = ""
    if ticket.messages:
        content = ticket.messages[0].content
    elif ticket.subject:
        content = ticket.subject
    channel_str = ticket.channel.value if ticket.channel else None
    suggestions = ai_service.suggest_replies(content, channel_str)
    return {"suggestions": suggestions}


@router.post("/classify/{ticket_id}", response_model=TicketOut)
async def classify_ticket(
    ticket_id: int,
    db: AsyncSession = Depends(get_db),
) -> TicketOut:
    """Classify the ticket's priority and category based on message content, then update."""
    from sqlalchemy import select
    from models.ticket import Ticket

    classification = await ai_service.classify_ticket(db, ticket_id)
    if "error" in classification:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=classification["error"])

    result = await db.execute(select(Ticket).where(Ticket.id == ticket_id))
    ticket = result.scalars().first()
    ticket.priority = classification["suggested_priority"]
    ticket.category = classification["suggested_category"]
    await db.flush()
    await db.refresh(ticket)
    return ticket


@router.post("/prioritize/{ticket_id}", response_model=TicketOut)
async def prioritize_ticket(
    ticket_id: int,
    db: AsyncSession = Depends(get_db),
) -> TicketOut:
    """Update only the priority of a ticket based on message content analysis."""
    from sqlalchemy import select
    from models.ticket import Ticket

    classification = await ai_service.classify_ticket(db, ticket_id)
    if "error" in classification:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=classification["error"])

    result = await db.execute(select(Ticket).where(Ticket.id == ticket_id))
    ticket = result.scalars().first()
    ticket.priority = classification["suggested_priority"]
    await db.flush()
    await db.refresh(ticket)
    return ticket
