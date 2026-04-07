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
  - [Channel Simulations](#channel-simulations)
  - [Routing](#routing)
  - [AI Engine](#ai-engine)
  - [Analytics](#analytics)
  - [Tags](#tags)
  - [WebSocket](#websocket)
- [Database](#database)
- [Interactive API Docs](#interactive-api-docs)

---

## Overview

The backend powers a multi-channel customer support platform where:

- **Customers** can contact support via email, web chat, WhatsApp, voice, social media (Facebook, Instagram, TikTok, LinkedIn), or Shopify.
- **Agents** manage and reply to support tickets in real time.
- **Tickets** track the full conversation history and lifecycle (`open` → `in_progress` → `closed`), with priority levels, SLA deadlines, tags, and categories.
- **Routing** assigns tickets to the best available agent using skill-based matching and workload balancing.
- **AI Engine** (keyword-based) suggests reply templates, classifies ticket categories, and recommends priority levels.
- **Analytics** endpoints provide KPI dashboards, SLA compliance reports, and volume breakdowns.
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
    │   ├── user.py              # Agent (User) model (skills, availability, department)
    │   ├── customer.py          # Customer model
    │   ├── ticket.py            # Ticket model + TicketStatus/ChannelType/TicketPriority enums
    │   ├── message.py           # Message model + SenderType enum
    │   └── tag.py               # Tag model + ticket_tags association table
    ├── schemas/                 # Pydantic request/response schemas
    │   ├── user.py, customer.py, ticket.py, message.py, tag.py, email.py
    ├── routes/
    │   ├── agents.py            # Agent CRUD, login, skills, availability
    │   ├── customers.py         # Customer endpoints
    │   ├── tickets.py           # Ticket CRUD, status, assign, tags
    │   ├── messages.py          # Message send & history endpoints
    │   ├── channels.py          # Channel simulation (WhatsApp, Social, Voice, Shopify, WebChat)
    │   ├── routing.py           # Queue view & skill-based auto-assignment
    │   ├── ai.py                # Suggest replies, classify, prioritize
    │   ├── analytics.py         # KPIs, SLA report, volume report
    │   ├── tags.py              # Tag list
    │   ├── email_simulation.py  # POST /simulate/email
    │   └── websocket.py         # WS /ws/tickets/{ticket_id}
    ├── services/                # Business logic layer
    │   ├── customer_service.py, ticket_service.py, user_service.py
    │   ├── message_service.py, email_service.py
    │   ├── tag_service.py, routing_service.py
    │   ├── ai_service.py, analytics_service.py
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
| `GET` | `/agents/` | List all agents |
| `GET` | `/agents/{agent_id}` | Retrieve a single agent by ID |
| `PUT` | `/agents/{agent_id}/skills` | Update agent skill tags |
| `PUT` | `/agents/{agent_id}/availability` | Set agent availability (`true`/`false`) |

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
| `POST` | `/tickets/{ticket_id}/tags` | Add a tag to a ticket (creates tag if needed) |
| `DELETE` | `/tickets/{ticket_id}/tags/{tag_id}` | Remove a tag from a ticket |

**Create ticket body:**

```json
{
  "customer_id": 1,
  "channel": "email",
  "subject": "Billing question",
  "priority": "high"
}
```

`channel`: `voice`, `whatsapp`, `facebook`, `instagram`, `tiktok`, `linkedin`, `shopify`, `webchat`, `email`  
`priority`: `low`, `medium`, `high`, `urgent`

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

### Channel Simulations

Simulate inbound messages from different communication platforms. Each endpoint creates the customer (if new), opens a ticket, and stores the first message.

| Method | Path | Description |
|---|---|---|
| `POST` | `/simulate/email` | Inbound customer email |
| `POST` | `/simulate/whatsapp` | Inbound WhatsApp message |
| `POST` | `/simulate/social` | Inbound social media message (Facebook/Instagram/TikTok/LinkedIn) |
| `POST` | `/simulate/voice` | Inbound voice call |
| `POST` | `/simulate/shopify` | Inbound Shopify order inquiry |
| `POST` | `/simulate/webchat` | Inbound web chat message |

**WhatsApp body:**
```json
{ "customer_name": "Ali", "customer_phone": "+1234567890", "message": "Hello, need help!" }
```

**Social body:**
```json
{ "platform": "facebook", "customer_handle": "ali.support", "message": "My order is late" }
```

**Voice body:**
```json
{ "customer_name": "Sara", "customer_phone": "+9876543210", "notes": "Customer called about a billing issue" }
```

**Shopify body:**
```json
{ "customer_name": "John", "customer_email": "john@store.com", "order_id": "ORD-999", "issue": "Item not delivered" }
```

**WebChat body:**
```json
{ "customer_name": "Nina", "customer_email": "nina@web.com", "message": "I need urgent help" }
```

---

### Routing

| Method | Path | Description |
|---|---|---|
| `GET` | `/routing/queue` | List open, unassigned tickets ordered by priority then age |
| `POST` | `/routing/auto-assign/{ticket_id}` | Auto-assign ticket to best available agent (skill-based) |

The auto-assign algorithm:
1. Finds all available agents (`is_available=true`).
2. Filters by agents whose `skills` include the ticket's channel or category.
3. Falls back to all available agents if none match.
4. Picks the agent with the fewest open/in-progress tickets.

---

### AI Engine

| Method | Path | Description |
|---|---|---|
| `GET` | `/ai/suggest-reply/{ticket_id}` | Return 3 canned reply suggestions based on ticket content |
| `POST` | `/ai/classify/{ticket_id}` | Classify priority & category from content, update ticket |
| `POST` | `/ai/prioritize/{ticket_id}` | Update only the priority based on content analysis |

**Suggest-reply response:**
```json
{
  "suggestions": [
    "Thank you for reaching out to our support team. We'll assist you shortly.",
    "Let me investigate this technical issue and provide you with a resolution.",
    "Is there any additional information you can provide to help us resolve this faster?"
  ]
}
```

---

### Analytics

| Method | Path | Description |
|---|---|---|
| `GET` | `/analytics/kpis` | KPI dashboard (totals, SLA rate, avg handle time, volume by channel/status) |
| `GET` | `/analytics/sla` | Per-ticket SLA compliance report |
| `GET` | `/analytics/volume` | Ticket volume by channel and by creation date |

---

### Tags

| Method | Path | Description |
|---|---|---|
| `GET` | `/tags/` | List all tags (alphabetical) |

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
