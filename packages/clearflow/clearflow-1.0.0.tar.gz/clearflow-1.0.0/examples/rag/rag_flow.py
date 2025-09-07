"""RAG flow construction."""

from clearflow import Node, flow
from examples.rag.models import AnsweredState, IndexedState, QueryState, RAGState
from examples.rag.nodes import (
    ChunkDocumentsNode,
    CreateIndexNode,
    EmbedDocumentsNode,
    EmbedQueryNode,
    GenerateAnswerNode,
    RetrieveDocumentNode,
)


def create_offline_flow() -> Node[RAGState, IndexedState]:
    """Create the offline indexing flow.

    This flow processes documents through:
    1. Chunking - Split documents into smaller pieces
    2. Embedding - Convert chunks to vectors
    3. Indexing - Create searchable vector index

    Returns:
        Flow that transforms RAGState to IndexedState
    """
    chunk = ChunkDocumentsNode()
    embed = EmbedDocumentsNode()
    index = CreateIndexNode()

    return (
        flow("IndexDocuments", chunk)
        .route(chunk, "chunked", embed)
        .route(embed, "embedded", index)
        .end(index, "indexed")
    )


def create_online_flow() -> Node[QueryState, AnsweredState]:
    """Create the online query flow.

    This flow processes queries through:
    1. Query embedding - Convert query to vector
    2. Retrieval - Find most relevant chunk
    3. Generation - Create answer with context

    Returns:
        Flow that processes QueryState
    """
    embed_query = EmbedQueryNode()
    retrieve = RetrieveDocumentNode()
    generate = GenerateAnswerNode()

    return (
        flow("AnswerQuery", embed_query)
        .route(embed_query, "embedded", retrieve)
        .route(retrieve, "retrieved", generate)
        .end(generate, "answered")
    )
