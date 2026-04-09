# Omni-Channel Contact Center

A full-stack **Omni-Channel Contact Center** platform that enables seamless customer engagement via Email, Web Chat, WhatsApp, Voice, and Social Media. The project includes a scalable FastAPI backend with real-time WebSocket support, LLM-powered AI agents (OpenAI / LangChain / LangGraph), and a React + TypeScript frontend dashboard for agents.

---

## Table of Contents

- [Overview](#overview)
- [Tech Stack](#tech-stack)
  - [Backend](#backend-tech-stack)
  - [Frontend](#frontend-tech-stack)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Environment Variables](#environment-variables)
- [Local Setup](#local-setup)
  - [Backend Setup](#backend-setup)
  - [Frontend Setup](#frontend-setup)
- [Running the Application](#running-the-application)
- [Frontend Pages](#frontend-pages)
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
  - [AI Agents](#ai-agents)
  - [Analytics](#analytics)
  - [Tags](#tags)
  - [WebSocket](#websocket)
- [Database](#database)
- [Interactive API Docs](#interactive-api-docs)

---

## Overview

This platform provides a complete multi-channel customer support solution consisting of:

- A **FastAPI backend** powering the business logic, REST API, and real-time WebSocket messaging.
- A **React + TypeScript frontend** agent dashboard with routing, ticket management, simulation tools, and analytics.

Key capabilities:

- **Customers** can contact support via email, web chat, WhatsApp, voice, social media (Facebook, Instagram, TikTok, LinkedIn), or Shopify.
- **Agents** manage and reply to support tickets in real time through the dashboard UI or directly via the API.
- **Tickets** track the full conversation history and lifecycle (`open` → `in_progress` → `closed`), with priority levels, SLA deadlines, tags, and categories.
- **Routing** assigns tickets to the best available agent using skill-based matching and workload balancing.
- **AI Engine** powers smart reply suggestions, ticket classification, and priority recommendations — backed by LangChain + GPT-4 with a keyword-based fallback, and a LangGraph multi-step workflow for full ticket processing.
- **Analytics** endpoints provide KPI dashboards, SLA compliance reports, and volume breakdowns.
- **WebSocket** channels deliver instant message broadcasts to all connected clients watching a ticket.
- **Simulation endpoints** let you test inbound flows (email, WhatsApp, social, voice, Shopify, web chat) end-to-end without external services.

---

## Tech Stack

### Backend Tech Stack

| Layer | Technology |
|---|---|
| Web framework | [FastAPI](https://fastapi.tiangolo.com/) ≥ 0.111 |
| ASGI server | [Uvicorn](https://www.uvicorn.org/) (standard extras) |
| ORM | [SQLAlchemy](https://www.sqlalchemy.org/) ≥ 2.0 (async) |
| Database driver | [asyncpg](https://magicstack.github.io/asyncpg/) ≥ 0.29 |
| Database | PostgreSQL |
| Validation | [Pydantic](https://docs.pydantic.dev/) ≥ 2.0 |
| LLM SDK | [OpenAI Python](https://github.com/openai/openai-python) ≥ 1.3 |
| AI orchestration | [LangChain](https://python.langchain.com/) ≥ 0.1 + [LangGraph](https://langchain-ai.github.io/langgraph/) ≥ 0.1 |
| Vector database | [Pinecone](https://www.pinecone.io/) (optional; falls back to in-process FAISS) |
| Vector search (local) | [FAISS](https://faiss.ai/) CPU ≥ 1.7 + [NumPy](https://numpy.org/) ≥ 1.24 |
| Language | Python 3.11+ |

### Frontend Tech Stack

| Layer | Technology |
|---|---|
| UI framework | [React](https://react.dev/) 19 |
| Language | TypeScript |
| Build tool | [Vite](https://vitejs.dev/) |
| Routing | [React Router](https://reactrouter.com/) v7 |
| HTTP client | [Axios](https://axios-http.com/) |
| Styling | [Tailwind CSS](https://tailwindcss.com/) v3 |

---

## Project Structure

```
Omni-channel-repo/
├── backend/
│   ├── main.py                  # FastAPI app entry point
│   ├── requirements.txt
│   ├── .env.example
│   ├── database/
│   │   ├── connection.py        # Engine, session factory, Base, get_db
│   │   └── init_db.py           # Table creation on startup
│   ├── models/
│   │   ├── user.py              # Agent (User) model (skills, availability, department, AI config)
│   │   ├── customer.py          # Customer model
│   │   ├── ticket.py            # Ticket model + TicketStatus/ChannelType/TicketPriority enums
│   │   ├── message.py           # Message model + SenderType enum
│   │   ├── tag.py               # Tag model + ticket_tags association table
│   │   └── agent_knowledge.py   # AgentKnowledgeBase + AgentResponse (AI audit trail) models
│   ├── schemas/                 # Pydantic request/response schemas
│   │   ├── user.py, customer.py, ticket.py, message.py, tag.py, email.py
│   │   └── ai_agents.py         # AI agent creation, knowledge base, query, and response schemas
│   ├── routes/
│   │   ├── agents.py            # Agent CRUD, login, skills, availability
│   │   ├── customers.py         # Customer endpoints
│   │   ├── tickets.py           # Ticket CRUD, status, assign, tags
│   │   ├── messages.py          # Message send & history endpoints
│   │   ├── channels.py          # Channel simulation (WhatsApp, Social, Voice, Shopify, WebChat)
│   │   ├── routing.py           # Queue view & skill-based auto-assignment
│   │   ├── ai.py                # Keyword + LangChain + LangGraph AI endpoints
│   │   ├── ai_agents.py         # AI agent management & RAG query endpoints
│   │   ├── analytics.py         # KPIs, SLA report, volume report
│   │   ├── tags.py              # Tag list
│   │   ├── email_simulation.py  # POST /simulate/email
│   │   └── websocket.py         # WS /ws/tickets/{ticket_id}
│   ├── services/                # Business logic layer
│   │   ├── customer_service.py, ticket_service.py, user_service.py
│   │   ├── message_service.py, email_service.py
│   │   ├── tag_service.py, routing_service.py
│   │   ├── ai_service.py        # Keyword-based classification & reply suggestions (fallback)
│   │   ├── langchain_ai_service.py  # LangChain/GPT-4 smart classification & replies
│   │   ├── langgraph_workflow.py    # LangGraph 4-step ticket processing workflow
│   │   ├── ai_agent_service.py      # RAG-powered AI agent response generation
│   │   ├── embedding_service.py     # OpenAI embeddings + Pinecone/local similarity search
│   │   ├── rag_service.py           # FAISS-backed knowledge-base retrieval
│   │   └── analytics_service.py
│   └── utils/
│       └── connection_manager.py  # WebSocket connection manager
└── frontend/
    ├── index.html
    ├── package.json
    ├── vite.config.ts
    ├── tailwind.config.js
    ├── tsconfig.json
    └── src/
        ├── main.tsx             # React entry point
        ├── App.tsx              # Router & layout
        ├── api/                 # Axios API client & typed helpers
        │   ├── client.ts        # Axios instance (reads VITE_API_URL, error interceptor)
        │   ├── types.ts         # Shared TypeScript interfaces (mirror backend schemas)
        │   ├── tickets.ts       # Ticket & message endpoints
        │   ├── agents.ts        # Agent endpoints
        │   ├── customers.ts     # Customer endpoints
        │   ├── analytics.ts     # Analytics endpoints
        │   ├── ai.ts            # AI suggestion / classify endpoints
        │   ├── ai_agents.ts     # AI agent management & RAG query endpoints
        │   ├── routing.ts       # Routing queue & auto-assign endpoints
        │   ├── simulate.ts      # Channel simulation endpoints
        │   └── index.ts         # Re-exports all types and API functions
        ├── components/          # Shared UI components
        │   ├── Sidebar.tsx
        │   ├── StatusBadge.tsx
        │   └── PriorityBadge.tsx
        └── pages/               # Route-level page components
            ├── Dashboard.tsx
            ├── Tickets.tsx
            ├── TicketDetail.tsx
            ├── Agents.tsx
            ├── AIAgents.tsx
            ├── RoutingQueue.tsx
            └── Simulate.tsx
```

---

## Prerequisites

- **Python 3.11+**
- **Node.js 18+** and **npm**
- **PostgreSQL** (local or remote instance)
- `pip` (or a virtual-environment tool such as `venv` / `poetry`)

---

## Environment Variables

### Backend

| Variable | Required | Default | Description |
|---|---|---|---|
| `DATABASE_URL` | No | `postgresql+asyncpg://postgres:postgres@localhost:5432/omnichannel` | Full async connection URL |
| `DB_POOL_SIZE` | No | `5` | Persistent connections kept in the pool |
| `DB_MAX_OVERFLOW` | No | `10` | Extra connections allowed above pool size |
| `DB_ECHO` | No | `false` | Set to `true` to log every SQL statement (dev only) |
| `CORS_ORIGINS` | No | `*` | Allowed CORS origins. Use `*` for development or a comma-separated list of URLs for production |
| `OPENAI_API_KEY` | **Yes*** | — | OpenAI API key. Required for embeddings, LangChain chains, LangGraph workflow, and AI agent RAG |
| `OPENAI_MODEL` | No | `gpt-4` | OpenAI chat model used by LangChain and LangGraph (`gpt-4`, `gpt-4-turbo`, `gpt-3.5-turbo`) |
| `OPENAI_EMBEDDING_MODEL` | No | `text-embedding-3-small` | OpenAI model used to generate knowledge-base embeddings |
| `ANTHROPIC_API_KEY` | No | — | Optional Anthropic Claude API key (alternative LLM provider) |
| `PINECONE_API_KEY` | No | — | Pinecone API key. When set, embeddings are stored in Pinecone; otherwise in-process cosine search is used |
| `PINECONE_ENVIRONMENT` | No | `us-west1-gcp` | Pinecone environment/region |
| `PINECONE_INDEX` | No | `agent-knowledge` | Pinecone index name for knowledge-base vectors |

> **\* AI features are optional.** The core ticketing, routing, WebSocket, and analytics functionality works without any OpenAI credentials. The smart AI endpoints fall back to keyword-based logic automatically when `OPENAI_API_KEY` is absent.

Copy the provided template and fill in your values:

```bash
cp backend/.env.example backend/.env
# then edit backend/.env
```

### Frontend

| Variable | Required | Default | Description |
|---|---|---|---|
| `VITE_API_URL` | No | *(empty — uses Vite dev proxy)* | Full backend REST URL for production builds (e.g. `https://api.example.com`) |
| `VITE_WS_URL` | No | *(empty — uses Vite dev proxy)* | Full backend WebSocket URL for production builds (e.g. `wss://api.example.com`) |

In **development** leave both variables unset. The Vite dev-server proxy forwards:
- `/api/*` → `http://localhost:8000/*` (REST)
- `/ws/*` → `ws://localhost:8000/ws/*` (WebSocket)

In **production** set both to point to your deployed backend.

```bash
cp frontend/.env.example frontend/.env
# then edit frontend/.env
```

---

## Local Setup

### Backend Setup

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

### Frontend Setup

```bash
# From the repository root
cd frontend

# Install dependencies
npm install

# (Optional) Copy the environment template – only needed for production deployments
# cp .env.example .env
```

---

## Running the Application

**Backend** (from the `backend/` directory):

```bash
uvicorn main:app --reload
```

The API server starts at **http://127.0.0.1:8000**.  
Database tables are created automatically on first startup.

**Frontend** (from the `frontend/` directory):

```bash
# Development server (with hot-module reload)
npm run dev
```

The frontend dev server starts at **http://localhost:5173** and proxies API calls to the backend.

**Production build** (from the `frontend/` directory):

```bash
# Type-check and build static assets into frontend/dist/
npm run build

# Preview the production build locally
npm run preview
```

**Linting** (from the `frontend/` directory):

```bash
npm run lint
```

> **Tip:** For the frontend to communicate with the backend, ensure the backend is running and that `CORS_ORIGINS` in `backend/.env` includes `http://localhost:5173`.

---

## Common Errors

| Error | Cause | Fix |
|---|---|---|
| `❌ Could not connect to the database` / `Connection refused` | PostgreSQL is not running or `DATABASE_URL` is wrong | Start PostgreSQL and verify `DATABASE_URL` in `backend/.env` |
| `ModuleNotFoundError` on startup | Dependencies not installed | Run `pip install -r requirements.txt` inside the virtual environment |
| `CORS` errors in browser | Frontend origin not allowed | Set `CORS_ORIGINS=http://localhost:5173` (or your frontend URL) in `backend/.env` |
| `422 Unprocessable Entity` from the API | Request body does not match the expected schema | Check the `/docs` page for the correct payload shape |
| `RuntimeError: OPENAI_API_KEY environment variable is not set` | AI endpoint called without the key configured | Add `OPENAI_API_KEY=sk-...` to `backend/.env` |
| `503 Service Unavailable` from `/ai-agents/{id}/query` | OpenAI key missing or OpenAI is unreachable | Set `OPENAI_API_KEY`; AI reply/classify endpoints fall back to keyword logic automatically |
| `RuntimeError: langgraph is not installed` | LangGraph package missing from the environment | Run `pip install -r requirements.txt` inside the virtual environment |

---

## Frontend Pages

| Route | Page | Description |
|---|---|---|
| `/` | Dashboard | KPI overview: total tickets, open/closed counts, SLA compliance, volume by channel |
| `/tickets` | Tickets | Browse and filter all tickets with status and priority indicators |
| `/tickets/:id` | Ticket Detail | View full message history, send replies, update status, manage tags |
| `/agents` | Agents | List agents, register new agents, update skills and availability |
| `/ai-agents` | AI Agents | Create and manage LLM-powered AI agents, manage their knowledge base, query them, and view response audit trails |
| `/routing` | Routing Queue | View unassigned tickets ordered by priority; trigger auto-assignment |
| `/simulate` | Simulate | Send test inbound messages from any supported channel (email, WhatsApp, etc.) |

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

The AI engine has three operational modes, tried in order:

1. **LangChain + GPT-4** — full LLM-powered classification and contextual reply suggestions.
2. **LangGraph workflow** — a 4-node state machine (classify → decide_response → route_agent → human_review).
3. **Keyword-based fallback** — rule-based logic that always works without any API credentials.

The `powered_by` field in smart-endpoint responses indicates which mode was used (`langchain`, `langgraph`, or `keyword_fallback`).

#### Keyword / classic endpoints

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

#### Smart endpoints (LangChain / LangGraph — require `OPENAI_API_KEY`)

| Method | Path | Description |
|---|---|---|
| `GET` | `/ai/suggest-reply-smart/{ticket_id}` | LangChain + GPT-4 contextually relevant reply suggestions with recommended tone |
| `POST` | `/ai/classify-smart/{ticket_id}` | LLM-based classification: priority, category, department, and reasoning |
| `POST` | `/ai/process-with-workflow/{ticket_id}` | Run the full LangGraph 4-step workflow for a ticket |

**`/ai/classify-smart` response:**
```json
{
  "ticket_id": 1,
  "suggested_priority": "high",
  "suggested_category": "billing",
  "reasoning": "Customer mentions invoice and payment dispute.",
  "suggested_department": "billing_team",
  "powered_by": "langchain"
}
```

**`/ai/process-with-workflow` response:**
```json
{
  "ticket_id": 1,
  "priority": "high",
  "category": "billing",
  "department": "billing_team",
  "requires_human_review": true,
  "auto_respond": false,
  "suggested_response": "",
  "routing_reason": "ESCALATED: Route to Billing Team – payment/invoice expertise needed",
  "workflow_steps": ["classify", "decide_response", "route_agent", "human_review"],
  "powered_by": "langgraph"
}
```

---

### AI Agents

Manage LLM-powered support agents that are backed by a per-agent knowledge base (RAG). Requires `OPENAI_API_KEY`.

| Method | Path | Description |
|---|---|---|
| `POST` | `/ai-agents/` | Create a new AI-powered agent |
| `POST` | `/ai-agents/{agent_id}/knowledge` | Add a knowledge document to the agent's knowledge base |
| `GET` | `/ai-agents/{agent_id}/knowledge` | List all knowledge documents for an agent |
| `POST` | `/ai-agents/{agent_id}/query` | Query the agent; retrieves relevant context via RAG then calls the LLM |
| `GET` | `/ai-agents/{agent_id}/responses` | View the audit trail of AI-generated responses for an agent |

**Create AI agent body:**
```json
{
  "name": "Support Bot",
  "email": "bot@example.com",
  "department": "support",
  "skills": ["billing", "technical"],
  "ai_model": "gpt-3.5-turbo",
  "ai_config": {
    "temperature": 0.7,
    "max_tokens": 500,
    "system_prompt": "You are a helpful support agent."
  },
  "knowledge_base_enabled": true,
  "auto_respond": false,
  "confidence_threshold": 0.7
}
```

**Query body:**
```json
{ "query": "How do I get a refund?", "ticket_id": 42, "use_knowledge_base": true }
```

**Query response:**
```json
{
  "response": "Refunds are processed within 3-5 business days. [Source 1: Billing FAQ]",
  "confidence_score": 0.87,
  "sources": [
    { "id": 1, "title": "Billing FAQ", "category": "billing", "score": 0.87 }
  ],
  "requires_human_review": false
}
```

When `confidence_score` falls below the agent's `confidence_threshold`, `requires_human_review` is set to `true` and the response is saved with `human_review_status: "pending"` in the audit trail.

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
