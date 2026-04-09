"""
services/langchain_ai_service.py
---------------------------------
LangChain-powered AI service for intelligent ticket classification and
smart reply suggestions using GPT-4 (or any OpenAI-compatible model).

Falls back gracefully to keyword-based logic when LangChain / OpenAI is
not available or when API calls fail.
"""
from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# ---------------------------------------------------------------------------
# Optional LangChain imports – service degrades gracefully when absent
# ---------------------------------------------------------------------------
try:
    from langchain_openai import ChatOpenAI  # type: ignore
    from langchain_core.prompts import ChatPromptTemplate  # type: ignore
    from langchain_core.output_parsers import PydanticOutputParser  # type: ignore
    _langchain_available = True
except ImportError:  # pragma: no cover
    _langchain_available = False


# ---------------------------------------------------------------------------
# Pydantic output models used by LangChain parsers
# ---------------------------------------------------------------------------

class TicketClassification(BaseModel):
    """Structured LLM output for ticket classification."""

    priority: str = Field(
        description="Ticket priority level: low, medium, high, or urgent"
    )
    category: str = Field(
        description="Ticket category: billing, technical, shipping, or general"
    )
    reasoning: str = Field(
        description="Brief explanation justifying the classification"
    )
    suggested_department: str = Field(
        description=(
            "Department best suited to handle this ticket: "
            "billing_team, technical_support, logistics, or general_support"
        )
    )


class SmartReplySuggestion(BaseModel):
    """Structured LLM output for reply suggestions."""

    suggestions: List[str] = Field(
        description="List of exactly 3 contextually relevant reply suggestions"
    )
    tone: str = Field(
        description=(
            "Recommended communication tone for this ticket: "
            "formal, empathetic, or technical"
        )
    )


# ---------------------------------------------------------------------------
# LangChain AI Service
# ---------------------------------------------------------------------------

class LangChainAIService:
    """
    Intelligent AI service using LangChain chains for ticket classification
    and smart reply suggestions.

    When LangChain or OpenAI is unavailable, every public method falls back
    to the existing keyword-based ``ai_service`` helpers so that the API
    remains fully functional without LLM credentials.
    """

    def __init__(self) -> None:
        self._llm: Optional[Any] = None

    # ------------------------------------------------------------------
    # Lazy LLM initialisation
    # ------------------------------------------------------------------

    def _get_llm(self) -> Any:
        if self._llm is not None:
            return self._llm
        if not _langchain_available:
            raise RuntimeError(
                "langchain-openai is not installed. "
                "Add 'langchain-openai>=0.1.0' to requirements.txt."
            )
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY environment variable is not set.")
        model = os.getenv("OPENAI_MODEL", "gpt-4")
        self._llm = ChatOpenAI(
            model=model,
            temperature=0.3,
            api_key=api_key,
        )
        return self._llm

    # ------------------------------------------------------------------
    # Classification chain
    # ------------------------------------------------------------------

    async def classify_ticket_smart(
        self, db: AsyncSession, ticket_id: int
    ) -> Dict[str, Any]:
        """
        Classify a ticket using LangChain + GPT-4.

        Returns a dict with keys: ticket_id, suggested_priority,
        suggested_category, reasoning, suggested_department, powered_by.
        Falls back to keyword-based classification on any error.
        """
        from models.message import Message
        from models.ticket import Ticket
        from services import ai_service

        result = await db.execute(select(Ticket).where(Ticket.id == ticket_id))
        ticket = result.scalars().first()
        if ticket is None:
            return {"ticket_id": ticket_id, "error": "Ticket not found"}

        msg_result = await db.execute(
            select(Message)
            .where(Message.ticket_id == ticket_id)
            .order_by(Message.timestamp.asc())
            .limit(1)
        )
        first_msg = msg_result.scalars().first()
        content = first_msg.content if first_msg else (ticket.subject or "")
        channel_str = ticket.channel.value if ticket.channel else "unknown"

        try:
            llm = self._get_llm()
            parser = PydanticOutputParser(pydantic_object=TicketClassification)
            prompt = ChatPromptTemplate.from_messages(
                [
                    (
                        "system",
                        "You are an expert customer support ticket classifier. "
                        "Analyse the incoming support ticket and classify it accurately.\n"
                        "{format_instructions}",
                    ),
                    (
                        "human",
                        "Classify this support ticket:\n"
                        "Channel: {channel}\n"
                        "Content: {content}",
                    ),
                ]
            ).partial(format_instructions=parser.get_format_instructions())

            chain = prompt | llm | parser
            classification: TicketClassification = await chain.ainvoke(
                {"channel": channel_str, "content": content}
            )

            return {
                "ticket_id": ticket_id,
                "suggested_priority": classification.priority,
                "suggested_category": classification.category,
                "reasoning": classification.reasoning,
                "suggested_department": classification.suggested_department,
                "powered_by": "langchain",
            }

        except Exception:
            fallback = await ai_service.classify_ticket(db, ticket_id)
            fallback["powered_by"] = "keyword_fallback"
            return fallback

    # ------------------------------------------------------------------
    # Smart reply chain
    # ------------------------------------------------------------------

    async def suggest_replies_smart(
        self, db: AsyncSession, ticket_id: int
    ) -> Dict[str, Any]:
        """
        Generate contextually relevant reply suggestions using LangChain.

        Returns a dict with keys: ticket_id, suggestions (list[str]),
        tone, powered_by.
        Falls back to canned replies on any error.
        """
        from models.message import Message
        from models.ticket import Ticket
        from services import ai_service

        result = await db.execute(select(Ticket).where(Ticket.id == ticket_id))
        ticket = result.scalars().first()
        if ticket is None:
            return {"ticket_id": ticket_id, "error": "Ticket not found"}

        msg_result = await db.execute(
            select(Message)
            .where(Message.ticket_id == ticket_id)
            .order_by(Message.timestamp.asc())
            .limit(3)
        )
        messages_list = msg_result.scalars().all()
        content = messages_list[0].content if messages_list else (ticket.subject or "")
        channel_str = ticket.channel.value if ticket.channel else "unknown"

        conversation_history = (
            "\n".join(f"[{m.sender_type}]: {m.content}" for m in messages_list)
            if messages_list
            else content
        )

        try:
            llm = self._get_llm()
            parser = PydanticOutputParser(pydantic_object=SmartReplySuggestion)
            prompt = ChatPromptTemplate.from_messages(
                [
                    (
                        "system",
                        "You are a skilled customer support agent. "
                        "Generate 3 contextually appropriate reply suggestions for "
                        "the agent to use. Suggestions should be professional, "
                        "empathetic, and actionable.\n"
                        "{format_instructions}",
                    ),
                    (
                        "human",
                        "Generate reply suggestions for this support ticket:\n"
                        "Channel: {channel}\n"
                        "Subject: {subject}\n"
                        "Conversation:\n{conversation}",
                    ),
                ]
            ).partial(format_instructions=parser.get_format_instructions())

            chain = prompt | llm | parser
            result_obj: SmartReplySuggestion = await chain.ainvoke(
                {
                    "channel": channel_str,
                    "subject": ticket.subject or "Support Request",
                    "conversation": conversation_history,
                }
            )

            return {
                "ticket_id": ticket_id,
                "suggestions": result_obj.suggestions[:3],
                "tone": result_obj.tone,
                "powered_by": "langchain",
            }

        except Exception:
            suggestions = ai_service.suggest_replies(content, channel_str)
            return {
                "ticket_id": ticket_id,
                "suggestions": suggestions,
                "powered_by": "keyword_fallback",
            }


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------
langchain_ai_service = LangChainAIService()
