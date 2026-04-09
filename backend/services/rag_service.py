"""
services/rag_service.py
-----------------------
FAISS-backed RAG (Retrieval-Augmented Generation) service using LangChain.

Provides:
  - In-memory FAISS vector store for document retrieval
  - Document embedding and indexing via OpenAI embeddings
  - Similarity search for knowledge-base queries

Falls back gracefully (returns empty results) when FAISS / LangChain is
not installed or when ``OPENAI_API_KEY`` is absent.
"""
from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

# ---------------------------------------------------------------------------
# Optional imports – service degrades gracefully when absent
# ---------------------------------------------------------------------------
try:
    from langchain_openai import OpenAIEmbeddings  # type: ignore
    from langchain_community.vectorstores import FAISS  # type: ignore
    from langchain_core.documents import Document  # type: ignore
    _rag_available = True
except ImportError:  # pragma: no cover
    _rag_available = False


class RAGService:
    """
    FAISS-backed knowledge base for document retrieval.

    Documents are embedded using OpenAI embeddings and stored in an
    in-memory FAISS index.  The ``search`` method returns the *top_k*
    most similar documents for a natural-language query.

    When RAG dependencies are unavailable, ``is_available()`` returns
    ``False`` and ``search()`` returns an empty list rather than raising.
    """

    def __init__(self) -> None:
        self._embeddings: Optional[Any] = None
        self._faiss_store: Optional[Any] = None

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_embeddings(self) -> Any:
        if self._embeddings is not None:
            return self._embeddings
        if not _rag_available:
            raise RuntimeError(
                "langchain-openai and langchain-community are required for RAG. "
                "Add them to requirements.txt."
            )
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY environment variable is not set.")
        embedding_model = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
        self._embeddings = OpenAIEmbeddings(model=embedding_model, api_key=api_key)
        return self._embeddings

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def is_available(self) -> bool:
        """Return ``True`` if RAG dependencies and ``OPENAI_API_KEY`` are present."""
        return _rag_available and bool(os.getenv("OPENAI_API_KEY"))

    async def add_documents(self, documents: List[Dict[str, str]]) -> int:
        """
        Embed and index *documents* into the FAISS vector store.

        Args:
            documents: List of dicts with ``content`` (required) and
                       optional ``title`` and ``category`` keys.

        Returns:
            Number of documents successfully indexed.
        """
        embeddings = self._get_embeddings()
        docs = [
            Document(
                page_content=d["content"],
                metadata={
                    "title": d.get("title", ""),
                    "category": d.get("category", ""),
                },
            )
            for d in documents
        ]
        if self._faiss_store is None:
            self._faiss_store = FAISS.from_documents(docs, embeddings)
        else:
            self._faiss_store.add_documents(docs)
        return len(docs)

    async def search(
        self, query: str, top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search the FAISS index for documents most similar to *query*.

        Returns:
            List of dicts with keys ``content``, ``title``, ``category``,
            and ``score`` (lower distance = more similar for L2 FAISS).
            Returns an empty list when no index exists or RAG is unavailable.
        """
        if self._faiss_store is None:
            return []
        results = self._faiss_store.similarity_search_with_score(query, k=top_k)
        return [
            {
                "content": doc.page_content,
                "title": doc.metadata.get("title", ""),
                "category": doc.metadata.get("category", ""),
                "score": float(score),
            }
            for doc, score in results
        ]

    async def setup_default_knowledge_base(self) -> int:
        """
        Seed the FAISS store with a built-in support knowledge base.

        Useful for demos and integration tests that do not have a live
        database of knowledge documents.

        Returns:
            Number of documents indexed.
        """
        default_docs = [
            {
                "title": "Billing FAQ",
                "category": "billing",
                "content": (
                    "For billing inquiries, refunds take 3-5 business days. "
                    "Invoices are sent automatically at the start of each billing cycle. "
                    "Contact billing@support.com for urgent payment issues."
                ),
            },
            {
                "title": "Technical Support Guide",
                "category": "technical",
                "content": (
                    "For technical issues, first try clearing your browser cache. "
                    "Check our status page at status.example.com for outages. "
                    "For API errors, verify your API key and rate limits."
                ),
            },
            {
                "title": "Shipping & Delivery",
                "category": "shipping",
                "content": (
                    "Standard shipping takes 5-7 business days. "
                    "Express shipping is available for 2-day delivery. "
                    "Track your order at tracking.example.com with your order number."
                ),
            },
            {
                "title": "Account Management",
                "category": "general",
                "content": (
                    "To reset your password, use the 'Forgot Password' link on the login page. "
                    "Account upgrades are available in your settings panel. "
                    "For account deletion, contact privacy@support.com."
                ),
            },
        ]
        return await self.add_documents(default_docs)


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------
rag_service = RAGService()
