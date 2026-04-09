"""
services/embedding_service.py
------------------------------
Vector-embedding helpers using the OpenAI embeddings API.

Embeddings are stored in two ways:
  1. As raw bytes in the ``agent_knowledge_bases.embedding`` column (always).
  2. In Pinecone (when ``PINECONE_API_KEY`` is set in the environment).

Similarity search uses Pinecone when available, otherwise falls back to an
in-process cosine-similarity scan over the rows already loaded from the DB.
"""
from __future__ import annotations

import io
import os
from typing import Any, Dict, List, Optional

import numpy as np

# ---------------------------------------------------------------------------
# Optional dependencies – imported lazily so the service still loads when
# neither openai nor pinecone is installed (unit-test / CI scenarios).
# ---------------------------------------------------------------------------
try:
    from openai import AsyncOpenAI  # type: ignore
    _openai_available = True
except ImportError:  # pragma: no cover
    _openai_available = False

try:
    from pinecone import Pinecone as PineconeClient  # type: ignore
    _pinecone_available = True
except ImportError:  # pragma: no cover
    _pinecone_available = False


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _array_to_bytes(vec: List[float]) -> bytes:
    arr = np.array(vec, dtype=np.float32)
    buf = io.BytesIO()
    np.save(buf, arr)
    return buf.getvalue()


def _bytes_to_array(data: bytes) -> np.ndarray:
    buf = io.BytesIO(data)
    return np.load(buf)


def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    denom = np.linalg.norm(a) * np.linalg.norm(b)
    if denom == 0:
        return 0.0
    return float(np.dot(a, b) / denom)


# ---------------------------------------------------------------------------
# Service class
# ---------------------------------------------------------------------------

class EmbeddingService:
    """Generate text embeddings and perform similarity search."""

    EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")

    def __init__(self) -> None:
        self._openai: Optional[Any] = None
        self._pinecone_index: Optional[Any] = None

    # ------------------------------------------------------------------
    # Lazy initialisation
    # ------------------------------------------------------------------

    def _get_openai(self) -> Any:
        if self._openai is None:
            if not _openai_available:
                raise RuntimeError(
                    "openai package is not installed. "
                    "Add 'openai>=1.3.0' to requirements.txt."
                )
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise RuntimeError("OPENAI_API_KEY environment variable is not set.")
            self._openai = AsyncOpenAI(api_key=api_key)
        return self._openai

    def _get_pinecone_index(self) -> Optional[Any]:
        """Return a Pinecone index handle, or None when Pinecone is not configured."""
        if self._pinecone_index is not None:
            return self._pinecone_index

        if not _pinecone_available:
            return None

        api_key = os.getenv("PINECONE_API_KEY")
        if not api_key:
            return None

        pc = PineconeClient(api_key=api_key)
        index_name = os.getenv("PINECONE_INDEX", "agent-knowledge")
        self._pinecone_index = pc.Index(index_name)
        return self._pinecone_index

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def generate_embedding(self, text: str) -> List[float]:
        """Return a float vector for *text* using the OpenAI embeddings API."""
        client = self._get_openai()
        response = await client.embeddings.create(
            model=self.EMBEDDING_MODEL,
            input=text,
        )
        return response.data[0].embedding

    def embedding_to_bytes(self, embedding: List[float]) -> bytes:
        return _array_to_bytes(embedding)

    async def store_in_pinecone(
        self,
        doc_id: str,
        embedding: List[float],
        metadata: Dict[str, Any],
    ) -> None:
        """Upsert a vector into Pinecone (no-op when Pinecone is not configured)."""
        index = self._get_pinecone_index()
        if index is None:
            return
        index.upsert(vectors=[(doc_id, embedding, metadata)])

    async def search_similar_pinecone(
        self,
        query_embedding: List[float],
        agent_id: int,
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        """Query Pinecone for similar vectors filtered by *agent_id*."""
        index = self._get_pinecone_index()
        if index is None:
            return []

        results = index.query(
            vector=query_embedding,
            top_k=top_k,
            filter={"agent_id": {"$eq": agent_id}},
            include_metadata=True,
        )
        return [
            {
                "id": match.id,
                "score": match.score,
                "metadata": match.metadata,
            }
            for match in results.matches
        ]

    def search_similar_local(
        self,
        query_embedding: List[float],
        kb_rows: List[Any],
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Fallback cosine-similarity search over *kb_rows* (ORM objects).

        Each row must have ``.id``, ``.title``, ``.category``, and
        ``.embedding`` (bytes produced by :meth:`embedding_to_bytes`).
        """
        query_vec = np.array(query_embedding, dtype=np.float32)
        scored: List[Dict[str, Any]] = []

        for row in kb_rows:
            if row.embedding is None:
                continue
            doc_vec = _bytes_to_array(row.embedding)
            score = _cosine_similarity(query_vec, doc_vec)
            scored.append(
                {
                    "id": row.id,
                    "title": row.title,
                    "category": row.category,
                    "score": score,
                }
            )

        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:top_k]


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------
embedding_service = EmbeddingService()
