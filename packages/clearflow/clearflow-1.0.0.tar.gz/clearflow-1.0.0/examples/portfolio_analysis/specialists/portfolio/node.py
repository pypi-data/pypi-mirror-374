"""Portfolio Manager node for strategic allocation recommendations."""

from dataclasses import dataclass, field
from typing import override

import dspy
import openai
from pydantic import ValidationError

from clearflow import Node, NodeResult
from examples.portfolio_analysis.shared.models import AnalysisError
from examples.portfolio_analysis.specialists.portfolio.models import AllocationChange, PortfolioRecommendations
from examples.portfolio_analysis.specialists.portfolio.signature import PortfolioManagerSignature
from examples.portfolio_analysis.specialists.risk.models import RiskAssessment


@dataclass(frozen=True)
class PortfolioManager(Node[RiskAssessment, PortfolioRecommendations | AnalysisError]):
    """AI-powered portfolio manager using DSPy for structured recommendations."""

    name: str = "portfolio_manager"
    _predict: dspy.Predict = field(init=False, repr=False)

    def __post_init__(self) -> None:
        """Initialize DSPy predictor."""
        super().__post_init__()
        object.__setattr__(self, "_predict", dspy.Predict(PortfolioManagerSignature))

    @override
    async def prep(self, state: RiskAssessment) -> RiskAssessment:
        """Pre-execution hook to show progress.

        Returns:
            State passed through unchanged.
        """
        print("\n🤖 PORTFOLIO MANAGER")
        print("   └─ Developing strategic allocation recommendations...")
        return state

    @staticmethod
    def _group_allocation_changes(
        allocation_changes: tuple[AllocationChange, ...],
    ) -> tuple[tuple[AllocationChange, ...], tuple[AllocationChange, ...]]:
        """Group allocation changes into increases and decreases.

        Returns:
            Tuple of (increases, decreases) allocation changes.
        """
        increases = tuple(c for c in allocation_changes if c.recommended_allocation > c.current_allocation)
        decreases = tuple(c for c in allocation_changes if c.recommended_allocation < c.current_allocation)
        return increases, decreases

    @staticmethod
    def _display_allocation_increases(increases: tuple[AllocationChange, ...]) -> None:
        """Display recommended allocation increases."""
        if increases:
            print("   • Recommended Increases:")
            for change in increases[:3]:
                delta = change.recommended_allocation - change.current_allocation
                print(f"     - {change.symbol}: +{delta:.1f}% (to {change.recommended_allocation:.1f}%)")

    @staticmethod
    def _display_allocation_decreases(decreases: tuple[AllocationChange, ...]) -> None:
        """Display recommended allocation decreases."""
        if decreases:
            print("   • Recommended Decreases:")
            for change in decreases[:3]:
                delta = change.current_allocation - change.recommended_allocation
                print(f"     - {change.symbol}: -{delta:.1f}% (to {change.recommended_allocation:.1f}%)")

    def _display_portfolio_recommendations(self, recommendations: PortfolioRecommendations) -> None:
        """Display portfolio recommendation details."""
        print("\n   💼 Portfolio Adjustments:")
        increases, decreases = self._group_allocation_changes(recommendations.allocation_changes)
        self._display_allocation_increases(increases)
        self._display_allocation_decreases(decreases)
        print(f"   • Strategy: {recommendations.investment_thesis[:100]}...")
        print(f"   • Timeline: {recommendations.execution_timeline}")

    @override
    async def post(
        self, result: NodeResult[PortfolioRecommendations | AnalysisError]
    ) -> NodeResult[PortfolioRecommendations | AnalysisError]:
        """Post-execution hook to show completion.

        Returns:
            Result passed through unchanged.
        """
        if isinstance(result.state, AnalysisError):
            print("   ❌ Portfolio management failed")
        else:
            print("   ✔ Recommendations generated")
            self._display_portfolio_recommendations(result.state)
        return result

    @override
    async def exec(self, state: RiskAssessment) -> NodeResult[PortfolioRecommendations | AnalysisError]:
        """Generate portfolio recommendations using DSPy.

        Returns:
            NodeResult with portfolio recommendations or analysis error.
        """

        # Check if risk is too extreme for adjustments
        if state.risk_level == "extreme":
            error = AnalysisError(
                error_type="extreme_risk",
                error_message="Risk level too high for portfolio adjustments",
                failed_stage="PORTFOLIO MANAGER (portfolio_manager)",
                market_data=None,
            )
            return NodeResult(error, outcome="analysis_failed")

        try:
            # Use DSPy to get structured recommendations
            prediction = self._predict(risk_assessment=state)
            recommendations: PortfolioRecommendations = prediction.recommendations

            return NodeResult(recommendations, outcome="recommendations_ready")

        except (ValidationError, openai.OpenAIError, ValueError, TypeError) as exc:
            error = AnalysisError(
                error_type="pm_analysis_failed",
                error_message=f"Portfolio management analysis failed: {exc!s}",
                failed_stage="PORTFOLIO MANAGER (portfolio_manager)",
                market_data=None,
            )
            return NodeResult(error, outcome="analysis_failed")
