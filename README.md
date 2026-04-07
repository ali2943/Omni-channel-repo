# Omni-Channel Contact Center

A scalable **Omni-Channel Contact Center** backend that enables seamless customer engagement via Email and Web Chat, with integrated Ticket Management, real-time messaging over WebSocket, and AI-readiness.

---

## Table of Contents

- [Overview](#overview)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Environment Variables](#environment-variables)
- [Local Setup](#local-setup)
- [Running the Server](#running-the-server)
- [API Reference](#api-reference)
  - [Health Check](#health-check)
  - [Agents](#agents)
  - [Customers](#customers)
  - [Tickets](#tickets)
  - [Messages](#messages)
  - [Email Simulation](#email-simulation)
  - [WebSocket](#websocket)
- [Database](#database)
- [Interactive API Docs](#interactive-api-docs)

---

## Overview

The backend powers a multi-channel customer support platform where:

- **Customers** can contact support via email or web chat.
- **Agents** manage and reply to support tickets in real time.
- **Tickets** track the full conversation history and lifecycle (`open` → `in_progress` → `closed`).
- **WebSocket** channels deliver instant message broadcasts to all connected clients watching a ticket.
- An **email simulation endpoint** lets you test the inbound email flow end-to-end without an external mail server.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Web framework | [FastAPI](https://fastapi.tiangolo.com/) ≥ 0.111 |
| ASGI server | [Uvicorn](https://www.uvicorn.org/) (standard extras) |
| ORM | [SQLAlchemy](https://www.sqlalchemy.org/) ≥ 2.0 (async) |
| Database driver | [asyncpg](https://magicstack.github.io/asyncpg/) ≥ 0.29 |
| Database | PostgreSQL |
| Validation | [Pydantic](https://docs.pydantic.dev/) ≥ 2.0 |
| Language | Python 3.11+ |

---

## Project Structure

```
Omni-channel-repo/
└── backend/
    ├── main.py                  # FastAPI app entry point
    ├── requirements.txt
    ├── database/
    │   ├── connection.py        # Engine, session factory, Base, get_db
    │   └── init_db.py           # Table creation on startup
    ├── models/
    │   ├── user.py              # Agent (User) model
    │   ├── customer.py          # Customer model
    │   ├── ticket.py            # Ticket model + TicketStatus enum
    │   └── message.py           # Message model + SenderType enum
    ├── schemas/                 # Pydantic request/response schemas
    ├── routes/
    │   ├── agents.py            # POST /agents, POST /agents/login, GET /agents/{id}
    │   ├── customers.py         # Customer endpoints
    │   ├── tickets.py           # Ticket CRUD & status/assign endpoints
    │   ├── messages.py          # Message send & history endpoints
    │   ├── email_simulation.py  # POST /simulate/email
    │   └── websocket.py         # WS /ws/tickets/{ticket_id}
    ├── services/                # Business logic layer
    └── utils/
        └── connection_manager.py  # WebSocket connection manager
```

---

## Prerequisites

- **Python 3.11+**
- **PostgreSQL** (local or remote instance)
- `pip` (or a virtual-environment tool such as `venv` / `poetry`)

---

## Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `DATABASE_URL` | No | `postgresql+asyncpg://postgres:postgres@localhost:5432/omnichannel` | Full async connection URL |
| `DB_POOL_SIZE` | No | `5` | Persistent connections kept in the pool |
| `DB_MAX_OVERFLOW` | No | `10` | Extra connections allowed above pool size |
| `DB_ECHO` | No | `false` | Set to `true` to log every SQL statement (dev only) |
| `CORS_ORIGINS` | No | `*` | Allowed CORS origins. Use `*` for development or a comma-separated list of URLs for production |

Copy the provided template and fill in your values:

```bash
cp backend/.env.example backend/.env
# then edit backend/.env
```

---

## Local Setup

```bash
# 1. Clone the repository
git clone https://github.com/ali2943/Omni-channel-repo.git
cd Omni-channel-repo/backend

# 2. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Copy and configure the environment file
cp .env.example .env
# Edit .env with your PostgreSQL credentials

# 5. Create the PostgreSQL database
psql -U postgres -c "CREATE DATABASE omnichannel;"
```

---

## Running the Server

```bash
# From the backend/ directory
uvicorn main:app --reload
```

The server starts at **http://127.0.0.1:8000**.  
Database tables are created automatically on first startup.

---

## Common Errors

| Error | Cause | Fix |
|---|---|---|
| `❌ Could not connect to the database` / `Connection refused` | PostgreSQL is not running or `DATABASE_URL` is wrong | Start PostgreSQL and verify `DATABASE_URL` in `backend/.env` |
| `ModuleNotFoundError` on startup | Dependencies not installed | Run `pip install -r requirements.txt` inside the virtual environment |
| `CORS` errors in browser | Frontend origin not allowed | Set `CORS_ORIGINS=http://localhost:3000` (or your frontend URL) in `backend/.env` |
| `422 Unprocessable Entity` from the API | Request body does not match the expected schema | Check the `/docs` page for the correct payload shape |

---

## API Reference

### Health Check

| Method | Path | Description |
|---|---|---|
| `GET` | `/` | Returns `{"status": "ok"}` |

---

### Agents

| Method | Path | Description |
|---|---|---|
| `POST` | `/agents/` | Register a new support agent |
| `POST` | `/agents/login` | Email-based login; returns agent details |
| `GET` | `/agents/{agent_id}` | Retrieve a single agent by ID |

---

### Customers

| Method | Path | Description |
|---|---|---|
| `POST` | `/customers/` | Create a new customer |
| `GET` | `/customers/{customer_id}` | Retrieve a customer by ID |

---

### Tickets

| Method | Path | Description |
|---|---|---|
| `POST` | `/tickets/` | Open a new support ticket |
| `GET` | `/tickets/` | List all tickets (newest first) |
| `GET` | `/tickets/{ticket_id}` | Get ticket details with full message history |
| `PUT` | `/tickets/{ticket_id}/assign` | Assign ticket to an agent |
| `PUT` | `/tickets/{ticket_id}/status` | Update ticket status (`open` / `in_progress` / `closed`) |

---

### Messages

| Method | Path | Description |
|---|---|---|
| `POST` | `/tickets/{ticket_id}/messages` | Send a message; also broadcasts via WebSocket |
| `GET` | `/tickets/{ticket_id}/messages` | Retrieve full message history for a ticket |

---

### Email Simulation

| Method | Path | Description |
|---|---|---|
| `POST` | `/simulate/email` | Simulate an inbound customer email (creates customer + ticket + first message) |

**Request body:**

```json
{
  "customer_name": "Jane Doe",
  "customer_email": "jane@example.com",
  "subject": "Order issue",
  "body": "Hi, I have a problem with my order #1234."
}
```

---

### WebSocket

| Protocol | Path | Description |
|---|---|---|
| `WS` | `/ws/tickets/{ticket_id}` | Real-time message channel for a ticket |

**Connect** to `ws://localhost:8000/ws/tickets/{ticket_id}` and send JSON:

```json
{
  "sender_type": "agent",
  "content": "Hello, how can I help you?"
}
```

`sender_type` must be `"agent"` or `"customer"`.  
Every message is persisted and broadcast to **all connected clients** on that ticket channel.

---

## Database

The database layer uses **async SQLAlchemy 2.0** with `asyncpg` as the PostgreSQL driver.

Key components in `database/connection.py`:

| Component | Description |
|---|---|
| `engine` | Async connection pool (`pool_size`, `max_overflow`, `pool_pre_ping`) |
| `AsyncSessionLocal` | Session factory (`autocommit=False`, `autoflush=False`, `expire_on_commit=False`) |
| `Base` | `DeclarativeBase` — all models inherit from this |
| `get_db()` | FastAPI dependency that yields a session and auto-commits/rolls back |
| `get_db_context()` | Async context manager for use outside FastAPI DI (e.g., WebSocket handlers) |

Tables are created automatically via `init_db.py` at application startup.

---

## Interactive API Docs

FastAPI provides built-in documentation UIs once the server is running:

- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc
