"""DSPy signature for Trading Decision."""

import dspy

from examples.portfolio_analysis.specialists.compliance.models import ComplianceReview
from examples.portfolio_analysis.specialists.decision.models import TradingDecision


class TradingDecisionSignature(dspy.Signature):
    """Finalize trading decision based on compliance review.

    You are the head of trading finalizing execution plans.

    CRITICAL REQUIREMENT:
    You MUST ONLY approve changes for symbols that were in the compliance review.
    Do NOT introduce any new ticker symbols.

    Determine:
    - Which allocation changes to execute
    - Detailed execution instructions
    - Monitoring requirements
    - Escalation needs

    Create a clear, actionable trading plan.
    Your approved_changes MUST reference ONLY symbols from the compliance review.
    """

    compliance_review: ComplianceReview = dspy.InputField(desc="Compliance review with checks and approval status")
    trading_decision: TradingDecision = dspy.OutputField(desc="Final trading decision with execution plan")
