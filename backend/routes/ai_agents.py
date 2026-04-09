"""
routes/ai_agents.py
-------------------
HTTP endpoints for AI-agent management.

POST /ai-agents/                     – create a new AI agent
POST /ai-agents/{agent_id}/knowledge – add a knowledge document
GET  /ai-agents/{agent_id}/knowledge – list knowledge documents
POST /ai-agents/{agent_id}/query     – query the AI agent
GET  /ai-agents/{agent_id}/responses – view AI response audit trail
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db
from schemas.ai_agents import (
    AIAgentOut,
    AgentResponseOut,
    AIQueryRequest,
    AIResponseSchema,
    CreateAIAgent,
    KnowledgeBaseCreate,
    KnowledgeBaseOut,
)
from services import user_service
from services.ai_agent_service import ai_agent_service

router = APIRouter(prefix="/ai-agents", tags=["AI Agents"])


# ---------------------------------------------------------------------------
# Create AI agent
# ---------------------------------------------------------------------------

@router.post("/", response_model=AIAgentOut, status_code=status.HTTP_201_CREATED)
async def create_ai_agent(
    payload: CreateAIAgent,
    db: AsyncSession = Depends(get_db),
) -> AIAgentOut:
    """Register a new AI-powered support agent."""
    existing = await user_service.get_agent_by_email(db, payload.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An agent with this email already exists.",
        )
    agent = await user_service.create_ai_agent(db, payload)
    return agent


# ---------------------------------------------------------------------------
# Knowledge base endpoints
# ---------------------------------------------------------------------------

@router.post(
    "/{agent_id}/knowledge",
    response_model=KnowledgeBaseOut,
    status_code=status.HTTP_201_CREATED,
)
async def add_knowledge_document(
    agent_id: int,
    payload: KnowledgeBaseCreate,
    db: AsyncSession = Depends(get_db),
) -> KnowledgeBaseOut:
    """Add a knowledge document to an AI agent's knowledge base."""
    agent = await user_service.get_agent_by_id(db, agent_id)
    if agent is None or not agent.is_ai_agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="AI agent not found.",
        )
    kb_entry = await ai_agent_service.add_knowledge(
        db,
        agent_id=agent_id,
        title=payload.title,
        content=payload.content,
        category=payload.category,
    )
    return KnowledgeBaseOut(
        id=kb_entry.id,
        agent_id=kb_entry.agent_id,
        title=kb_entry.title,
        content=kb_entry.content,
        category=kb_entry.category,
        embedding_model=kb_entry.embedding_model,
        created_at=kb_entry.created_at.isoformat(),
    )


@router.get("/{agent_id}/knowledge", response_model=list[KnowledgeBaseOut])
async def list_knowledge_documents(
    agent_id: int,
    db: AsyncSession = Depends(get_db),
) -> list[KnowledgeBaseOut]:
    """List all knowledge documents for an AI agent."""
    agent = await user_service.get_agent_by_id(db, agent_id)
    if agent is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found.",
        )
    rows = await ai_agent_service.list_knowledge(db, agent_id)
    return [
        KnowledgeBaseOut(
            id=r.id,
            agent_id=r.agent_id,
            title=r.title,
            content=r.content,
            category=r.category,
            embedding_model=r.embedding_model,
            created_at=r.created_at.isoformat(),
        )
        for r in rows
    ]


# ---------------------------------------------------------------------------
# Query AI agent (RAG)
# ---------------------------------------------------------------------------

@router.post("/{agent_id}/query", response_model=AIResponseSchema)
async def query_ai_agent(
    agent_id: int,
    payload: AIQueryRequest,
    db: AsyncSession = Depends(get_db),
) -> AIResponseSchema:
    """
    Query an AI agent.

    The agent retrieves relevant knowledge-base context, sends it to the
    configured LLM, and returns a structured response with confidence score
    and source citations.
    """
    agent = await user_service.get_agent_by_id(db, agent_id)
    if agent is None or not agent.is_ai_agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="AI agent not found.",
        )
    try:
        response = await ai_agent_service.generate_response(
            db=db,
            agent_id=agent_id,
            customer_query=payload.query,
            ticket_id=payload.ticket_id,
            use_knowledge_base=payload.use_knowledge_base,
        )
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    return response


# ---------------------------------------------------------------------------
# Audit trail
# ---------------------------------------------------------------------------

@router.get("/{agent_id}/responses", response_model=list[AgentResponseOut])
async def list_ai_responses(
    agent_id: int,
    db: AsyncSession = Depends(get_db),
) -> list[AgentResponseOut]:
    """Return the audit trail of AI-generated responses for an agent."""
    agent = await user_service.get_agent_by_id(db, agent_id)
    if agent is None or not agent.is_ai_agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="AI agent not found.",
        )
    rows = await ai_agent_service.list_responses(db, agent_id)
    return [
        AgentResponseOut(
            id=r.id,
            agent_id=r.agent_id,
            ticket_id=r.ticket_id,
            customer_query=r.customer_query,
            ai_response=r.ai_response,
            confidence_score=r.confidence_score,
            sources_used=r.sources_used,
            human_review_status=r.human_review_status,
            created_at=r.created_at.isoformat(),
        )
        for r in rows
    ]
