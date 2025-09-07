"""Configuration for DSPy and OpenAI integration."""

import os
from pathlib import Path

import dspy
from dotenv import load_dotenv


def configure_dspy(model: str = "gpt-5-nano-2025-08-07", temperature: float = 1.0) -> None:
    """Configure DSPy with OpenAI backend.

    Args:
        model: OpenAI model to use (default: gpt-5-nano for best performance)
        temperature: Temperature for responses (1.0 for gpt-5-nano requirement)

    Raises:
        ValueError: If OPENAI_API_KEY is not found in environment variables.
    """
    # Load environment variables
    _load_env()

    # Get API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        msg = "OPENAI_API_KEY not found in environment variables"
        raise ValueError(msg)

    # Configure DSPy with OpenAI
    # Note: gpt-5-nano requires max_tokens >= 16000 and temperature=1.0
    lm = dspy.LM(
        model=f"openai/{model}",
        api_key=api_key,
        temperature=temperature,
        max_tokens=16000,  # Required for reasoning models
    )

    dspy.configure(lm=lm)


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


# Financial thresholds and limits
class FinancialThresholds:
    """Centralized financial thresholds and limits."""

    # Risk limits
    PORTFOLIO_VAR_LIMIT = 2_000_000  # $2M VaR limit
    MAX_DRAWDOWN_THRESHOLD = 0.20  # 20% max drawdown
    HIGH_VAR_THRESHOLD = 1_800_000  # $1.8M high VaR warning

    # Position limits
    MAX_ALLOCATION_PER_ASSET = 15.0  # 15% max per asset
    MIN_ALLOCATION = 2.0  # 2% minimum position
    HIGH_CONCENTRATION_LIMIT = 0.25  # 25% concentration warning

    # Sector limits
    MAX_SECTOR_ALLOCATION = 40.0  # 40% max per sector

    # Confidence thresholds
    MIN_CONFIDENCE = 0.5  # Minimum confidence for signals
    HIGH_CONFIDENCE = 0.8  # High confidence threshold


class ComplianceRules:
    """Centralized compliance rules."""

    POSITION_LIMIT = 15.0  # 15% max position size
    SECTOR_LIMIT = 40.0  # 40% max sector allocation
    MIN_THESIS_LENGTH = 50  # Minimum investment thesis length
    MAX_VIOLATIONS_FOR_ESCALATION = 2  # Escalate if > 2 violations
