"""
routes/messages.py
------------------
HTTP endpoints for Messaging.

POST /tickets/{id}/messages  – send a message in a ticket
GET  /tickets/{id}/messages  – retrieve all messages for a ticket

After persisting a new message the endpoint also broadcasts it over
WebSocket to all clients currently subscribed to that ticket.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db
from schemas.message import MessageCreate, MessageOut
from services import message_service, ticket_service
from utils.connection_manager import manager

router = APIRouter(prefix="/tickets", tags=["Messages"])


@router.post(
    "/{ticket_id}/messages",
    response_model=MessageOut,
    status_code=status.HTTP_201_CREATED,
)
async def send_message(
    ticket_id: int,
    payload: MessageCreate,
    db: AsyncSession = Depends(get_db),
) -> MessageOut:
    """
    Send a message inside a ticket.
    The message is persisted and then broadcast via WebSocket to all
    connected clients watching this ticket.
    """
    # Ensure the ticket exists
    ticket = await ticket_service.get_ticket_by_id(db, ticket_id)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found.",
        )

    message = await message_service.send_message(db, ticket_id, payload)

    # Broadcast the new message to all WebSocket subscribers of this ticket
    await manager.broadcast_to_ticket(
        ticket_id,
        {
            "event": "new_message",
            "message": {
                "id": message.id,
                "ticket_id": message.ticket_id,
                "sender_type": message.sender_type.value,
                "content": message.content,
                "timestamp": message.timestamp.isoformat(),
            },
        },
    )

    return message


@router.get("/{ticket_id}/messages", response_model=list[MessageOut])
async def get_messages(
    ticket_id: int,
    db: AsyncSession = Depends(get_db),
) -> list[MessageOut]:
    """Retrieve the full message history for a ticket."""
    ticket = await ticket_service.get_ticket_by_id(db, ticket_id)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found.",
        )
    return await message_service.get_messages_for_ticket(db, ticket_id)
