"""
services/ai_agent_service.py
-----------------------------
RAG (Retrieval-Augmented Generation) service that orchestrates:
  1. Vector search over an agent's knowledge base.
  2. LLM call (OpenAI) with retrieved context injected into the system prompt.
  3. Persistence of the response for audit/compliance.

Optional external dependencies
-------------------------------
``openai`` is required for live LLM calls. When it is absent (e.g. CI / unit
tests), the service raises a clear ``RuntimeError`` rather than crashing at
import time.
"""
from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.agent_knowledge import AgentKnowledgeBase, AgentResponse
from models.user import User
from schemas.ai_agents import AIResponseSchema, AISourceSchema
from services.embedding_service import embedding_service

try:
    from openai import AsyncOpenAI  # type: ignore
    _openai_available = True
except ImportError:  # pragma: no cover
    _openai_available = False


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_openai_client() -> Any:
    if not _openai_available:
        raise RuntimeError(
            "openai package is not installed. "
            "Add 'openai>=1.3.0' to requirements.txt."
        )
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY environment variable is not set.")
    return AsyncOpenAI(api_key=api_key)


# ---------------------------------------------------------------------------
# Service class
# ---------------------------------------------------------------------------

class AIAgentService:
    """LLM-powered support agent backed by a vector knowledge base."""

    # ------------------------------------------------------------------
    # Agent config retrieval
    # ------------------------------------------------------------------

    async def _get_agent(self, db: AsyncSession, agent_id: int) -> User:
        result = await db.execute(
            select(User).where(User.id == agent_id, User.is_ai_agent.is_(True))
        )
        agent = result.scalars().first()
        if agent is None:
            raise ValueError(f"AI agent with id={agent_id} not found.")
        return agent

    def _build_config(self, agent: User) -> Dict[str, Any]:
        cfg = agent.ai_config or {}
        return {
            "model": agent.ai_model or "gpt-3.5-turbo",
            "temperature": cfg.get("temperature", 0.7),
            "max_tokens": int(cfg.get("max_tokens", 500)),
            "system_prompt": cfg.get("system_prompt", "You are a helpful support agent."),
        }

    # ------------------------------------------------------------------
    # Knowledge base retrieval (vector search)
    # ------------------------------------------------------------------

    async def _retrieve_context(
        self,
        db: AsyncSession,
        query: str,
        agent_id: int,
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Search the agent's knowledge base for entries relevant to *query*.

        Tries Pinecone first; falls back to in-process cosine similarity when
        Pinecone is not configured.
        """
        query_embedding = await embedding_service.generate_embedding(query)

        # --- Pinecone path ---
        pinecone_hits = await embedding_service.search_similar_pinecone(
            query_embedding, agent_id, top_k
        )
        if pinecone_hits:
            # Enrich with DB data (title / category)
            ids = [int(h["id"].split("_kb_")[-1]) for h in pinecone_hits]
            result = await db.execute(
                select(AgentKnowledgeBase).where(AgentKnowledgeBase.id.in_(ids))
            )
            kb_map = {row.id: row for row in result.scalars().all()}
            enriched = []
            for hit in pinecone_hits:
                kb_id = int(hit["id"].split("_kb_")[-1])
                row = kb_map.get(kb_id)
                enriched.append(
                    {
                        "id": kb_id,
                        "title": row.title if row else hit["metadata"].get("title", ""),
                        "category": row.category if row else hit["metadata"].get("category"),
                        "score": hit["score"],
                        "content": row.content if row else hit["metadata"].get("content", ""),
                    }
                )
            return enriched

        # --- Local fallback ---
        result = await db.execute(
            select(AgentKnowledgeBase).where(
                AgentKnowledgeBase.agent_id == agent_id,
                AgentKnowledgeBase.embedding.is_not(None),
            )
        )
        rows = result.scalars().all()
        hits = embedding_service.search_similar_local(query_embedding, rows, top_k)
        # Attach content
        row_map = {r.id: r for r in rows}
        for h in hits:
            row = row_map.get(h["id"])
            h["content"] = row.content if row else ""
        return hits

    # ------------------------------------------------------------------
    # LLM response generation
    # ------------------------------------------------------------------

    async def generate_response(
        self,
        db: AsyncSession,
        agent_id: int,
        customer_query: str,
        ticket_id: Optional[int] = None,
        use_knowledge_base: bool = True,
    ) -> AIResponseSchema:
        """
        Generate a contextual LLM response for *customer_query*.

        Steps:
          1. Fetch agent config.
          2. Optionally retrieve relevant knowledge-base excerpts.
          3. Call the OpenAI chat-completions API.
          4. Persist the result as an :class:`~models.agent_knowledge.AgentResponse`.
          5. Return a structured :class:`~schemas.ai_agents.AIResponseSchema`.
        """
        agent = await self._get_agent(db, agent_id)
        cfg = self._build_config(agent)

        # --- Retrieve context ---
        context_docs: List[Dict[str, Any]] = []
        if use_knowledge_base and agent.knowledge_base_enabled:
            context_docs = await self._retrieve_context(db, customer_query, agent_id)

        # --- Build system prompt ---
        system_prompt = cfg["system_prompt"]
        if context_docs:
            excerpts = "\n\n".join(
                f"[Source {i + 1}: {doc['title']}]\n{doc['content']}"
                for i, doc in enumerate(context_docs)
            )
            system_prompt = (
                f"{system_prompt}\n\n"
                "Use the following knowledge-base excerpts to answer the customer. "
                "Cite the source numbers where relevant.\n\n"
                f"{excerpts}"
            )

        # --- Call LLM ---
        client = _get_openai_client()
        completion = await client.chat.completions.create(
            model=cfg["model"],
            temperature=cfg["temperature"],
            max_tokens=cfg["max_tokens"],
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": customer_query},
            ],
        )
        ai_response_text = completion.choices[0].message.content or ""

        # --- Confidence heuristic ---
        # Score is the average similarity of retrieved docs (or a low default).
        if context_docs:
            confidence = min(
                sum(d["score"] for d in context_docs) / len(context_docs), 1.0
            )
        else:
            confidence = 0.3

        # --- Persist audit record ---
        if ticket_id is not None:
            source_ids = [d["id"] for d in context_docs]
            db_record = AgentResponse(
                agent_id=agent_id,
                ticket_id=ticket_id,
                customer_query=customer_query,
                ai_response=ai_response_text,
                confidence_score=confidence,
                sources_used=json.dumps(source_ids),
                human_review_status="pending"
                if confidence < agent.confidence_threshold
                else "approved",
            )
            db.add(db_record)
            await db.flush()

        sources = [
            AISourceSchema(
                id=d["id"],
                title=d["title"],
                category=d.get("category"),
                score=round(d["score"], 4),
            )
            for d in context_docs
        ]

        return AIResponseSchema(
            response=ai_response_text,
            confidence_score=round(confidence, 4),
            sources=sources,
            requires_human_review=confidence < agent.confidence_threshold,
        )

    # ------------------------------------------------------------------
    # Knowledge base management
    # ------------------------------------------------------------------

    async def add_knowledge(
        self,
        db: AsyncSession,
        agent_id: int,
        title: str,
        content: str,
        category: str = "General",
    ) -> AgentKnowledgeBase:
        """
        Persist a new knowledge document and generate + store its embedding.
        """
        # Generate embedding
        embedding_vec = await embedding_service.generate_embedding(content)
        embedding_bytes = embedding_service.embedding_to_bytes(embedding_vec)

        kb_entry = AgentKnowledgeBase(
            agent_id=agent_id,
            title=title,
            content=content,
            category=category,
            embedding=embedding_bytes,
            embedding_model=embedding_service.EMBEDDING_MODEL,
        )
        db.add(kb_entry)
        await db.flush()
        await db.refresh(kb_entry)

        # Also push to Pinecone (no-op when not configured)
        await embedding_service.store_in_pinecone(
            doc_id=f"agent_{agent_id}_kb_{kb_entry.id}",
            embedding=embedding_vec,
            metadata={
                "agent_id": agent_id,
                "kb_id": kb_entry.id,
                "title": title,
                "category": category,
                "content": content[:500],  # keep metadata payload small
            },
        )

        return kb_entry

    async def list_knowledge(
        self,
        db: AsyncSession,
        agent_id: int,
    ) -> List[AgentKnowledgeBase]:
        """Return all knowledge documents for an agent."""
        result = await db.execute(
            select(AgentKnowledgeBase)
            .where(AgentKnowledgeBase.agent_id == agent_id)
            .order_by(AgentKnowledgeBase.created_at.desc())
        )
        return list(result.scalars().all())

    async def list_responses(
        self,
        db: AsyncSession,
        agent_id: int,
    ) -> List[AgentResponse]:
        """Return the audit trail of AI responses for an agent."""
        result = await db.execute(
            select(AgentResponse)
            .where(AgentResponse.agent_id == agent_id)
            .order_by(AgentResponse.created_at.desc())
        )
        return list(result.scalars().all())


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------
ai_agent_service = AIAgentService()
