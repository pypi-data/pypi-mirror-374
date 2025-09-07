"""Portfolio analysis example using DSPy-powered nodes."""

from clearflow import Node, flow
from examples.portfolio_analysis.shared import MarketData, configure_dspy
from examples.portfolio_analysis.specialists import (
    ComplianceOfficer,
    DecisionNode,
    ErrorHandler,
    PortfolioManager,
    QuantAnalyst,
    RiskAnalyst,
)
from examples.portfolio_analysis.specialists.decision.models import TradingDecision


def create_portfolio_analysis_flow() -> Node[MarketData, TradingDecision]:
    """Create the AI portfolio analysis workflow with DSPy nodes.

    Returns:
        Flow that processes MarketData through multiple AI specialists
        to produce TradingDecision or error states.
    """
    # Configure DSPy with OpenAI
    configure_dspy()

    # Create nodes
    quant = QuantAnalyst()
    risk = RiskAnalyst()
    pm = PortfolioManager()
    compliance = ComplianceOfficer()
    decision = DecisionNode()
    error_handler = ErrorHandler()

    # Build the flow with routing
    # Note: We need a converged end point. Let's use decision as the final node
    # and have error_handler route to it with a "hold" decision
    return (
        flow("PortfolioAnalysis", quant)
        # Quantitative analysis routes
        .route(quant, "analysis_complete", risk)
        .route(quant, "analysis_failed", error_handler)
        # Risk assessment routes
        .route(risk, "risk_acceptable", pm)
        .route(risk, "risk_limits_exceeded", error_handler)
        # Portfolio management routes
        .route(pm, "recommendations_ready", compliance)
        .route(pm, "analysis_failed", error_handler)
        # Compliance review routes
        .route(compliance, "compliance_approved", decision)
        .route(compliance, "compliance_failed", error_handler)
        # Error handler produces a minimal decision
        .route(error_handler, "error_handled", decision)
        # Single termination point
        .end(decision, "decision_ready")
    )
