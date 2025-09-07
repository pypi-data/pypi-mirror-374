"""Shared data models used across agents."""

from typing import Literal

from pydantic import Field
from pydantic.dataclasses import dataclass


@dataclass(frozen=True)
class AssetData:
    """Individual asset market data."""

    symbol: str = Field(description="Asset ticker symbol")
    price: float = Field(gt=0, description="Current asset price")
    volume: int = Field(ge=0, description="Trading volume")
    volatility: float = Field(ge=0, le=1, description="30-day volatility as decimal")
    momentum: float = Field(ge=-1, le=1, description="Price momentum indicator")
    sector: str = Field(description="Industry sector classification")


@dataclass(frozen=True)
class MarketData:
    """Stage 1: Raw market data input for analysis."""

    assets: tuple[AssetData, ...] = Field(description="List of assets to analyze")
    market_date: str = Field(description="Date of market data snapshot")
    risk_free_rate: float = Field(ge=0, le=0.1, description="Current risk-free rate")
    market_sentiment: Literal["bullish", "bearish", "neutral"] = Field(description="Overall market sentiment")


@dataclass(frozen=True)
class AnalysisError:
    """Error state when analysis fails."""

    error_type: str = Field(description="Type of error encountered")
    error_message: str = Field(description="Detailed error message")
    failed_stage: str = Field(description="Stage where error occurred")
    market_data: MarketData | None = Field(default=None, description="Original input for retry")
