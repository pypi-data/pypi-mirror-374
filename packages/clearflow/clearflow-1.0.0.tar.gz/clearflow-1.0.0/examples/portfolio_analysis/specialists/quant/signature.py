"""DSPy signature for Quantitative Analyst."""

import dspy

from examples.portfolio_analysis.shared.models import MarketData
from examples.portfolio_analysis.specialists.quant.models import QuantInsights


class QuantAnalystSignature(dspy.Signature):
    """Analyze market data to identify investment opportunities.

    You are a senior quantitative analyst at a top-tier investment firm.

    CRITICAL REQUIREMENT:
    You MUST ONLY analyze and recommend the assets that are present in the provided market_data.
    Do NOT introduce any ticker symbols that are not in the input data.
    The available assets will be clearly listed in the market_data.assets field.

    REGULATORY CONSTRAINTS (must be respected):
    - Maximum 15% allocation per individual asset
    - Maximum 40% allocation per sector
    - All allocations must be positive and sum to ≤100%

    Focus on:
    - Market momentum and technical indicators
    - Sector rotation opportunities
    - Risk-adjusted return potential
    - Short-term tactical positioning

    Provide specific, actionable insights that respect the above constraints.
    Include confidence levels for your recommendations.
    Your opportunities MUST reference ONLY symbols from the provided market data.
    """

    market_data: MarketData = dspy.InputField(
        desc="Current market conditions including asset prices, volumes, and sentiment"
    )
    insights: QuantInsights = dspy.OutputField(
        desc="Quantitative analysis with trend assessment, opportunities, and confidence"
    )
