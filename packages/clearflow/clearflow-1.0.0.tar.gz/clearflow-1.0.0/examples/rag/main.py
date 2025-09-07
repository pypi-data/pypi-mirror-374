#!/usr/bin/env python3
"""Main entry point for RAG example."""

import asyncio
import os
import sys

from dotenv import load_dotenv

from examples.rag.models import QueryState, RAGState
from examples.rag.rag_flow import create_offline_flow, create_online_flow


def get_sample_documents() -> tuple[str, ...]:
    """Get sample documents for indexing.

    Returns:
        Tuple of document strings
    """
    return (
        # ClearFlow framework
        """ClearFlow is a type-safe workflow orchestration framework for Python.
        It provides 100% test coverage and zero dependencies.
        Nodes transform immutable state through explicit routing.
        Single termination enforcement ensures no ambiguous endings.
        To install: pip install clearflow""",
        # Fictional medical device
        """NeurAlign M7 is a revolutionary non-invasive neural alignment device.
        Targeted magnetic resonance technology increases neuroplasticity in specific brain regions.
        Clinical trials showed 72% improvement in PTSD treatment outcomes.
        Developed by Cortex Medical in 2024 as an adjunct to standard cognitive therapy.
        Portable design allows for in-home use with remote practitioner monitoring.""",
        # Made-up historical event
        """The Velvet Revolution of Caldonia (1967-1968) ended Generalissimo Verak's 40-year rule.
        Led by poet Eliza Markovian through underground literary societies.
        Culminated in the Great Silence Protest with 300,000 silent protesters.
        First democratic elections held in March 1968 with 94% voter turnout.
        Became a model for non-violent political transitions in neighboring regions.""",
        # Fictional technology
        """Q-Mesh is QuantumLeap Technologies' instantaneous data synchronization protocol.
        Utilizes directed acyclic graph consensus for 500,000 transactions per second.
        Consumes 95% less energy than traditional blockchain systems.
        Adopted by three central banks for secure financial data transfer.
        Released in February 2024 after five years of development in stealth mode.""",
        # Made-up scientific research
        """Harlow Institute's Mycelium Strain HI-271 removes 99.7% of PFAS from contaminated soil.
        Engineered fungi create symbiotic relationships with native soil bacteria.
        Breaks down "forever chemicals" into non-toxic compounds within 60 days.
        Field tests successfully remediated previously permanently contaminated industrial sites.
        Deployment costs 80% less than traditional chemical extraction methods.""",
    )


def print_header() -> None:
    """Print application header."""
    print("=" * 60)
    print("ClearFlow RAG Example")
    print("=" * 60)
    print()


def get_query() -> str:
    """Get query from command line or use default.

    Returns:
        Query string
    """
    # Check for command line argument
    if len(sys.argv) > 1:
        # Join all arguments after the script name
        query = " ".join(sys.argv[1:])
        # Remove leading -- if present
        query = query.removeprefix("--")
    else:
        query = "How to install ClearFlow?"

    return query


async def run_rag_pipeline() -> None:
    """Run the complete RAG pipeline."""
    print_header()

    # Get sample documents
    documents = get_sample_documents()
    print(f"📚 Loaded {len(documents)} documents for indexing\n")

    # Create initial state
    initial_state = RAGState(documents=documents)

    # Run offline indexing
    print("=" * 60)
    print("OFFLINE: Document Indexing")
    print("=" * 60)
    offline_flow = create_offline_flow()
    indexed_result = await offline_flow(initial_state)
    indexed_state = indexed_result.state
    print()

    # Get query
    query = get_query()

    # Create query state from indexed state
    query_state = QueryState(
        documents=indexed_state.documents,
        chunks=indexed_state.chunks,
        embeddings=indexed_state.embeddings,
        index=indexed_state.index,
        query=query,
    )

    # Run online query
    print("=" * 60)
    print("ONLINE: Query Processing")
    print("=" * 60)
    online_flow = create_online_flow()
    result = await online_flow(query_state)

    # Display final answer
    print("\n" + "=" * 60)
    print("FINAL ANSWER")
    print("=" * 60)
    print(f"Question: {result.state.query}")
    print(f"Answer: {result.state.answer}")


async def main() -> None:
    """Main application entry point."""
    # Load environment variables
    load_dotenv()

    # Check for OpenAI API key
    if not os.environ.get("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable is not set")
        print("Please set it in your .env file or environment")
        print("\nExample:")
        print("  export OPENAI_API_KEY='your-api-key-here'")
        sys.exit(1)

    try:
        await run_rag_pipeline()
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user")
        sys.exit(0)


if __name__ == "__main__":
    asyncio.run(main())
