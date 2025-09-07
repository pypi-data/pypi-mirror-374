"""Decision and Error Handler nodes for final trading decisions."""

from dataclasses import dataclass, field
from typing import override

import dspy
import openai
from pydantic import ValidationError

from clearflow import Node, NodeResult
from examples.portfolio_analysis.shared.models import AnalysisError
from examples.portfolio_analysis.specialists.compliance.models import ComplianceError, ComplianceReview
from examples.portfolio_analysis.specialists.decision.models import TradingDecision
from examples.portfolio_analysis.specialists.decision.signature import TradingDecisionSignature
from examples.portfolio_analysis.specialists.risk.models import RiskLimitError


@dataclass(frozen=True)
class DecisionNode(Node[ComplianceReview, TradingDecision]):
    """Final decision node using DSPy for structured trading decision."""

    name: str = "final_decision"
    _predict: dspy.Predict = field(init=False, repr=False)

    def __post_init__(self) -> None:
        """Initialize DSPy predictor."""
        super().__post_init__()
        object.__setattr__(self, "_predict", dspy.Predict(TradingDecisionSignature))

    @override
    async def exec(self, state: ComplianceReview) -> NodeResult[TradingDecision]:
        """Create final trading decision using DSPy.

        Returns:
            NodeResult with trading decision.
        """

        try:
            # Use DSPy to get structured trading decision
            prediction = self._predict(compliance_review=state)
            decision: TradingDecision = prediction.trading_decision

            return NodeResult(decision, outcome="decision_ready")

        except (ValidationError, openai.OpenAIError, ValueError, TypeError) as exc:
            # Create minimal trading decision on error
            decision = TradingDecision(
                approved_changes=(),
                execution_plan="Hold - unable to process decision",
                monitoring_requirements=("Monitor system status",),
                audit_trail=f"Decision processing failed: {exc!s}",
                decision_status="hold",
            )
            return NodeResult(decision, outcome="decision_ready")


@dataclass(frozen=True)
class ErrorHandler(Node[AnalysisError | RiskLimitError | ComplianceError, TradingDecision]):
    """Error handler node that converts errors to a hold decision."""

    name: str = "error_handler"

    @override
    async def exec(self, state: AnalysisError | RiskLimitError | ComplianceError) -> NodeResult[TradingDecision]:
        """Convert error state to a conservative trading decision.

        Returns:
            NodeResult with hold trading decision.
        """
        # Create error message based on error type
        if isinstance(state, AnalysisError):
            error_msg = f"Analysis Error: {state.error_message}"
        elif isinstance(state, RiskLimitError):
            error_msg = f"Risk Limit Exceeded: {', '.join(state.exceeded_limits)}"
        else:  # ComplianceError
            error_msg = f"Compliance Violation: {len(state.violations)} violations"

        # Create hold decision
        decision = TradingDecision(
            approved_changes=(),
            execution_plan="HOLD - Error in analysis pipeline",
            monitoring_requirements=(
                "Monitor error resolution",
                "Review system status",
                f"Error details: {error_msg}",
            ),
            audit_trail=f"Decision halted due to: {error_msg} at {state.failed_stage}",
            decision_status="hold",
        )
        return NodeResult(decision, outcome="error_handled")
