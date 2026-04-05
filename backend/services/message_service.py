"""
services/message_service.py
----------------------------
Business logic for Message operations.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.message import Message
from schemas.message import MessageCreate


async def send_message(
    db: AsyncSession, ticket_id: int, payload: MessageCreate
) -> Message:
    """Persist a new message for a ticket and return it."""
    message = Message(
        ticket_id=ticket_id,
        sender_type=payload.sender_type,
        content=payload.content,
    )
    db.add(message)
    await db.flush()
    await db.refresh(message)
    return message


async def get_messages_for_ticket(
    db: AsyncSession, ticket_id: int
) -> list[Message]:
    """Return all messages for a ticket, ordered by timestamp ascending."""
    result = await db.execute(
        select(Message)
        .where(Message.ticket_id == ticket_id)
        .order_by(Message.timestamp.asc())
    )
    return list(result.scalars().all())
