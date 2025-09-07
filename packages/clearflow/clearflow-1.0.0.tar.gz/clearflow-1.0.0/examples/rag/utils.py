"""Utilities for LLM and embedding operations."""

import os
from pathlib import Path
from typing import cast

import numpy as np
import numpy.typing as npt
from dotenv import load_dotenv
from openai import OpenAI


def _load_env() -> None:
    """Load environment variables from .env file."""
    # Try multiple locations for the .env file
    env_locations = [
        Path(".env"),  # Current directory
        Path("../.env"),  # Parent directory
        Path("../../.env"),  # Grandparent directory (repo root)
    ]

    for env_path in env_locations:
        if env_path.exists():
            load_dotenv(env_path)
            break


# Load environment variables before initializing client
_load_env()

# Initialize OpenAI client
api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    msg = "OPENAI_API_KEY not found. Please set it in .env file at project root."
    raise ValueError(msg)

client = OpenAI(api_key=api_key)


def get_embedding(text: str) -> npt.NDArray[np.float32]:
    """Get embedding vector for text using OpenAI's API.

    Args:
        text: Text to embed

    Returns:
        Embedding vector as numpy array
    """
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text,
    )
    embedding = response.data[0].embedding
    return np.array(embedding, dtype=np.float32)


def call_llm(prompt: str) -> str:
    """Call OpenAI's chat completion API.

    Args:
        prompt: Prompt for the LLM

    Returns:
        Generated text response
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=200,
    )
    content = response.choices[0].message.content
    return cast("str", content)


def fixed_size_chunk(text: str, chunk_size: int = 500, overlap: int = 50) -> tuple[str, ...]:
    """Split text into fixed-size chunks with overlap.

    Args:
        text: Text to chunk
        chunk_size: Maximum characters per chunk
        overlap: Number of overlapping characters between chunks

    Returns:
        Tuple of text chunks
    """
    if not text:
        return ()

    text_length = len(text)

    # Build chunks using a generator expression
    return tuple(
        text[start : min(start + chunk_size, text_length)].strip()
        for start in range(0, text_length, chunk_size - overlap)
        if text[start : min(start + chunk_size, text_length)].strip()
    )


if __name__ == "__main__":
    # Test embedding function
    print("Testing OpenAI connection...")
    try:
        test_text = "Hello, world!"
        embedding = get_embedding(test_text)
        print(f"✅ Successfully created embedding with dimension: {embedding.shape[0]}")

        test_prompt = "Say 'API is working' if you can read this."
        response = call_llm(test_prompt)
        print(f"✅ LLM response: {response}")
    except (KeyError, ValueError, TypeError) as e:
        print(f"❌ Error: {e}")
        print("Please ensure OPENAI_API_KEY is set in your environment")
