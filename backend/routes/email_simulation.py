"""
routes/email_simulation.py
--------------------------
HTTP endpoint that triggers the incoming-email simulation.

POST /simulate/email
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db
from schemas.email import IncomingEmailPayload
from services.email_service import simulate_incoming_email

router = APIRouter(prefix="/simulate", tags=["Email Simulation"])


@router.post("/email", status_code=status.HTTP_201_CREATED)
async def simulate_email(
    payload: IncomingEmailPayload,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Simulate receiving a customer email.
    - Creates the customer if they are new.
    - Opens a support ticket.
    - Stores the email body as the first message.
    """
    result = await simulate_incoming_email(
        db,
        customer_name=payload.customer_name,
        customer_email=payload.customer_email,
        subject=payload.subject,
        body=payload.body,
    )
    return result
