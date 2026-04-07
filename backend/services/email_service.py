"""
services/email_service.py
--------------------------
Simulates an incoming customer email:
  1. Creates the customer if they don't exist.
  2. Opens a new support ticket for that customer.
  3. Stores the email body as the first message on the ticket.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from models.message import SenderType
from models.ticket import ChannelType
from schemas.message import MessageCreate
from schemas.ticket import TicketCreate
from services.customer_service import get_or_create_customer
from services.message_service import send_message
from services.ticket_service import create_ticket


async def simulate_incoming_email(
    db: AsyncSession,
    customer_name: str,
    customer_email: str,
    subject: str,
    body: str,
) -> dict:
    """
    Simulate receiving an inbound email from a customer.

    Steps:
        1. Get or create the customer record.
        2. Create a new ticket linked to that customer with channel=email.
        3. Store the email body as the opening customer message.

    Returns a dict summarising the created resources.
    """
    customer, was_created = await get_or_create_customer(
        db, name=customer_name, email=customer_email
    )

    ticket = await create_ticket(
        db,
        TicketCreate(
            customer_id=customer.id,
            channel=ChannelType.email,
            subject=subject,
        ),
    )

    message_content = f"[Subject: {subject}]\n\n{body}"
    message = await send_message(
        db,
        ticket_id=ticket.id,
        payload=MessageCreate(
            sender_type=SenderType.customer,
            content=message_content,
        ),
    )

    return {
        "customer_id": customer.id,
        "customer_created": was_created,
        "ticket_id": ticket.id,
        "message_id": message.id,
    }
