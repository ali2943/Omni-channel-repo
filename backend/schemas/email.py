"""
schemas/email.py
----------------
Pydantic schemas for the email-simulation endpoint.
"""

from pydantic import BaseModel, EmailStr


class IncomingEmailPayload(BaseModel):
    """Payload mimicking a raw inbound email."""

    customer_name: str
    customer_email: EmailStr
    subject: str
    body: str
