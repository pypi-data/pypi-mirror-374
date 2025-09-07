"""Quantitative Analyst node for market analysis."""

from dataclasses import dataclass, field
from operator import itemgetter
from typing import override

import dspy
import openai
from pydantic import ValidationError

from clearflow import Node, NodeResult
from examples.portfolio_analysis.shared.models import AnalysisError, MarketData
from examples.portfolio_analysis.specialists.quant.models import OpportunitySignal, QuantInsights
from examples.portfolio_analysis.specialists.quant.signature import QuantAnalystSignature


@dataclass(frozen=True)
class QuantAnalyst(Node[MarketData, QuantInsights | AnalysisError]):
    """AI-powered quantitative analyst using DSPy for structured analysis."""

    name: str = "quant_analyst"
    _predict: dspy.Predict = field(init=False, repr=False)

    def __post_init__(self) -> None:
        """Initialize DSPy predictor."""
        super().__post_init__()
        # Create predictor with signature
        object.__setattr__(self, "_predict", dspy.Predict(QuantAnalystSignature))

    @override
    async def prep(self, state: MarketData) -> MarketData:
        """Pre-execution hook to show progress.

        Returns:
            State passed through unchanged.
        """
        print("\n🤖 QUANTITATIVE ANALYST")
        print("   └─ Analyzing market trends and opportunities...")
        return state

    @staticmethod
    def _display_opportunities(opportunities: tuple[OpportunitySignal, ...]) -> None:
        """Display top investment opportunities."""
        if opportunities:
            print("   • Top Opportunities:")
            for opp in opportunities[:3]:
                print(f"     - {opp.symbol}: {opp.confidence:.0%} confidence")

    @staticmethod
    def _display_sector_analysis(sector_analysis: dict[str, float]) -> None:
        """Display sector outlook with sentiment analysis."""
        if sector_analysis:
            print("   • Sector Outlook:")
            sorted_sectors = sorted(sector_analysis.items(), key=itemgetter(1), reverse=True)
            for sector, score in sorted_sectors[:3]:
                sentiment = "bullish" if score > 0 else "bearish"
                print(f"     - {sector}: {sentiment} ({score:+.2f})")

    def _display_insights(self, insights: QuantInsights) -> None:
        """Display quantitative analysis insights."""
        print("\n   📊 Key Insights:")
        self._display_opportunities(insights.opportunities)
        self._display_sector_analysis(insights.sector_analysis)
        print(f"   • Market Regime: {insights.market_trend}")
        print(f"   • Summary: {insights.analysis_summary}")

    @override
    async def post(
        self, result: NodeResult[QuantInsights | AnalysisError]
    ) -> NodeResult[QuantInsights | AnalysisError]:
        """Post-execution hook to show completion.

        Returns:
            Result passed through unchanged.
        """
        if isinstance(result.state, AnalysisError):
            print("   ❌ Analysis failed")
        else:
            print("   ✔ Analysis complete")
            self._display_insights(result.state)
        return result

    @override
    async def exec(self, state: MarketData) -> NodeResult[QuantInsights | AnalysisError]:
        """Analyze market data using DSPy structured prediction.

        Returns:
            NodeResult with quantitative insights or analysis error.
        """

        if not state.assets:
            error = AnalysisError(
                error_type="no_market_data",
                error_message="No market data provided for analysis",
                failed_stage="QUANTITATIVE ANALYST (quant_analyst)",
                market_data=state,
            )
            return NodeResult(error, outcome="analysis_failed")

        try:
            # Extract available symbols for context
            symbols = tuple(asset.symbol for asset in state.assets)
            max_display = 5
            print(
                f"   • Analyzing {len(symbols)} assets: {', '.join(symbols[:max_display])}{'...' if len(symbols) > max_display else ''}"
            )

            # Use DSPy to get structured insights
            prediction = self._predict(market_data=state)
            insights: QuantInsights = prediction.insights

            return NodeResult(insights, outcome="analysis_complete")

        except (ValidationError, openai.OpenAIError, ValueError, TypeError) as exc:
            error = AnalysisError(
                error_type="prediction_failed",
                error_message=f"Quantitative analysis failed: {exc!s}",
                failed_stage="QUANTITATIVE ANALYST (quant_analyst)",
                market_data=state,
            )
            return NodeResult(error, outcome="analysis_failed")
