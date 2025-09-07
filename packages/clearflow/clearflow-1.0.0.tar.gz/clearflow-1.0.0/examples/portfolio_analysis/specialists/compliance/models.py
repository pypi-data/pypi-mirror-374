"""Data models for Compliance Officer."""

from typing import Literal

from pydantic import Field
from pydantic.dataclasses import dataclass


@dataclass(frozen=True)
class ComplianceCheck:
    """Individual compliance validation."""

    rule_name: str = Field(description="Compliance rule identifier")
    status: Literal["pass", "fail", "warning"] = Field(description="Compliance check result")
    details: str = Field(description="Specific details about the check")


@dataclass(frozen=True)
class ComplianceReview:
    """Stage 5: Regulatory and policy compliance validation."""

    compliance_checks: tuple[ComplianceCheck, ...] = Field(description="Individual compliance validations")
    overall_status: Literal["approved", "rejected", "conditional"] = Field(description="Overall compliance decision")
    regulatory_notes: tuple[str, ...] = Field(description="Regulatory considerations and notes")
    compliance_summary: str = Field(max_length=400, description="Compliance review summary")


@dataclass(frozen=True)
class ComplianceError:
    """Error state when compliance checks fail."""

    violations: tuple[ComplianceCheck, ...] = Field(description="Compliance violations found")
    required_actions: tuple[str, ...] = Field(description="Actions required for compliance")
    escalation_required: bool = Field(description="Whether escalation is needed")
    failed_stage: str = Field(description="Stage where compliance failed")
