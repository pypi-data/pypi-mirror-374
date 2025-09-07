"""Data models for Trading Decision."""

from typing import Literal

from pydantic import Field
from pydantic.dataclasses import dataclass

from examples.portfolio_analysis.specialists.portfolio.models import AllocationChange


@dataclass(frozen=True)
class TradingDecision:
    """Stage 6: Final approved portfolio decision."""

    approved_changes: tuple[AllocationChange, ...] = Field(description="Final approved allocation changes")
    execution_plan: str = Field(description="Detailed execution instructions")
    monitoring_requirements: tuple[str, ...] = Field(description="Ongoing monitoring needs")
    audit_trail: str = Field(description="Complete decision reasoning chain")
    decision_status: Literal["execute", "hold", "escalate"] = Field(description="Final decision status")
