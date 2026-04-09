"""
schemas/ai_agents.py
--------------------
Pydantic schemas for the AI-agent management endpoints.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, EmailStr


# ---------------------------------------------------------------------------
# Knowledge base
# ---------------------------------------------------------------------------

class KnowledgeBaseCreate(BaseModel):
    """Payload for adding a knowledge document to an agent."""
    title: str
    content: str
    category: str = "General"


class KnowledgeBaseOut(BaseModel):
    """Knowledge document as returned to the client."""
    id: int
    agent_id: int
    title: str
    content: str
    category: Optional[str] = None
    embedding_model: Optional[str] = None
    created_at: str  # ISO-8601

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Query / response
# ---------------------------------------------------------------------------

class AIQueryRequest(BaseModel):
    """Request body for querying an AI agent."""
    query: str
    ticket_id: Optional[int] = None
    use_knowledge_base: bool = True


class AISourceSchema(BaseModel):
    """A single source document returned alongside an AI response."""
    id: int
    title: str
    category: Optional[str]
    score: float  # cosine-similarity score (0-1)


class AIResponseSchema(BaseModel):
    """Full response returned from the AI agent."""
    response: str
    confidence_score: float
    sources: List[AISourceSchema]
    requires_human_review: bool


# ---------------------------------------------------------------------------
# Agent creation
# ---------------------------------------------------------------------------

class CreateAIAgent(BaseModel):
    """Payload for creating a new AI-powered agent."""
    name: str
    email: EmailStr
    department: str = "support"
    skills: List[str] = []
    ai_model: str = "gpt-3.5-turbo"
    ai_config: Dict[str, Any] = {
        "temperature": 0.7,
        "max_tokens": 500,
        "system_prompt": "You are a helpful support agent.",
    }
    knowledge_base_enabled: bool = True
    auto_respond: bool = False
    confidence_threshold: float = 0.7


class AIAgentOut(BaseModel):
    """AI agent record as returned to the client."""
    id: int
    name: str
    email: str
    department: Optional[str] = None
    skills: List[str] = []
    is_available: bool
    is_ai_agent: bool
    ai_model: Optional[str] = None
    knowledge_base_enabled: bool
    auto_respond: bool
    confidence_threshold: float

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Audit-trail responses
# ---------------------------------------------------------------------------

class AgentResponseOut(BaseModel):
    """Stored AI response as returned to the client."""
    id: int
    agent_id: int
    ticket_id: int
    customer_query: str
    ai_response: str
    confidence_score: Optional[float]
    sources_used: Optional[str]
    human_review_status: str
    created_at: str

    model_config = {"from_attributes": True}
