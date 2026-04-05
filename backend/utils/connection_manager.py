"""
utils/connection_manager.py
----------------------------
Manages active WebSocket connections.
Supports broadcasting messages to all clients watching a specific ticket.
"""

from collections import defaultdict

from fastapi import WebSocket


class ConnectionManager:
    """
    Maintains a registry of active WebSocket connections grouped by ticket_id.
    This allows targeted broadcasts (only clients subscribed to a ticket
    receive its new messages).
    """

    def __init__(self) -> None:
        # Maps ticket_id -> list of connected WebSockets
        self._active: dict[int, list[WebSocket]] = defaultdict(list)

    async def connect(self, websocket: WebSocket, ticket_id: int) -> None:
        """Accept a WebSocket handshake and register it under the ticket."""
        await websocket.accept()
        self._active[ticket_id].append(websocket)

    def disconnect(self, websocket: WebSocket, ticket_id: int) -> None:
        """Remove a WebSocket from the registry (called on disconnect/error)."""
        connections = self._active.get(ticket_id, [])
        if websocket in connections:
            connections.remove(websocket)

    async def broadcast_to_ticket(self, ticket_id: int, data: dict) -> None:
        """
        Send a JSON payload to every WebSocket subscribed to `ticket_id`.
        Stale connections are silently removed.
        """
        dead: list[WebSocket] = []
        for ws in list(self._active.get(ticket_id, [])):
            try:
                await ws.send_json(data)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws, ticket_id)


# Module-level singleton shared across the entire application
manager = ConnectionManager()
