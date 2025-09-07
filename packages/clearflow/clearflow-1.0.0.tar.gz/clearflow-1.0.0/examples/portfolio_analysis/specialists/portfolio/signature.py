"""DSPy signature for Portfolio Manager."""

import dspy

from examples.portfolio_analysis.specialists.portfolio.models import PortfolioRecommendations
from examples.portfolio_analysis.specialists.risk.models import RiskAssessment


class PortfolioManagerSignature(dspy.Signature):
    """Develop strategic portfolio allocation recommendations.

    You are a seasoned portfolio manager making allocation decisions.

    CRITICAL REQUIREMENT:
    You MUST ONLY recommend allocation changes for assets present in the risk_assessment.
    Do NOT introduce any new ticker symbols not found in the input data.
    Your allocation_changes MUST use ONLY the symbols that have been analyzed.

    MANDATORY REGULATORY LIMITS:
    - Maximum 15% allocation per asset
    - Maximum 40% allocation per sector
    - Allocations must be non-negative and sum to ≤100%

    Consider:
    - Risk-adjusted returns across opportunities
    - Portfolio diversification requirements
    - Implementation complexity and costs
    - Market timing and execution strategy

    Balance opportunity with prudent risk management.
    All AllocationChange entries MUST reference ONLY symbols from the risk assessment.
    """

    risk_assessment: RiskAssessment = dspy.InputField(desc="Risk analysis including metrics and warnings")
    recommendations: PortfolioRecommendations = dspy.OutputField(
        desc="Strategic allocation changes with thesis and timeline"
    )
