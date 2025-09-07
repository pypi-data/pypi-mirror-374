"""Node implementations for RAG pipeline."""

from dataclasses import dataclass, replace
from typing import override

import faiss
import numpy as np

from clearflow import Node, NodeResult
from examples.rag.models import (
    AnsweredState,
    ChunkedState,
    EmbeddedState,
    IndexedState,
    QueryState,
    RAGState,
    RetrievedState,
)
from examples.rag.utils import call_llm, fixed_size_chunk, get_embedding

# Offline indexing nodes


@dataclass(frozen=True)
class ChunkDocumentsNode(Node[RAGState, ChunkedState]):
    """Splits documents into smaller chunks for processing."""

    name: str = "chunk_documents"

    @override
    async def exec(self, state: RAGState) -> NodeResult[ChunkedState]:
        """Chunk all documents into smaller pieces.

        Returns:
            NodeResult with chunked state and 'chunked' outcome.
        """
        all_chunks = tuple(chunk for doc in state.documents for chunk in fixed_size_chunk(doc))

        print(f"✅ Created {len(all_chunks)} chunks from {len(state.documents)} documents")

        new_state = ChunkedState(
            documents=state.documents,
            chunks=all_chunks,
        )
        return NodeResult(new_state, outcome="chunked")


@dataclass(frozen=True)
class EmbedDocumentsNode(Node[ChunkedState, EmbeddedState]):
    """Creates embeddings for all document chunks."""

    name: str = "embed_documents"

    @override
    async def exec(self, state: ChunkedState) -> NodeResult[EmbeddedState]:
        """Create embeddings for all chunks.

        Returns:
            NodeResult with embedded state and 'embedded' outcome.
        """
        embeddings_tuple = tuple(get_embedding(chunk) for chunk in state.chunks)

        for i in range(len(embeddings_tuple)):
            print(f"  Embedded chunk {i + 1}/{len(state.chunks)}", end="\r")

        embeddings = np.array(embeddings_tuple, dtype=np.float32)
        print(f"✅ Created {len(embeddings)} document embeddings")

        new_state = EmbeddedState(
            documents=state.documents,
            chunks=state.chunks,
            embeddings=embeddings,
        )
        return NodeResult(new_state, outcome="embedded")


@dataclass(frozen=True)
class CreateIndexNode(Node[EmbeddedState, IndexedState]):
    """Creates a FAISS index from document embeddings."""

    name: str = "create_index"

    @override
    async def exec(self, state: EmbeddedState) -> NodeResult[IndexedState]:
        """Create FAISS index from embeddings.

        Returns:
            NodeResult with indexed state and 'indexed' outcome.

        Raises:
            ValueError: If no embeddings are available to index.
        """
        print("🔍 Creating search index...")

        if state.embeddings is None or len(state.embeddings) == 0:
            msg = "No embeddings to index"
            raise ValueError(msg)

        dimension = state.embeddings.shape[1]

        # Create a flat L2 index
        index = faiss.IndexFlatL2(dimension)

        # Add the embeddings to the index
        index.add(state.embeddings)

        print(f"✅ Index created with {index.ntotal} vectors")

        new_state = IndexedState(
            documents=state.documents,
            chunks=state.chunks,
            embeddings=state.embeddings,
            index=index,
        )
        return NodeResult(new_state, outcome="indexed")


# Online query nodes


@dataclass(frozen=True)
class EmbedQueryNode(Node[QueryState]):
    """Creates embedding for the user's query."""

    name: str = "embed_query"

    @override
    async def exec(self, state: QueryState) -> NodeResult[QueryState]:
        """Embed the query.

        Returns:
            NodeResult with query embedding and 'embedded' outcome.
        """
        print(f"🔍 Embedding query: {state.query}")

        query_embedding = get_embedding(state.query)
        query_embedding_array = np.array([query_embedding], dtype=np.float32)

        new_state = replace(state, query_embedding=query_embedding_array)
        return NodeResult(new_state, outcome="embedded")


@dataclass(frozen=True)
class RetrieveDocumentNode(Node[QueryState, RetrievedState]):
    """Retrieves the most relevant document chunk."""

    name: str = "retrieve_document"

    @override
    async def exec(self, state: QueryState) -> NodeResult[RetrievedState]:
        """Search for the most relevant document.

        Returns:
            NodeResult with retrieved state and 'retrieved' outcome.

        Raises:
            ValueError: If query embedding, index, or chunks are missing.
        """
        print("🔎 Searching for relevant documents...")

        if state.query_embedding is None:
            msg = "No query embedding available"
            raise ValueError(msg)
        if state.index is None:
            msg = "No search index available"
            raise ValueError(msg)
        if not state.chunks:
            msg = "No document chunks available"
            raise ValueError(msg)

        # Search for the most similar document
        distances, indices = state.index.search(state.query_embedding, k=1)

        # Get the index of the most similar document
        best_idx = int(indices[0][0])
        distance = float(distances[0][0])

        # Get the corresponding text
        most_relevant_text = state.chunks[best_idx]

        print(f"📄 Retrieved document (index: {best_idx}, distance: {distance:.4f})")
        print(f'📄 Most relevant text: "{most_relevant_text[:200]}..."')

        new_state = RetrievedState(
            documents=state.documents,
            chunks=state.chunks,
            embeddings=state.embeddings,
            index=state.index,
            query=state.query,
            query_embedding=state.query_embedding,
            retrieved_text=most_relevant_text,
            retrieved_index=best_idx,
            retrieval_score=distance,
        )
        return NodeResult(new_state, outcome="retrieved")


@dataclass(frozen=True)
class GenerateAnswerNode(Node[RetrievedState, AnsweredState]):
    """Generates an answer using the retrieved context."""

    name: str = "generate_answer"

    @override
    async def exec(self, state: RetrievedState) -> NodeResult[AnsweredState]:
        """Generate answer using LLM with retrieved context.

        Returns:
            NodeResult with answered state and 'answered' outcome.
        """
        prompt = f"""Briefly answer the following question based on the context provided:
Question: {state.query}
Context: {state.retrieved_text}
Answer:"""

        answer = call_llm(prompt)

        print("\n🤖 Generated Answer:")
        print(answer)

        new_state = AnsweredState(
            documents=state.documents,
            chunks=state.chunks,
            embeddings=state.embeddings,
            index=state.index,
            query=state.query,
            query_embedding=state.query_embedding,
            retrieved_text=state.retrieved_text,
            retrieved_index=state.retrieved_index,
            retrieval_score=state.retrieval_score,
            answer=answer,
        )
        return NodeResult(new_state, outcome="answered")
