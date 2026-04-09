"""
services/langgraph_workflow.py
-------------------------------
LangGraph-powered multi-step ticket processing workflow with state management.

Workflow nodes (executed in order):
  1. classify_ticket   – LLM-based priority / category / department classification
  2. decide_response   – decide whether to auto-respond or escalate
  3. route_to_agent    – determine routing logic and reason
  4. human_review      – flag tickets that require human oversight

Conditional edges route the workflow to END after human_review, carrying
the full accumulated state.

Falls back gracefully to simple keyword-based logic when LangGraph or
LangChain is not installed, or when the OpenAI API call fails.
"""
from __future__ import annotations

import os
from typing import Any, Dict, List, Optional, TypedDict

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# ---------------------------------------------------------------------------
# Optional LangGraph + LangChain imports
# ---------------------------------------------------------------------------
try:
    from langgraph.graph import StateGraph, END  # type: ignore
    _langgraph_available = True
except ImportError:  # pragma: no cover
    _langgraph_available = False

try:
    from langchain_openai import ChatOpenAI  # type: ignore
    from langchain_core.prompts import ChatPromptTemplate  # type: ignore
    _langchain_available = True
except ImportError:  # pragma: no cover
    _langchain_available = False


# ---------------------------------------------------------------------------
# Workflow State
# ---------------------------------------------------------------------------

class TicketWorkflowState(TypedDict):
    """Typed state object passed through every workflow node."""

    ticket_id: int
    content: str
    subject: str
    channel: str
    # Set by classify node
    priority: str
    category: str
    department: str
    # Set by decide_response node
    auto_respond: bool
    suggested_response: str
    # Set by route_agent node
    routing_reason: str
    # Set by human_review node
    requires_human_review: bool
    # Audit trail
    workflow_steps: List[str]


# ---------------------------------------------------------------------------
# Workflow Service
# ---------------------------------------------------------------------------

class LangGraphWorkflowService:
    """
    Orchestrates multi-step ticket processing using a LangGraph state machine.

    Falls back to simple keyword-based logic when LangGraph is unavailable
    or when an LLM call fails, ensuring the endpoint always returns a
    meaningful result.
    """

    def __init__(self) -> None:
        self._llm: Optional[Any] = None
        self._workflow: Optional[Any] = None

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
        self._llm = ChatOpenAI(model=model, temperature=0.2, api_key=api_key)
        return self._llm

    # ------------------------------------------------------------------
    # Workflow nodes
    # ------------------------------------------------------------------

    async def _node_classify(
        self, state: TicketWorkflowState
    ) -> TicketWorkflowState:
        """Node 1: Classify ticket priority, category, and department via LLM."""
        try:
            llm = self._get_llm()
            prompt = ChatPromptTemplate.from_messages(
                [
                    (
                        "system",
                        "You are a support ticket classifier. "
                        "Respond with EXACTLY this format (no extra text):\n"
                        "PRIORITY|CATEGORY|DEPARTMENT\n\n"
                        "Valid values:\n"
                        "  PRIORITY   : low / medium / high / urgent\n"
                        "  CATEGORY   : billing / technical / shipping / general\n"
                        "  DEPARTMENT : billing_team / technical_support / logistics / general_support",
                    ),
                    (
                        "human",
                        "Classify: Channel={channel}, Content={content}",
                    ),
                ]
            )
            chain = prompt | llm
            response = await chain.ainvoke(
                {"channel": state["channel"], "content": state["content"]}
            )
            parts = response.content.strip().split("|")
            if len(parts) == 3:
                state["priority"] = parts[0].strip().lower()
                state["category"] = parts[1].strip().lower()
                state["department"] = parts[2].strip().lower()
        except Exception:
            # Keep keyword-seeded defaults already in state
            pass

        state["workflow_steps"].append("classify")
        return state

    async def _node_decide_response(
        self, state: TicketWorkflowState
    ) -> TicketWorkflowState:
        """Node 2: Decide whether the ticket should receive an auto-response."""
        priority = state.get("priority", "medium")
        category = state.get("category", "general")

        # Auto-respond only for low/medium-priority, non-billing tickets
        auto_respond = priority in ("low", "medium") and category != "billing"
        state["auto_respond"] = auto_respond

        if auto_respond:
            try:
                llm = self._get_llm()
                prompt = ChatPromptTemplate.from_messages(
                    [
                        (
                            "system",
                            "You are a customer support agent. "
                            "Write a brief, professional acknowledgment response. "
                            "Keep it under 100 words.",
                        ),
                        (
                            "human",
                            "Customer issue (category={category}): {content}",
                        ),
                    ]
                )
                chain = prompt | llm
                response = await chain.ainvoke(
                    {"content": state["content"], "category": category}
                )
                state["suggested_response"] = response.content.strip()
            except Exception:
                state["suggested_response"] = (
                    "Thank you for contacting us. We have received your request "
                    "and will get back to you as soon as possible."
                )

        state["workflow_steps"].append("decide_response")
        return state

    async def _node_route_agent(
        self, state: TicketWorkflowState
    ) -> TicketWorkflowState:
        """Node 3: Determine routing logic and produce a human-readable reason."""
        department = state.get("department", "general_support")
        priority = state.get("priority", "medium")

        routing_rules: Dict[str, str] = {
            "billing_team": (
                "Route to Billing Team – payment/invoice expertise needed"
            ),
            "technical_support": (
                "Route to Technical Support – engineering knowledge required"
            ),
            "logistics": (
                "Route to Logistics Team – shipping/delivery tracking needed"
            ),
            "general_support": (
                "Route to General Support – standard customer service"
            ),
        }

        reason = routing_rules.get(
            department, "Route to General Support – default routing"
        )

        # Escalate high/urgent tickets
        if priority in ("high", "urgent"):
            reason = f"ESCALATED: {reason}"

        state["routing_reason"] = reason
        state["workflow_steps"].append("route_agent")
        return state

    async def _node_human_review(
        self, state: TicketWorkflowState
    ) -> TicketWorkflowState:
        """Node 4: Determine whether human review is required."""
        priority = state.get("priority", "medium")
        category = state.get("category", "general")

        # Human review required for high/urgent tickets or billing issues
        requires_human = priority in ("high", "urgent") or category == "billing"
        state["requires_human_review"] = requires_human
        state["workflow_steps"].append("human_review")
        return state

    # ------------------------------------------------------------------
    # Conditional edge
    # ------------------------------------------------------------------

    def _should_auto_respond(self, state: TicketWorkflowState) -> str:
        """Conditional router: both branches end the workflow."""
        if state.get("requires_human_review", False):
            return "needs_human"
        return "auto_handled"

    # ------------------------------------------------------------------
    # Build workflow graph
    # ------------------------------------------------------------------

    def _build_workflow(self) -> Any:
        """Construct and compile the LangGraph StateGraph."""
        if not _langgraph_available:
            raise RuntimeError(
                "langgraph is not installed. "
                "Add 'langgraph>=0.1.0' to requirements.txt."
            )

        workflow: StateGraph = StateGraph(TicketWorkflowState)

        workflow.add_node("classify", self._node_classify)
        workflow.add_node("decide_response", self._node_decide_response)
        workflow.add_node("route_agent", self._node_route_agent)
        workflow.add_node("human_review", self._node_human_review)

        workflow.set_entry_point("classify")

        workflow.add_edge("classify", "decide_response")
        workflow.add_edge("decide_response", "route_agent")
        workflow.add_edge("route_agent", "human_review")

        workflow.add_conditional_edges(
            "human_review",
            self._should_auto_respond,
            {
                "needs_human": END,
                "auto_handled": END,
            },
        )

        return workflow.compile()

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------

    async def process_ticket(
        self, db: AsyncSession, ticket_id: int
    ) -> Dict[str, Any]:
        """
        Run the full LangGraph workflow for a ticket.

        Fetches ticket data, seeds the initial state using keyword-based
        defaults (so the fallback is always meaningful), then runs the
        LangGraph state machine.

        Falls back to simple classification if LangGraph is unavailable
        or the workflow raises an exception.
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

        # Seed state with keyword-based defaults as a safe baseline
        keyword_result = await ai_service.classify_ticket(db, ticket_id)
        initial_state: TicketWorkflowState = {
            "ticket_id": ticket_id,
            "content": content,
            "subject": ticket.subject or "",
            "channel": channel_str,
            "priority": str(keyword_result.get("suggested_priority", "medium")),
            "category": str(keyword_result.get("suggested_category", "general")),
            "department": "general_support",
            "auto_respond": False,
            "suggested_response": "",
            "routing_reason": "",
            "requires_human_review": False,
            "workflow_steps": [],
        }

        try:
            if self._workflow is None:
                self._workflow = self._build_workflow()

            final_state: TicketWorkflowState = await self._workflow.ainvoke(
                initial_state
            )

            return {
                "ticket_id": ticket_id,
                "priority": final_state["priority"],
                "category": final_state["category"],
                "department": final_state["department"],
                "requires_human_review": final_state["requires_human_review"],
                "auto_respond": final_state["auto_respond"],
                "suggested_response": final_state.get("suggested_response", ""),
                "routing_reason": final_state.get("routing_reason", ""),
                "workflow_steps": final_state["workflow_steps"],
                "powered_by": "langgraph",
            }

        except Exception:
            # Graceful fallback
            return {
                "ticket_id": ticket_id,
                "priority": initial_state["priority"],
                "category": initial_state["category"],
                "department": "general_support",
                "requires_human_review": False,
                "auto_respond": False,
                "suggested_response": "",
                "routing_reason": "Default routing (LangGraph unavailable)",
                "workflow_steps": ["fallback"],
                "powered_by": "keyword_fallback",
            }


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------
langgraph_workflow_service = LangGraphWorkflowService()
