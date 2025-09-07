"""Risk Analyst node for portfolio risk assessment."""

from dataclasses import dataclass, field
from typing import override

import dspy
import openai
from pydantic import ValidationError

from clearflow import Node, NodeResult
from examples.portfolio_analysis.specialists.quant.models import QuantInsights
from examples.portfolio_analysis.specialists.risk.models import RiskAssessment, RiskLimitError, RiskMetrics
from examples.portfolio_analysis.specialists.risk.signature import RiskAnalystSignature


@dataclass(frozen=True)
class RiskAnalyst(Node[QuantInsights, RiskAssessment | RiskLimitError]):
    """AI-powered risk analyst using DSPy for structured risk assessment."""

    name: str = "risk_analyst"
    _predict: dspy.Predict = field(init=False, repr=False)

    def __post_init__(self) -> None:
        """Initialize DSPy predictor."""
        super().__post_init__()
        object.__setattr__(self, "_predict", dspy.Predict(RiskAnalystSignature))

    @override
    async def prep(self, state: QuantInsights) -> QuantInsights:
        """Pre-execution hook to show progress.

        Returns:
            State passed through unchanged.
        """
        print("\n🤖 RISK ANALYST")
        print("   └─ Evaluating portfolio risk metrics and stress testing...")
        return state

    @staticmethod
    def _display_risk_issues(error: RiskLimitError) -> None:
        """Display risk limit violations."""
        print("\n   ⚠️  Risk Issues:")
        for limit in error.exceeded_limits:
            print(f"   • {limit}")

    @staticmethod
    def _display_risk_assessment(assessment: RiskAssessment) -> None:
        """Display risk assessment details."""
        print("\n   🛡️ Risk Metrics:")
        metrics = assessment.risk_metrics
        print(f"   • Value at Risk (95%): ${metrics.value_at_risk:,.0f}")
        print(f"   • Max Drawdown: {metrics.max_drawdown:.1%}")
        print(f"   • Risk Level: {assessment.risk_level.upper()}")
        # Display concentration risks if any
        if metrics.concentration_risk:
            print("   • Concentration Risks:")
            for asset, concentration in list(metrics.concentration_risk.items())[:3]:
                print(f"     - {asset}: {concentration:.1%}")
        # Display top warnings
        if assessment.risk_warnings:
            print("   • Key Warnings:")
            for warning in assessment.risk_warnings[:2]:
                print(f"     - {warning}")
        print(f"   • Overall Assessment: {assessment.risk_summary}")

    @override
    async def post(
        self, result: NodeResult[RiskAssessment | RiskLimitError]
    ) -> NodeResult[RiskAssessment | RiskLimitError]:
        """Post-execution hook to show completion.

        Returns:
            Result passed through unchanged.
        """
        if isinstance(result.state, RiskLimitError):
            print("   ❌ Risk limits exceeded")
            self._display_risk_issues(result.state)
        else:
            print("   ✔ Risk assessment complete")
            self._display_risk_assessment(result.state)
        return result

    @override
    async def exec(self, state: QuantInsights) -> NodeResult[RiskAssessment | RiskLimitError]:
        """Perform risk analysis using DSPy structured prediction.

        Returns:
            NodeResult with risk assessment or risk limit error.
        """

        try:
            # Use DSPy to get structured risk assessment
            # The AI will determine risk acceptability based on context
            prediction = self._predict(quant_insights=state)
            assessment: RiskAssessment = prediction.risk_assessment

            # Let AI determine the outcome based on its risk assessment
            # High/extreme risks should be flagged by the AI's judgment
            if assessment.risk_level == "extreme":
                # AI has determined risks are unacceptable
                error = RiskLimitError(
                    exceeded_limits=tuple(assessment.risk_warnings[:3]),  # Top warnings
                    risk_metrics=assessment.risk_metrics,
                    recommendations=tuple(assessment.risk_warnings[3:6]),  # Recommendations
                    failed_stage="RISK ANALYST (risk_analyst)",
                )
                return NodeResult(error, outcome="risk_limits_exceeded")

            return NodeResult(assessment, outcome="risk_acceptable")

        except (ValidationError, openai.OpenAIError, ValueError, TypeError) as exc:
            # Create minimal error for exception handling
            error_metrics = RiskMetrics(
                value_at_risk=0.01,  # Minimum positive value for validation
                max_drawdown=0.0,
                concentration_risk={},
                correlation_warning=False,
            )
            error = RiskLimitError(
                exceeded_limits=(f"Analysis failed: {exc!s}",),
                risk_metrics=error_metrics,
                recommendations=("Retry risk analysis", "Check input data quality"),
                failed_stage="RISK ANALYST (risk_analyst)",
            )
            return NodeResult(error, outcome="risk_limits_exceeded")
