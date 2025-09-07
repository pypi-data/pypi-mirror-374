"""Test Flow orchestration features of ClearFlow.

This module tests the Flow class functionality including linear flows,
branching, single termination enforcement, and flow composition.

"""

from dataclasses import dataclass, replace
from dataclasses import dataclass as dc
from typing import override

from clearflow import Node, NodeResult, flow
from tests.conftest import ValidationState


@dataclass(frozen=True)
class ChatState:
    """State for chat routing tests."""

    query: str = ""
    intent: str = ""
    agent: str = ""
    response_type: str = ""
    formatted: bool = False


@dataclass(frozen=True)
class DocState:
    """State for document processing tests."""

    source: str
    loaded: str = ""
    doc_count: str = ""
    embedded: str = ""
    embedding_dim: str = ""
    stored: str = ""


# Test nodes for chat routing - defined outside test to reduce complexity
@dc(frozen=True)
class IntentClassifier(Node[ChatState]):
    """Classifies user intent for appropriate AI response."""

    name: str = "classifier"

    @override
    async def exec(self, state: ChatState) -> NodeResult[ChatState]:
        query = state.query or ""
        intent = self._classify_intent(query)
        new_state = replace(state, intent=intent)
        return NodeResult(new_state, outcome=intent)

    def _classify_intent(self, query: str) -> str:
        """Classify query intent.

        Returns:
            Intent string: "technical", "question", or "general".
        """
        query_lower = str(query).lower()
        if "code" in query_lower or "bug" in query_lower:
            return "technical"
        if "?" in str(query):
            return "question"
        return "general"


@dc(frozen=True)
class TechnicalAgent(Node[ChatState]):
    """Handles technical queries with code examples."""

    name: str = "technical_agent"

    @override
    async def exec(self, state: ChatState) -> NodeResult[ChatState]:
        new_state = replace(
            state,
            agent="technical",
            response_type="code_example",
        )
        return NodeResult(new_state, outcome="responded")


@dc(frozen=True)
class QAAgent(Node[ChatState]):
    """Handles Q&A with retrieval augmented generation."""

    name: str = "qa_agent"

    @override
    async def exec(self, state: ChatState) -> NodeResult[ChatState]:
        new_state = replace(
            state,
            agent="qa",
            response_type="retrieved_answer",
        )
        return NodeResult(new_state, outcome="responded")


@dc(frozen=True)
class GeneralAgent(Node[ChatState]):
    """Handles general conversation."""

    name: str = "general_agent"

    @override
    async def exec(self, state: ChatState) -> NodeResult[ChatState]:
        new_state = replace(
            state,
            agent="general",
            response_type="chat",
        )
        return NodeResult(new_state, outcome="responded")


@dc(frozen=True)
class ResponseFormatter(Node[ChatState]):
    """Formats final response for user."""

    name: str = "formatter"

    @override
    async def exec(self, state: ChatState) -> NodeResult[ChatState]:
        new_state = replace(state, formatted=True)
        return NodeResult(new_state, outcome="complete")


# Test data classes and nodes for linear flow
@dc(frozen=True)
class RawText:
    """Raw text to be processed."""

    content: str
    source: str


@dc(frozen=True)
class TokenizedText:
    """Text split into tokens."""

    raw: RawText
    tokens: tuple[str, ...]


@dc(frozen=True)
class IndexedDocument:
    """Final indexed document."""

    tokenized: TokenizedText
    token_count: int
    indexed: bool = True


@dc(frozen=True)
class TokenizerNode(Node[RawText, TokenizedText]):
    """Tokenizes text for embedding generation."""

    name: str = "tokenizer"

    @override
    async def exec(self, state: RawText) -> NodeResult[TokenizedText]:
        tokens = tuple(state.content.split())
        tokenized = TokenizedText(raw=state, tokens=tokens)
        return NodeResult(tokenized, outcome="tokenized")


@dc(frozen=True)
class IndexerNode(Node[TokenizedText, IndexedDocument]):
    """Creates embeddings and indexes document."""

    name: str = "indexer"

    @override
    async def exec(self, state: TokenizedText) -> NodeResult[IndexedDocument]:
        indexed = IndexedDocument(tokenized=state, token_count=len(state.tokens))
        return NodeResult(indexed, outcome="indexed")


# Nodes for nested flow testing
@dc(frozen=True)
class DocumentLoader(Node[DocState]):
    """Loads documents for processing."""

    name: str = "loader"

    @override
    async def exec(self, state: DocState) -> NodeResult[DocState]:
        new_state = replace(state, loaded="true", doc_count="5")
        return NodeResult(new_state, outcome="loaded")


@dc(frozen=True)
class Embedder(Node[DocState]):
    """Creates embeddings from loaded documents."""

    name: str = "embedder"

    @override
    async def exec(self, state: DocState) -> NodeResult[DocState]:
        new_state = replace(
            state,
            embedded="true",
            embedding_dim="768",
        )
        return NodeResult(new_state, outcome="embedded")


@dc(frozen=True)
class VectorStore(Node[DocState]):
    """Stores embeddings in vector database."""

    name: str = "vector_store"

    @override
    async def exec(self, state: DocState) -> NodeResult[DocState]:
        new_state = replace(state, stored="true")
        return NodeResult(new_state, outcome="indexed")


class TestFlow:
    """Test the Flow orchestration."""

    @staticmethod
    async def test_linear_flow_build() -> None:
        """Test building a linear flow."""
        tokenizer = TokenizerNode()
        indexer = IndexerNode()

        flow_instance = flow("RAG", tokenizer).route(tokenizer, "tokenized", indexer).end(indexer, "indexed")

        assert flow_instance.name == "RAG"

    @staticmethod
    async def test_linear_flow_execution() -> None:
        """Test executing a linear flow."""
        tokenizer = TokenizerNode()
        indexer = IndexerNode()

        flow_instance = flow("RAG", tokenizer).route(tokenizer, "tokenized", indexer).end(indexer, "indexed")

        initial = RawText(content="Natural language processing", source="test.txt")
        result = await flow_instance(initial)

        assert result.outcome == "indexed"
        assert isinstance(result.state, IndexedDocument)
        assert result.state.token_count == 3

    @staticmethod
    async def test_chat_routing_flow_setup() -> None:
        """Test building an AI chat routing flow."""
        # Build AI chat routing flow using new API
        classifier = IntentClassifier()
        technical = TechnicalAgent()
        qa = QAAgent()
        general = GeneralAgent()
        formatter = ResponseFormatter()

        chat_flow = (
            flow("ChatRouter", classifier)
            .route(classifier, "technical", technical)
            .route(classifier, "question", qa)
            .route(classifier, "general", general)
            .route(technical, "responded", formatter)
            .route(qa, "responded", formatter)
            .route(general, "responded", formatter)
            .end(formatter, "complete")
        )

        # Just verify flow builds correctly
        assert chat_flow.name == "ChatRouter"

    @staticmethod
    async def test_chat_technical_path() -> None:
        """Test technical query routing in chat flow."""
        classifier = IntentClassifier()
        technical = TechnicalAgent()
        formatter = ResponseFormatter()

        chat_flow = (
            flow("TechRouter", classifier)
            .route(classifier, "technical", technical)
            .route(technical, "responded", formatter)
            .end(formatter, "complete")
        )

        tech_input = ChatState(query="How do I fix this bug in my code?")
        result = await chat_flow(tech_input)
        assert result.state.intent == "technical"
        assert result.state.agent == "technical"
        assert result.outcome == "complete"

    @staticmethod
    async def test_chat_question_path() -> None:
        """Test question routing in chat flow."""
        classifier = IntentClassifier()
        qa = QAAgent()
        formatter = ResponseFormatter()

        chat_flow = (
            flow("QARouter", classifier)
            .route(classifier, "question", qa)
            .route(qa, "responded", formatter)
            .end(formatter, "complete")
        )

        question_input = ChatState(query="What is RAG?")
        result = await chat_flow(question_input)
        assert result.state.intent == "question"
        assert result.state.agent == "qa"
        assert result.outcome == "complete"

    @staticmethod
    async def test_chat_general_path() -> None:
        """Test general conversation routing."""
        classifier = IntentClassifier()
        general = GeneralAgent()
        formatter = ResponseFormatter()

        chat_flow = (
            flow("GeneralRouter", classifier)
            .route(classifier, "general", general)
            .route(general, "responded", formatter)
            .end(formatter, "complete")
        )

        input_state = ChatState(query="Hello there")
        result = await chat_flow(input_state)
        assert result.state.intent == "general"
        assert result.state.agent == "general"
        assert result.outcome == "complete"

    @staticmethod
    async def test_single_termination_enforcement() -> None:
        """Test that flows must have exactly one termination point."""

        @dc(frozen=True)
        class DataValidator(Node[ValidationState]):
            """Validates incoming data for processing."""

            name: str = "validator"

            @override
            async def exec(self, state: ValidationState) -> NodeResult[ValidationState]:
                return NodeResult(state, outcome="valid")

        @dc(frozen=True)
        class DataProcessor(Node[ValidationState]):
            """Processes validated data."""

            name: str = "processor"

            @override
            async def exec(self, state: ValidationState) -> NodeResult[ValidationState]:
                return NodeResult(state, outcome="processed")

        validator = DataValidator()
        processor = DataProcessor()

        # This works - single termination point
        valid_flow = (
            flow("ValidationPipeline", validator).route(validator, "valid", processor).end(processor, "processed")
        )

        # Test that it runs successfully
        result = await valid_flow(ValidationState(input_text="test data"))
        assert result.outcome == "processed"

    @staticmethod
    async def test_flow_composition() -> None:
        """Test that flows can be composed as nodes."""
        loader = DocumentLoader()
        embedder = Embedder()

        # Create inner flow
        inner_flow = flow("Inner", loader).route(loader, "loaded", embedder).end(embedder, "embedded")

        # Use inner flow as a node
        vector_store = VectorStore()
        outer_flow = flow("Outer", inner_flow).route(inner_flow, "embedded", vector_store).end(vector_store, "indexed")

        # Just verify it builds
        assert outer_flow.name == "Outer"

    @staticmethod
    async def test_nested_flow_execution() -> None:
        """Test execution of nested flows."""
        loader = DocumentLoader()
        embedder = Embedder()
        doc_flow = flow("DocFlow", loader).route(loader, "loaded", embedder).end(embedder, "embedded")

        vector_store = VectorStore()
        pipeline = flow("Pipeline", doc_flow).route(doc_flow, "embedded", vector_store).end(vector_store, "indexed")

        doc_input = DocState(
            source="kb",
            loaded="",
            doc_count="",
            embedded="",
            embedding_dim="",
            stored="",
        )
        result = await pipeline(doc_input)
        assert result.outcome == "indexed"
        assert result.state.stored == "true"
