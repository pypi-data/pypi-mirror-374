"""DSPy signatures for Compliance Officer."""

import dspy

from examples.portfolio_analysis.specialists.compliance.models import ComplianceError, ComplianceReview
from examples.portfolio_analysis.specialists.portfolio.models import PortfolioRecommendations


class ComplianceOfficerSignature(dspy.Signature):
    """Review portfolio recommendations for regulatory compliance.

    You are a chief compliance officer ensuring regulatory adherence.

    CRITICAL REQUIREMENT:
    You MUST ONLY review allocations for the symbols present in the recommendations.
    Do NOT reference any ticker symbols not found in the allocation_changes.

    Check for:
    - Position limit violations (max 15% per asset)
    - Sector concentration limits (max 40% per sector)
    - Documentation requirements
    - Execution timeline appropriateness
    - Regulatory reporting needs

    Be thorough and conservative in compliance assessments.
    Focus your review ONLY on the symbols provided in the portfolio recommendations.
    """

    recommendations: PortfolioRecommendations = dspy.InputField(desc="Portfolio manager's allocation recommendations")
    compliance_review: ComplianceReview = dspy.OutputField(
        desc="Detailed compliance checks and overall approval status"
    )


class ComplianceViolationSignature(dspy.Signature):
    """Identify compliance violations and required actions."""

    recommendations: PortfolioRecommendations = dspy.InputField(desc="Portfolio recommendations to check")
    compliance_error: ComplianceError | None = dspy.OutputField(
        desc="Compliance error if violations found, None if compliant"
    )
