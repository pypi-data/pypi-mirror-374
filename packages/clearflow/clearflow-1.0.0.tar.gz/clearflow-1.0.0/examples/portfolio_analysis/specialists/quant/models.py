"""Data models for Quantitative Analyst."""

from typing import Literal

from pydantic import Field, field_validator
from pydantic.dataclasses import dataclass


@dataclass(frozen=True)
class OpportunitySignal:
    """Individual investment opportunity identified by quant analysis."""

    symbol: str = Field(description="Asset symbol for this opportunity")
    signal_type: Literal["buy", "sell", "hold"] = Field(description="Trading signal")
    confidence: float = Field(ge=0, le=1, description="Confidence score 0-1")
    target_allocation: float = Field(ge=0, le=100, description="Recommended portfolio percentage")
    reasoning: str = Field(description="Rationale for this signal")


@dataclass(frozen=True)
class QuantInsights:
    """Stage 2: Quantitative analysis insights and opportunities."""

    market_trend: Literal["bullish", "bearish", "sideways"] = Field(description="Overall market trend assessment")
    sector_analysis: dict[str, float] = Field(description="Sector momentum scores (-1 to 1)")
    opportunities: tuple[OpportunitySignal, ...] = Field(description="Identified trading opportunities")
    overall_confidence: float = Field(ge=0, le=1, description="Overall analysis confidence")
    analysis_summary: str = Field(max_length=500, description="Brief summary of analysis")

    @field_validator("sector_analysis")
    @classmethod
    def validate_sector_scores(cls, v: dict[str, float]) -> dict[str, float]:
        """Ensure sector scores are within valid range.

        Returns:
            Validated sector scores dictionary.

        Raises:
            ValueError: If any sector score is outside [-1, 1] range.
        """
        for sector, score in v.items():
            if not -1 <= score <= 1:
                msg = f"{cls.__name__}: Sector score for {sector} must be between -1 and 1"
                raise ValueError(msg)
        return v
