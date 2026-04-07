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

import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database.connection import DATABASE_URL
from database.init_db import init_models
from routes import agents, customers, email_simulation, messages, tickets, websocket
from routes import channels, routing, ai, analytics, tags as tags_router

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Lifespan – runs once at startup / shutdown
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create database tables before the first request is served."""
    try:
        await init_models()
    except Exception as exc:
        logger.error(
            "\n\n"
            "  ❌  Could not connect to the database on startup.\n"
            "      Error   : %s\n"
            "      URL     : %s\n\n"
            "  Make sure PostgreSQL is running and that DATABASE_URL is correct.\n"
            "  You can set it in backend/.env  (see .env.example).\n",
            exc,
            DATABASE_URL,
        )
        raise
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
# CORS – allow all origins in development; tighten in production by setting
# the CORS_ORIGINS environment variable to a comma-separated list of URLs.
# ---------------------------------------------------------------------------
_raw_origins = os.getenv("CORS_ORIGINS", "*")
_allow_all = _raw_origins.strip() == "*"
_origins = ["*"] if _allow_all else [o.strip() for o in _raw_origins.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=not _allow_all,
    allow_methods=["*"],
    allow_headers=["*"],
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
app.include_router(channels.router)
app.include_router(routing.router)
app.include_router(ai.router)
app.include_router(analytics.router)
app.include_router(tags_router.router)


# ---------------------------------------------------------------------------
# Health-check endpoint
# ---------------------------------------------------------------------------
@app.get("/", tags=["Health"])
async def root() -> dict:
    """Simple health-check – confirms the API is running."""
    return {"status": "ok", "message": "Omnichannel Support API is running."}
