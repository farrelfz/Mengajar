"""
Universal Document Intelligence System V5 — Calibrated Decision Contract.

Phase 2C: Arbitrates combined Fidelity and Quality into authoritative export decisions.
Decision Matrix:
- HIGH FIDELITY + HIGH QUALITY   -> PASS
- HIGH FIDELITY + LOW QUALITY    -> PASS_WITH_WARNINGS or BLOCKED (depending on severity)
- LOW FIDELITY  + HIGH QUALITY   -> BLOCKED (Integrity failure overrides visual appearance)
- LOW FIDELITY  + LOW QUALITY    -> BLOCKED
"""

from __future__ import annotations

import time
from enum import Enum
from typing import Any, Dict, List, Tuple
from pydantic import BaseModel, ConfigDict, Field

from app.quality.contracts.fidelity_contract import ArtifactFidelityReport
from app.quality.contracts.quality_contract import ArtifactQualityReport


class QualityDecisionStatus(str, Enum):
    """Authoritative lifecycle status for an evaluated artifact."""
    PASS = "PASS"
    PASS_WITH_WARNINGS = "PASS_WITH_WARNINGS"
    BLOCKED = "BLOCKED"


class CalibratedQualityDecision(BaseModel):
    """Calibrated decision outcome combining fidelity preservation and artifact quality."""
    model_config = ConfigDict(frozen=True)

    artifact_type: str
    overall_decision: QualityDecisionStatus
    fidelity_status: str  # PASS / FAIL
    quality_status: str   # PASS / PASS_WITH_WARNINGS / BLOCKED
    fidelity_score: float
    quality_score: float
    blocking_failures: Tuple[str, ...] = Field(default_factory=tuple)
    warnings: Tuple[str, ...] = Field(default_factory=tuple)
    can_export: bool
    rationale: str
    timestamp: float = Field(default_factory=time.time)

    @classmethod
    def arbitrate(
        cls,
        fidelity_report: ArtifactFidelityReport,
        quality_report: ArtifactQualityReport,
        custom_blocking_rules: List[str] | None = None,
    ) -> CalibratedQualityDecision:
        blocking_failures: List[str] = list(custom_blocking_rules or [])
        warnings: List[str] = []

        # 1. Check Fidelity Failures (Fidelity failure ALWAYS blocks export)
        if not fidelity_report.is_passing:
            blocking_failures.append(
                f"Fidelity violation: Contract preservation failed with score {fidelity_report.overall_fidelity_score:.3f}"
            )
        blocking_failures.extend(fidelity_report.violations)
        warnings.extend(fidelity_report.warnings)

        # 2. Check Quality Failures
        critical_quality_findings = [
            f.finding for f in quality_report.findings if getattr(f, "severity", None) in ("critical", "CRITICAL")
        ]
        if critical_quality_findings:
            blocking_failures.extend(critical_quality_findings)

        warning_quality_findings = [
            f.finding for f in quality_report.findings if getattr(f, "severity", None) in ("warning", "WARNING")
        ]
        warnings.extend(warning_quality_findings)

        # Quality score thresholds
        if quality_report.overall_quality_score < 0.60:
            blocking_failures.append(
                f"Unacceptable quality: Composite quality score ({quality_report.overall_quality_score:.3f}) < 0.60"
            )
        elif quality_report.overall_quality_score < 0.75:
            warnings.append(
                f"Suboptimal quality: Composite quality score ({quality_report.overall_quality_score:.3f}) requires review"
            )

        # Determine statuses
        fidelity_status = "PASS" if (fidelity_report.is_passing and not fidelity_report.violations) else "FAIL"
        
        if blocking_failures:
            quality_status = "BLOCKED"
            overall_decision = QualityDecisionStatus.BLOCKED
            can_export = False
            rationale = (
                f"Export BLOCKED due to {len(blocking_failures)} critical failures. "
                f"Fidelity: {fidelity_report.overall_fidelity_score:.3f}, Quality: {quality_report.overall_quality_score:.3f}. "
                f"Top blocker: {blocking_failures[0]}"
            )
        elif warnings:
            quality_status = "PASS_WITH_WARNINGS"
            overall_decision = QualityDecisionStatus.PASS_WITH_WARNINGS
            can_export = True
            rationale = (
                f"Export APPROVED WITH WARNINGS ({len(warnings)} non-blocking advisories). "
                f"Fidelity: {fidelity_report.overall_fidelity_score:.3f}, Quality: {quality_report.overall_quality_score:.3f}."
            )
        else:
            quality_status = "PASS"
            overall_decision = QualityDecisionStatus.PASS
            can_export = True
            rationale = (
                f"Export APPROVED. High fidelity ({fidelity_report.overall_fidelity_score:.3f}) "
                f"and high quality ({quality_report.overall_quality_score:.3f}) verified."
            )

        return cls(
            artifact_type=fidelity_report.artifact_type,
            overall_decision=overall_decision,
            fidelity_status=fidelity_status,
            quality_status=quality_status,
            fidelity_score=fidelity_report.overall_fidelity_score,
            quality_score=quality_report.overall_quality_score,
            blocking_failures=tuple(blocking_failures),
            warnings=tuple(warnings),
            can_export=can_export,
            rationale=rationale,
        )
