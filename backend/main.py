"""
main.py
-------
FastAPI application entry point.

Start the server with:
    uvicorn main:app --reload

The app:
  - Initialises the database schema on startup
  - Registers all route groups (agents, customers, tickets, messages,
    WebSocket, email simulation)
  - Exposes interactive API docs at /docs
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from database.init_db import init_models
from routes import agents, customers, email_simulation, messages, tickets, websocket


# ---------------------------------------------------------------------------
# Lifespan – runs once at startup / shutdown
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create database tables before the first request is served."""
    await init_models()
    yield


# ---------------------------------------------------------------------------
# Application instance
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Omnichannel Customer Support API",
    description=(
        "Backend for a scalable omnichannel support system. "
        "Customers contact support via email or webchat; "
        "agents manage and reply to tickets in real time."
    ),
    version="1.0.0",
    lifespan=lifespan,
)


# ---------------------------------------------------------------------------
# Register routers
# ---------------------------------------------------------------------------
app.include_router(agents.router)
app.include_router(customers.router)
app.include_router(tickets.router)
app.include_router(messages.router)
app.include_router(websocket.router)
app.include_router(email_simulation.router)


# ---------------------------------------------------------------------------
# Health-check endpoint
# ---------------------------------------------------------------------------
@app.get("/", tags=["Health"])
async def root() -> dict:
    """Simple health-check – confirms the API is running."""
    return {"status": "ok", "message": "Omnichannel Support API is running."}
