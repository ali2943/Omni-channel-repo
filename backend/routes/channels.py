"""
routes/channels.py
------------------
Channel simulation endpoints. Each endpoint mimics an inbound message
arriving from a specific communication platform.

POST /simulate/whatsapp   – WhatsApp inbound message
POST /simulate/social     – Social media (Facebook/Instagram/TikTok/LinkedIn)
POST /simulate/voice      – Inbound voice call
POST /simulate/shopify    – Shopify order inquiry
POST /simulate/webchat    – Web chat message
"""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db
from models.message import SenderType
from models.ticket import ChannelType
from schemas.message import MessageCreate
from schemas.ticket import TicketCreate
from services.customer_service import get_or_create_customer
from services.message_service import send_message
from services.ticket_service import create_ticket

router = APIRouter(prefix="/simulate", tags=["Channel Simulations"])


# ---------------------------------------------------------------------------
# Request bodies
# ---------------------------------------------------------------------------

class WhatsAppPayload(BaseModel):
    customer_name: str
    customer_phone: str
    message: str


class SocialPayload(BaseModel):
    platform: ChannelType  # must be facebook/instagram/tiktok/linkedin
    customer_handle: str
    message: str


class VoicePayload(BaseModel):
    customer_name: str
    customer_phone: str
    notes: str


class ShopifyPayload(BaseModel):
    customer_name: str
    customer_email: str
    order_id: str
    issue: str


class WebchatPayload(BaseModel):
    customer_name: str
    customer_email: str
    message: str


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------
_SOCIAL_PLATFORMS = {
    ChannelType.facebook,
    ChannelType.instagram,
    ChannelType.tiktok,
    ChannelType.linkedin,
}


async def _create_interaction(
    db: AsyncSession,
    *,
    name: str,
    email: str,
    channel: ChannelType,
    subject: Optional[str],
    message_content: str,
) -> dict:
    """Shared logic: resolve customer → create ticket → store first message."""
    customer, was_created = await get_or_create_customer(db, name=name, email=email)
    ticket = await create_ticket(
        db,
        TicketCreate(
            customer_id=customer.id,
            channel=channel,
            subject=subject,
        ),
    )
    message = await send_message(
        db,
        ticket_id=ticket.id,
        payload=MessageCreate(sender_type=SenderType.customer, content=message_content),
    )
    return {
        "customer_id": customer.id,
        "customer_created": was_created,
        "ticket_id": ticket.id,
        "message_id": message.id,
    }


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("/whatsapp")
async def simulate_whatsapp(
    payload: WhatsAppPayload,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Simulate an inbound WhatsApp message."""
    email = f"{payload.customer_phone}@whatsapp.sim"
    return await _create_interaction(
        db,
        name=payload.customer_name,
        email=email,
        channel=ChannelType.whatsapp,
        subject="WhatsApp Message",
        message_content=payload.message,
    )


@router.post("/social")
async def simulate_social(
    payload: SocialPayload,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Simulate an inbound social media message (Facebook/Instagram/TikTok/LinkedIn)."""
    if payload.platform not in _SOCIAL_PLATFORMS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Platform must be one of: {', '.join(p.value for p in _SOCIAL_PLATFORMS)}",
        )
    email = f"{payload.customer_handle}@{payload.platform.value}.sim"
    return await _create_interaction(
        db,
        name=payload.customer_handle,
        email=email,
        channel=payload.platform,
        subject=f"{payload.platform.value.capitalize()} Message",
        message_content=payload.message,
    )


@router.post("/voice")
async def simulate_voice(
    payload: VoicePayload,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Simulate an inbound voice call."""
    email = f"{payload.customer_phone}@voice.sim"
    return await _create_interaction(
        db,
        name=payload.customer_name,
        email=email,
        channel=ChannelType.voice,
        subject="Inbound Call",
        message_content=payload.notes,
    )


@router.post("/shopify")
async def simulate_shopify(
    payload: ShopifyPayload,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Simulate an inbound Shopify order inquiry."""
    return await _create_interaction(
        db,
        name=payload.customer_name,
        email=payload.customer_email,
        channel=ChannelType.shopify,
        subject=f"Order #{payload.order_id}",
        message_content=payload.issue,
    )


@router.post("/webchat")
async def simulate_webchat(
    payload: WebchatPayload,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Simulate an inbound web chat message."""
    return await _create_interaction(
        db,
        name=payload.customer_name,
        email=payload.customer_email,
        channel=ChannelType.webchat,
        subject="Web Chat",
        message_content=payload.message,
    )
