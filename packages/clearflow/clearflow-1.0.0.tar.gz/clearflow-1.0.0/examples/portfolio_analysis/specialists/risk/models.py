"""Data models for Risk Analyst."""

from typing import Literal

from pydantic import Field
from pydantic.dataclasses import dataclass


@dataclass(frozen=True)
class RiskMetrics:
    """Portfolio risk calculations."""

    value_at_risk: float = Field(gt=0, description="Value at Risk (VaR) in dollars")
    max_drawdown: float = Field(ge=0, le=1, description="Maximum potential loss as decimal")
    concentration_risk: dict[str, float] = Field(description="Risk concentration by sector/asset")
    correlation_warning: bool = Field(description="Flag for high correlation issues")


@dataclass(frozen=True)
class RiskAssessment:
    """Stage 3: Risk analysis of quantitative recommendations."""

    risk_metrics: RiskMetrics = Field(description="Calculated risk metrics")
    risk_level: Literal["low", "medium", "high", "extreme"] = Field(description="Overall risk classification")
    stress_test_results: dict[str, float] = Field(description="Scenario analysis outcomes")
    risk_warnings: tuple[str, ...] = Field(description="Specific risk concerns identified")
    risk_summary: str = Field(max_length=500, description="Risk analysis summary")


@dataclass(frozen=True)
class RiskLimitError:
    """Error state when risk limits are exceeded."""

    exceeded_limits: tuple[str, ...] = Field(description="List of exceeded risk limits")
    risk_metrics: RiskMetrics = Field(description="Current risk metrics")
    recommendations: tuple[str, ...] = Field(description="Risk mitigation suggestions")
    failed_stage: str = Field(description="Stage where limit was exceeded")
