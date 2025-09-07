"""Test type transformation features of ClearFlow.

This module tests Node[TIn, TOut] type transformations for real AI pipelines,
demonstrating how to avoid "god objects" through type-safe transformations.

"""

from dataclasses import dataclass as dc
from typing import override

from clearflow import Node, NodeResult
from tests.conftest import Document


# RAG pipeline types
@dc(frozen=True)
class Query:
    """User query for RAG system."""

    text: str
    max_results: int = 5


@dc(frozen=True)
class SearchResults:
    """Retrieved documents with scores."""

    query: Query
    documents: tuple[tuple[Document, float], ...]  # (doc, relevance_score)


@dc(frozen=True)
class Context:
    """Prepared context for generation."""

    query: Query
    relevant_texts: tuple[str, ...]
    total_tokens: int


@dc(frozen=True)
class Response:
    """Final generated response."""

    query: Query
    answer: str
    sources: tuple[str, ...]


@dc(frozen=True)
class RetrievalNode(Node[Query, SearchResults]):
    """Retrieves relevant documents."""

    name: str = "retriever"

    @override
    async def exec(self, state: Query) -> NodeResult[SearchResults]:
        # Simulate retrieval
        mock_docs = (
            (Document("AI is transforming industries", "doc1.pdf"), 0.95),
            (Document("Machine learning applications", "doc2.pdf"), 0.87),
        )
        results = SearchResults(query=state, documents=mock_docs[: state.max_results])
        return NodeResult(results, outcome="retrieved")


@dc(frozen=True)
class ContextBuilder(Node[SearchResults, Context]):
    """Builds context from search results."""

    name: str = "context_builder"

    @override
    async def exec(self, state: SearchResults) -> NodeResult[Context]:
        texts = tuple(doc.content for doc, _ in state.documents)
        tokens = sum(len(text.split()) for text in texts)
        context = Context(query=state.query, relevant_texts=texts, total_tokens=tokens)
        outcome = "context_ready" if tokens < 1000 else "context_too_long"
        return NodeResult(context, outcome=outcome)


@dc(frozen=True)
class GenerationNode(Node[Context, Response]):
    """Generates response from context."""

    name: str = "generator"

    @override
    async def exec(self, state: Context) -> NodeResult[Response]:
        # Simulate generation
        answer = f"Based on {len(state.relevant_texts)} sources: " + state.relevant_texts[0][:50]
        sources = tuple(f"doc{i + 1}.pdf" for i in range(len(state.relevant_texts)))
        response = Response(query=state.query, answer=answer, sources=sources)
        return NodeResult(response, outcome="generated")


class TestTypeTransformations:
    """Test Node[TIn, TOut] type transformations for real AI pipelines."""

    @staticmethod
    async def test_rag_retrieval_transformation() -> None:
        """Test Query to SearchResults transformation."""
        query = Query(text="How is AI transforming industries?", max_results=2)
        retrieval = RetrievalNode()
        result = await retrieval(query)
        assert isinstance(result.state, SearchResults)
        assert len(result.state.documents) == 2

    @staticmethod
    async def test_rag_context_building() -> None:
        """Test SearchResults to Context transformation."""
        query = Query(text="AI query", max_results=2)
        mock_results = SearchResults(
            query=query,
            documents=(
                (Document("AI content", "doc1.pdf"), 0.95),
                (Document("ML content", "doc2.pdf"), 0.87),
            ),
        )
        builder = ContextBuilder()
        result = await builder(mock_results)
        assert isinstance(result.state, Context)
        assert result.state.total_tokens > 0

    @staticmethod
    async def test_rag_generation() -> None:
        """Test Context to Response transformation."""
        query = Query(text="test", max_results=1)
        context = Context(query=query, relevant_texts=("Test content",), total_tokens=2)
        generator = GenerationNode()
        result = await generator(context)
        assert isinstance(result.state, Response)
        assert result.state.query == query
        assert len(result.state.sources) > 0

    @staticmethod
    async def test_tool_planning() -> None:
        """Test tool planning transformation."""

        # Tool types
        @dc(frozen=True)
        class ToolQuery:
            question: str
            context: str = ""

        @dc(frozen=True)
        class ToolPlan:
            query: ToolQuery
            selected_tool: str
            parameters: tuple[tuple[str, str], ...]

        @dc(frozen=True)
        class SimplePlanner(Node[ToolQuery, ToolPlan]):
            name: str = "planner"

            @override
            async def exec(self, state: ToolQuery) -> NodeResult[ToolPlan]:
                tool = "calculator" if "calculate" in state.question.lower() else "none"
                params = (("expr", state.question),) if tool != "none" else ()
                plan = ToolPlan(query=state, selected_tool=tool, parameters=params)
                return NodeResult(plan, outcome="planned")

        query = ToolQuery(question="Calculate 6 * 7")
        planner = SimplePlanner()
        result = await planner(query)
        assert isinstance(result.state, ToolPlan)
        assert result.state.selected_tool == "calculator"

    @staticmethod
    async def test_tool_execution() -> None:
        """Test tool execution transformation."""

        @dc(frozen=True)
        class ToolQuery:
            question: str

        @dc(frozen=True)
        class ToolPlan:
            query: ToolQuery
            selected_tool: str

        @dc(frozen=True)
        class ToolResult:
            plan: ToolPlan
            output: str
            success: bool

        @dc(frozen=True)
        class SimpleExecutor(Node[ToolPlan, ToolResult]):
            name: str = "executor"

            @override
            async def exec(self, state: ToolPlan) -> NodeResult[ToolResult]:
                output = "Result: 42" if state.selected_tool == "calculator" else "None"
                success = state.selected_tool == "calculator"
                result = ToolResult(plan=state, output=output, success=success)
                return NodeResult(result, outcome="executed")

        query = ToolQuery(question="test")
        plan = ToolPlan(query=query, selected_tool="calculator")
        executor = SimpleExecutor()
        result = await executor(plan)
        assert isinstance(result.state, ToolResult)
        assert result.state.success is True
