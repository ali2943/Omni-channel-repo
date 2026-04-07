"""
routes/tickets.py
-----------------
HTTP endpoints for Ticket management.

POST   /tickets/                       – create a new ticket
GET    /tickets/                       – list all tickets
GET    /tickets/{id}                   – get ticket with messages
PUT    /tickets/{id}/assign            – assign ticket to agent
PUT    /tickets/{id}/status            – update ticket status
POST   /tickets/{id}/tags              – add tag to ticket
DELETE /tickets/{id}/tags/{tag_id}     – remove tag from ticket
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db
from schemas.tag import TagCreate
from schemas.ticket import (
    TicketAssign,
    TicketCreate,
    TicketDetailOut,
    TicketOut,
    TicketStatusUpdate,
)
from services import ticket_service
from services import tag_service

router = APIRouter(prefix="/tickets", tags=["Tickets"])


@router.post("/", response_model=TicketOut, status_code=status.HTTP_201_CREATED)
async def create_ticket(
    payload: TicketCreate,
    db: AsyncSession = Depends(get_db),
) -> TicketOut:
    """Open a new support ticket for a customer."""
    ticket = await ticket_service.create_ticket(db, payload)
    return ticket


@router.get("/", response_model=list[TicketOut])
async def list_tickets(db: AsyncSession = Depends(get_db)) -> list[TicketOut]:
    """Return all tickets (newest first)."""
    return await ticket_service.get_all_tickets(db)


@router.get("/{ticket_id}", response_model=TicketDetailOut)
async def get_ticket(
    ticket_id: int,
    db: AsyncSession = Depends(get_db),
) -> TicketDetailOut:
    """Return a ticket and its complete message history."""
    ticket = await ticket_service.get_ticket_by_id(db, ticket_id)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found.",
        )
    return ticket


@router.put("/{ticket_id}/assign", response_model=TicketOut)
async def assign_ticket(
    ticket_id: int,
    payload: TicketAssign,
    db: AsyncSession = Depends(get_db),
) -> TicketOut:
    """Assign a ticket to a specific agent."""
    ticket = await ticket_service.assign_ticket(db, ticket_id, payload.agent_id)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found.",
        )
    return ticket


@router.put("/{ticket_id}/status", response_model=TicketOut)
async def update_ticket_status(
    ticket_id: int,
    payload: TicketStatusUpdate,
    db: AsyncSession = Depends(get_db),
) -> TicketOut:
    """Update the lifecycle status of a ticket."""
    ticket = await ticket_service.update_ticket_status(db, ticket_id, payload)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found.",
        )
    return ticket


@router.post("/{ticket_id}/tags", response_model=TicketOut)
async def add_tag(
    ticket_id: int,
    payload: TagCreate,
    db: AsyncSession = Depends(get_db),
) -> TicketOut:
    """Add a tag to a ticket by name (creates the tag if it doesn't exist)."""
    ticket = await tag_service.add_tag_to_ticket(db, ticket_id, payload.name)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found.",
        )
    return ticket


@router.delete("/{ticket_id}/tags/{tag_id}", response_model=TicketOut)
async def remove_tag(
    ticket_id: int,
    tag_id: int,
    db: AsyncSession = Depends(get_db),
) -> TicketOut:
    """Remove a tag from a ticket."""
    ticket = await tag_service.remove_tag_from_ticket(db, ticket_id, tag_id)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found.",
        )
    return ticket
