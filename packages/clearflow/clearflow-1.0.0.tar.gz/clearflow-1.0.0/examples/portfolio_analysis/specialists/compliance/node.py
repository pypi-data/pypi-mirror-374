"""Compliance Officer node for regulatory compliance review."""

from dataclasses import dataclass, field
from typing import override

import dspy
import openai
from pydantic import ValidationError

from clearflow import Node, NodeResult
from examples.portfolio_analysis.specialists.compliance.models import ComplianceCheck, ComplianceError, ComplianceReview
from examples.portfolio_analysis.specialists.compliance.signature import ComplianceOfficerSignature
from examples.portfolio_analysis.specialists.compliance.validators import (
    validate_allocation_sanity,
    validate_position_limits,
    validate_sector_concentration,
)
from examples.portfolio_analysis.specialists.portfolio.models import AllocationChange, PortfolioRecommendations


@dataclass(frozen=True)
class ComplianceOfficer(Node[PortfolioRecommendations, ComplianceReview | ComplianceError]):
    """AI-powered compliance officer using DSPy for structured compliance review."""

    name: str = "compliance_officer"
    _predict: dspy.Predict = field(init=False, repr=False)

    def __post_init__(self) -> None:
        """Initialize DSPy predictor."""
        super().__post_init__()
        object.__setattr__(self, "_predict", dspy.Predict(ComplianceOfficerSignature))

    @override
    async def prep(self, state: PortfolioRecommendations) -> PortfolioRecommendations:
        """Pre-execution hook to show progress.

        Returns:
            State passed through unchanged.
        """
        print("\n🤖 COMPLIANCE OFFICER")
        print("   └─ Reviewing recommendations for regulatory compliance...")
        return state

    @staticmethod
    def _display_compliance_violations(error: ComplianceError) -> None:
        """Display compliance violations."""
        print("\n   🚫 Violations:")
        for violation in error.violations:
            print(f"   • {violation.rule_name}: {violation.details}")

    @staticmethod
    def _display_passed_checks(compliance_checks: tuple[ComplianceCheck, ...]) -> None:
        """Display passed compliance checks."""
        passed_checks = [c for c in compliance_checks if c.status == "pass"]
        for check in passed_checks[:3]:
            print(f"   • ✓ {check.rule_name}: {check.details}")

    @staticmethod
    def _display_warning_checks(compliance_checks: tuple[ComplianceCheck, ...]) -> None:
        """Display warning compliance checks."""
        warning_checks = [c for c in compliance_checks if c.status == "warning"]
        if warning_checks:
            print("   • Warnings:")
            for check in warning_checks:
                print(f"     ⚠️  {check.details}")

    def _display_compliance_review(self, review: ComplianceReview) -> None:
        """Display compliance review details."""
        print("\n   ✅ Compliance Checks:")
        self._display_passed_checks(review.compliance_checks)
        self._display_warning_checks(review.compliance_checks)
        if review.regulatory_notes:
            print(f"   • Regulatory Notes: {review.regulatory_notes}")
        print(f"   • Summary: {review.compliance_summary}")

    @override
    async def post(
        self, result: NodeResult[ComplianceReview | ComplianceError]
    ) -> NodeResult[ComplianceReview | ComplianceError]:
        """Post-execution hook to show completion.

        Returns:
            Result passed through unchanged.
        """
        if isinstance(result.state, ComplianceError):
            print("   ❌ Compliance violations detected")
            self._display_compliance_violations(result.state)
        else:
            print("   ✔ Compliance review approved")
            self._display_compliance_review(result.state)
        return result

    @staticmethod
    def _run_regulatory_checks(allocation_changes: tuple[AllocationChange, ...]) -> tuple[ComplianceCheck, ...]:
        """Run all regulatory compliance checks.

        Returns:
            Tuple of compliance checks with pass/fail status.
        """
        return (
            validate_position_limits(allocation_changes),
            validate_sector_concentration(allocation_changes),
            validate_allocation_sanity(allocation_changes),
        )

    @staticmethod
    def _check_for_violations(checks: tuple[ComplianceCheck, ...]) -> tuple[ComplianceCheck, ...]:
        """Filter checks for failures.

        Returns:
            Tuple of failed compliance checks only.
        """
        return tuple(check for check in checks if check.status == "fail")

    @override
    async def exec(self, state: PortfolioRecommendations) -> NodeResult[ComplianceReview | ComplianceError]:
        """Review compliance using DSPy structured prediction.

        Returns:
            NodeResult with compliance review or compliance error.
        """

        try:
            # Run regulatory compliance checks
            regulatory_checks = self._run_regulatory_checks(state.allocation_changes)
            failures = self._check_for_violations(regulatory_checks)

            if failures:
                # Regulatory violations detected
                error = ComplianceError(
                    violations=failures,
                    required_actions=tuple(f"Fix: {check.details}" for check in failures),
                    escalation_required=True,
                    failed_stage="COMPLIANCE OFFICER (compliance_officer)",
                )
                return NodeResult(error, outcome="compliance_failed")

            # Use DSPy for additional compliance review
            prediction = self._predict(recommendations=state)
            review: ComplianceReview = prediction.compliance_review

            # Merge regulatory checks with AI review
            review = ComplianceReview(
                compliance_checks=regulatory_checks + review.compliance_checks,
                overall_status=review.overall_status,
                regulatory_notes=review.regulatory_notes,
                compliance_summary=review.compliance_summary,
            )

            return NodeResult(review, outcome="compliance_approved")

        except (ValidationError, openai.OpenAIError, ValueError, TypeError) as exc:
            # Create compliance error
            error_check = ComplianceCheck(
                rule_name="analysis_error",
                status="fail",
                details=f"Compliance analysis failed: {exc!s}",
            )

            error = ComplianceError(
                violations=(error_check,),
                required_actions=(
                    "Retry compliance analysis",
                    "Review input recommendations",
                ),
                escalation_required=True,
                failed_stage="COMPLIANCE OFFICER (compliance_officer)",
            )
            return NodeResult(error, outcome="compliance_failed")
