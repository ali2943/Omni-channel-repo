"""
services/ai_service.py
-----------------------
Keyword-based simulated AI helpers for ticket triage and reply suggestions.
No external API calls are made.
"""
from __future__ import annotations

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.message import Message
from models.ticket import TicketPriority

# ---------------------------------------------------------------------------
# Keyword lists
# ---------------------------------------------------------------------------
_URGENT_KW = {"urgent", "asap", "emergency", "critical", "broken", "down", "outage"}
_HIGH_KW = {"not working", "error", "issue", "problem", "fail"}
_LOW_KW = {"question", "curious", "wondering", "when will"}

_BILLING_KW = {"payment", "invoice", "charge", "bill", "refund", "money"}
_TECHNICAL_KW = {"bug", "error", "crash", "not loading", "broken"}
_SHIPPING_KW = {"delivery", "shipment", "order", "track", "arrived"}


def _lower(text: str) -> str:
    return text.lower()


def suggest_priority(content: str) -> TicketPriority:
    """Classify ticket priority from message content using keyword matching."""
    text = _lower(content)
    if any(kw in text for kw in _URGENT_KW):
        return TicketPriority.urgent
    if any(kw in text for kw in _HIGH_KW):
        return TicketPriority.high
    if any(kw in text for kw in _LOW_KW):
        return TicketPriority.low
    return TicketPriority.medium


def suggest_category(content: str, channel: Optional[str] = None) -> str:
    """Classify ticket category from message content using keyword matching."""
    text = _lower(content)
    if any(kw in text for kw in _BILLING_KW):
        return "billing"
    if any(kw in text for kw in _TECHNICAL_KW):
        return "technical"
    if any(kw in text for kw in _SHIPPING_KW):
        return "shipping"
    return channel or "general"


def suggest_replies(
    ticket_content: str, channel: Optional[str] = None
) -> list[str]:
    """Return 3 canned reply suggestions based on ticket content keywords."""
    text = _lower(ticket_content)
    replies: list[str] = [
        "Thank you for reaching out to our support team. We'll assist you shortly."
    ]
    if any(kw in text for kw in _BILLING_KW):
        replies.append(
            "I'll look into your billing concern immediately and get back to you with details."
        )
    elif any(kw in text for kw in _TECHNICAL_KW):
        replies.append(
            "Let me investigate this technical issue and provide you with a resolution."
        )
    elif any(kw in text for kw in _SHIPPING_KW):
        replies.append(
            "I'll check your order status right away and update you with the latest information."
        )
    else:
        replies.append(
            "I understand your concern. Let me look into this and get back to you promptly."
        )
    replies.append(
        "Is there any additional information you can provide to help us resolve this faster?"
    )
    return replies[:3]


async def classify_ticket(db: AsyncSession, ticket_id: int) -> dict:
    """
    Suggest priority and category for a ticket by reading its first message.
    Returns a dict with keys: ticket_id, suggested_priority, suggested_category.
    """
    from models.ticket import Ticket  # local import

    result = await db.execute(select(Ticket).where(Ticket.id == ticket_id))
    ticket = result.scalars().first()
    if ticket is None:
        return {"ticket_id": ticket_id, "error": "Ticket not found"}

    # Fetch first message
    msg_result = await db.execute(
        select(Message)
        .where(Message.ticket_id == ticket_id)
        .order_by(Message.timestamp.asc())
        .limit(1)
    )
    first_msg = msg_result.scalars().first()
    content = first_msg.content if first_msg else (ticket.subject or "")
    channel_str = ticket.channel.value if ticket.channel else None

    return {
        "ticket_id": ticket_id,
        "suggested_priority": suggest_priority(content),
        "suggested_category": suggest_category(content, channel_str),
    }
