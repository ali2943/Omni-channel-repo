"""
routes/websocket.py
-------------------
WebSocket endpoint for real-time messaging.

WS /ws/tickets/{ticket_id}

Clients connect to a ticket-specific channel.  Any message received from the
client is persisted to the database and then broadcast to all other subscribers
of that ticket.
"""

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import AsyncSessionLocal
from models.message import SenderType
from schemas.message import MessageCreate
from services import message_service
from utils.connection_manager import manager

router = APIRouter(tags=["WebSocket"])


@router.websocket("/ws/tickets/{ticket_id}")
async def websocket_endpoint(websocket: WebSocket, ticket_id: int) -> None:
    """
    Real-time WebSocket channel for a ticket.

    Expected inbound JSON payload:
        {
            "sender_type": "agent" | "customer",
            "content": "Hello!"
        }

    The server persists the message and broadcasts it to all connected
    clients on the same ticket channel (including the sender).
    """
    await manager.connect(websocket, ticket_id)
    try:
        while True:
            data = await websocket.receive_json()

            # Validate the sender_type field
            sender_type_value = data.get("sender_type", "customer")
            try:
                sender_type = SenderType(sender_type_value)
            except ValueError:
                await websocket.send_json(
                    {"error": f"Invalid sender_type: '{sender_type_value}'"}
                )
                continue

            content = data.get("content", "").strip()
            if not content:
                await websocket.send_json({"error": "Message content cannot be empty."})
                continue

            # Persist the message using a fresh DB session
            async with AsyncSessionLocal() as db:
                try:
                    message = await message_service.send_message(
                        db,
                        ticket_id=ticket_id,
                        payload=MessageCreate(
                            sender_type=sender_type,
                            content=content,
                        ),
                    )
                    await db.commit()
                except Exception as exc:
                    await db.rollback()
                    await websocket.send_json({"error": str(exc)})
                    continue

            # Broadcast to all subscribers of this ticket
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

    except WebSocketDisconnect:
        manager.disconnect(websocket, ticket_id)
