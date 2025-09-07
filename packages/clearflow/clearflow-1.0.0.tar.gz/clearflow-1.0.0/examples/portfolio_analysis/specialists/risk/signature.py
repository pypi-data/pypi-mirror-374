"""DSPy signatures for Risk Analyst."""

import dspy

from examples.portfolio_analysis.specialists.quant.models import QuantInsights
from examples.portfolio_analysis.specialists.risk.models import RiskAssessment, RiskLimitError


class RiskAnalystSignature(dspy.Signature):
    """Perform holistic risk analysis using professional judgment.

    You are a senior risk analyst evaluating portfolio risks contextually.

    CRITICAL REQUIREMENT:
    You MUST ONLY assess risks for the assets identified in the quant_insights.
    Do NOT reference any ticker symbols that are not in the opportunities provided.
    Focus your analysis exclusively on the symbols present in the input.

    Be aware of regulatory constraints:
    - Maximum 15% per asset, 40% per sector
    - These are hard limits that cannot be exceeded

    Assess risks holistically considering:
    - VaR relative to portfolio size and investor risk tolerance
    - Drawdown risk in context of current market volatility
    - Concentration risks that could amplify losses
    - Systemic and correlation risks
    - Stress scenarios based on historical precedents

    Use your professional judgment to:
    - Set risk_level (low/medium/high/extreme) based on overall assessment
    - Generate realistic risk metrics appropriate for the portfolio
    - Identify material risks that need attention
    - Consider market conditions when evaluating acceptability

    Focus on actionable risk insights, not arbitrary thresholds.
    Your concentration_risk MUST reference ONLY symbols from the quant insights.
    """

    quant_insights: QuantInsights = dspy.InputField(desc="Quantitative analysis with identified opportunities")
    risk_assessment: RiskAssessment = dspy.OutputField(desc="Comprehensive risk metrics and warnings")


class RiskLimitSignature(dspy.Signature):
    """Evaluate if risk limits are exceeded and recommend mitigation."""

    risk_assessment: RiskAssessment = dspy.InputField(desc="Risk assessment with metrics")
    risk_limit_check: RiskLimitError | None = dspy.OutputField(
        desc="Risk limit error if thresholds exceeded, None if acceptable"
    )
