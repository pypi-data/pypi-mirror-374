# RAG Example

Retrieval-Augmented Generation system demonstrating ClearFlow's type-safe state transformations.

## Flow

```mermaid
graph TD
    subgraph Offline Indexing Flow
        Start1([RAGState]) --> Chunk[ChunkDocumentsNode]
        Chunk -->|chunked| Embed[EmbedDocumentsNode]
        Embed -->|embedded| Index[CreateIndexNode]
        Index -->|indexed| End1([IndexedState])
    end
    
    subgraph Online Query Flow
        Start2([QueryState]) --> EmbedQ[EmbedQueryNode]
        EmbedQ -->|embedded| Retrieve[RetrieveDocumentNode]
        Retrieve -->|retrieved| Generate[GenerateAnswerNode]
        Generate -->|answered| End2([AnsweredState])
    end
```

## Quick Start

```bash
# From project root directory

# 1. Set up your OpenAI API key
cp .env.example .env
# Edit .env and add your API key

# 2. Install dependencies
uv sync --all-extras

# 3. Run the example
cd examples/rag
python main.py  # If venv is activated
# Or: uv run python main.py
# With custom query:
python main.py "What is Q-Mesh protocol?"
```

## How It Works

RAG combines document retrieval with language model generation. This implementation uses two flows:

**Offline Indexing Flow:**

- `ChunkDocuments` - Splits text into overlapping chunks (500 chars, 50 overlap)
- `EmbedDocuments` - Creates OpenAI embeddings for each chunk
- `CreateIndex` - Builds FAISS vector index for similarity search

**Online Query Flow:**

- `EmbedQuery` - Converts user query to embedding
- `RetrieveDocument` - Finds most similar chunk via cosine similarity
- `GenerateAnswer` - Uses GPT-4 with retrieved context to answer

Each transformation creates new immutable state: `RAGState → ChunkedState → EmbeddedState → IndexedState`

## Key Features

- **Two-phase architecture** - Separate indexing and query flows
- **Type-safe transformations** - Each node produces specific state types
- **Immutable state** - All transformations create new state objects
- **Vector search** - FAISS for efficient similarity matching
- **Explicit routing** - Clear flow definition with single termination

## Files

- `main.py` - Entry point and flow orchestration
- `nodes.py` - All node implementations
- `rag_flow.py` - Flow definitions and routing
- `models.py` - State type definitions
- `utils.py` - OpenAI and chunking utilities
