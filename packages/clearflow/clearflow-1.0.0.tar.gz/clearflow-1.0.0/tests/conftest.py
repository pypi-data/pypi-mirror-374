"""Shared test fixtures and types for ClearFlow test suite.

This module provides immutable types used across multiple test modules,
demonstrating mission-critical AI orchestration patterns with deep immutability.

"""

from dataclasses import dataclass as dc

# Immutable types for mission-critical AI orchestration scenarios
# All state is deeply immutable using frozen dataclasses


@dc(frozen=True)
class Document:
    """Immutable document for RAG pipelines."""

    content: str
    source: str
    metadata: tuple[tuple[str, str], ...] = ()


@dc(frozen=True)
class EmbeddedDocument:
    """Document with embedding vector."""

    document: Document
    embedding: tuple[float, ...]


@dc(frozen=True)
class RAGState:
    """State for retrieval-augmented generation."""

    query: str
    documents: tuple[Document, ...]
    retrieved: tuple[Document, ...] = ()
    context: str = ""
    response: str = ""


@dc(frozen=True)
class Message:
    """Immutable message for agent communication."""

    role: str  # 'user', 'assistant', 'system'
    content: str


@dc(frozen=True)
class AgentState:
    """State for multi-agent orchestration."""

    messages: tuple[Message, ...]
    context: str
    temperature: float = 0.7


@dc(frozen=True)
class ToolCall:
    """Immutable tool invocation."""

    name: str
    parameters: tuple[tuple[str, str], ...]
    result: str = ""


@dc(frozen=True)
class ToolState:
    """State for tool use orchestration."""

    query: str
    available_tools: tuple[str, ...]
    selected_tool: str = ""
    tool_calls: tuple[ToolCall, ...] = ()
    final_answer: str = ""


@dc(frozen=True)
class ValidationState:
    """State for output validation pipelines."""

    input_text: str
    validated: bool = False
    errors: tuple[str, ...] = ()
    sanitized_output: str = ""
