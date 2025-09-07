"""State models for RAG pipeline."""

from dataclasses import dataclass

import faiss
import numpy as np
import numpy.typing as npt


@dataclass(frozen=True)
class RAGState:
    """Base state for RAG pipeline with documents."""

    documents: tuple[str, ...] = ()


@dataclass(frozen=True)
class ChunkedState(RAGState):
    """State after document chunking."""

    chunks: tuple[str, ...] = ()


@dataclass(frozen=True)
class EmbeddedState(ChunkedState):
    """State after creating embeddings."""

    embeddings: npt.NDArray[np.float32] | None = None


@dataclass(frozen=True)
class IndexedState(EmbeddedState):
    """State after creating search index."""

    index: faiss.Index | None = None


@dataclass(frozen=True)
class QueryState(IndexedState):
    """State for query processing."""

    query: str = ""
    query_embedding: npt.NDArray[np.float32] | None = None


@dataclass(frozen=True)
class RetrievedState(QueryState):
    """State after document retrieval."""

    retrieved_text: str = ""
    retrieved_index: int = -1
    retrieval_score: float = 0.0


@dataclass(frozen=True)
class AnsweredState(RetrievedState):
    """Final state with generated answer."""

    answer: str = ""
