"""
Universal Document Intelligence System V5 — Unified Quality Authority.

Phase 3A.1: The single canonical arbiter of document quality, failure normalization,
causal attribution, and export gating across all artifact formats.
"""

from __future__ import annotations

import time
import uuid
from typing import Any, Dict, List, Optional, Tuple

from app.quality.causal.attribution_engine import CausalAttributionEngine
from app.quality.causal.contracts import (
    CanonicalFailure,
    CanonicalQualityAssessment,
    FailureCluster,
    QualitySignal,
    RootCauseHypothesis,
)
from app.quality.causal.evidence_collector import CausalEvidenceCollector, MultiLayerEvidence
from app.quality.causal.failure_normalizer import FailureNormalizer
from app.quality.causal.signal_normalizer import QualitySignalNormalizer
from app.quality.causal.taxonomy import (
    CanonicalFailureSeverity,
    CausalConfidenceLevel,
    FailureScope,
    UnifiedDecisionStatus,
)


class UnifiedQualityAuthority:
    """Consolidated master quality authority arbitrating all quality signals and decisions."""

    @classmethod
    def evaluate_artifact(
        cls,
        artifact_type: str,
        rendered_inspection: Any = None,
        phase_2c_report: Any = None,
        fidelity_report: Any = None,
        intermediate_model: Any = None,
        source_metadata: Dict[str, Any] | None = None,
    ) -> CanonicalQualityAssessment:
        norm_type = artifact_type.upper()

        # 1. Ingest all raw signals into canonical QualitySignal objects
        signals: List[QualitySignal] = []
        if rendered_inspection is not None:
            signals.extend(QualitySignalNormalizer.from_rendered_inspection(rendered_inspection))
        if phase_2c_report is not None:
            signals.extend(QualitySignalNormalizer.from_phase_2c_report(phase_2c_report))
        if fidelity_report is not None:
            signals.extend(QualitySignalNormalizer.from_fidelity_report(fidelity_report))

        # 2. Collect multi-layer evidence snapshot
        evidence = CausalEvidenceCollector.collect(
            artifact_type=norm_type,
            rendered_inspection=rendered_inspection,
            intermediate_model=intermediate_model,
            source_manifest=source_metadata,
        )

        total_pages = max(1, evidence.total_pages)

        # 3. Normalize signals into deduplicated CanonicalFailures
        failures = FailureNormalizer.normalize_signals(signals, total_pages=total_pages)

        # 4. Perform Causal Attribution and Clustering
        hypotheses, clusters = CausalAttributionEngine.attribute(failures, evidence)

        # 5. Extract Dimensional Scores & Composite Quality Score
        dimensional_scores: Dict[str, float] = {}
        if rendered_inspection and hasattr(rendered_inspection, "dimensional_scores"):
            dimensional_scores = dict(rendered_inspection.dimensional_scores)
        elif phase_2c_report and hasattr(phase_2c_report, "dimensional_scores"):
            for k, v in phase_2c_report.dimensional_scores.items():
                dimensional_scores[k] = getattr(v, "score", float(v)) if not isinstance(v, (int, float)) else float(v)

        # Fallback default score
        overall_score = (
            rendered_inspection.overall_quality_score
            if rendered_inspection and hasattr(rendered_inspection, "overall_quality_score")
            else (
                phase_2c_report.overall_quality_score
                if phase_2c_report and hasattr(phase_2c_report, "overall_quality_score")
                else 1.0
            )
        )

        # 6. Count severities
        critical_count = sum(1 for f in failures if f.severity == CanonicalFailureSeverity.CRITICAL)
        major_count = sum(1 for f in failures if f.severity == CanonicalFailureSeverity.MAJOR)
        minor_count = sum(1 for f in failures if f.severity == CanonicalFailureSeverity.MINOR)

        # 7. Apply Scope-Aware Deterministic Decision Policy
        decision, can_export, repair_required, manual_review, rationale = cls._arbitrate_decision(
            failures=failures,
            clusters=clusters,
            hypotheses=hypotheses,
            critical_count=critical_count,
            major_count=major_count,
            minor_count=minor_count,
            overall_score=overall_score,
            total_pages=total_pages,
        )

        pdf_path = getattr(rendered_inspection, "rendered_pdf_path", None)

        return CanonicalQualityAssessment(
            artifact_type=norm_type,
            rendered_pdf_path=pdf_path,
            page_count=total_pages,
            dimensional_scores=dimensional_scores,
            overall_quality_score=round(overall_score, 3),
            failures=tuple(failures),
            failure_clusters=tuple(clusters),
            root_cause_hypotheses=tuple(hypotheses),
            critical_failures_count=critical_count,
            major_warnings_count=major_count,
            minor_warnings_count=minor_count,
            decision=decision,
            can_export=can_export,
            repair_required=repair_required,
            manual_review_required=manual_review,
            rationale=rationale,
        )

    @classmethod
    def _arbitrate_decision(
        cls,
        failures: List[CanonicalFailure],
        clusters: List[FailureCluster],
        hypotheses: List[RootCauseHypothesis],
        critical_count: int,
        major_count: int,
        minor_count: int,
        overall_score: float,
        total_pages: int,
    ) -> Tuple[UnifiedDecisionStatus, bool, bool, bool, str]:
        # 1. Any CRITICAL failure unconditionally BLOCKS export
        if critical_count > 0:
            top_crit = [f for f in failures if f.severity == CanonicalFailureSeverity.CRITICAL][0]
            rationale = f"Export blocked due to {critical_count} critical failures. Top: {top_crit.symptom}"
            return UnifiedDecisionStatus.BLOCKED, False, True, False, rationale

        # 2. Check for Ambiguous / Low confidence root causes
        has_ambiguous_cause = any(
            h.confidence_level in (CausalConfidenceLevel.AMBIGUOUS, CausalConfidenceLevel.LOW)
            for h in hypotheses
        )

        # 3. MAJOR Failures with Scope Analysis
        if major_count > 0:
            major_failures = [f for f in failures if f.severity == CanonicalFailureSeverity.MAJOR]
            has_systemic_or_cluster = any(
                f.scope in (FailureScope.SYSTEMIC, FailureScope.CLUSTER, FailureScope.ARTIFACT_WIDE)
                for f in major_failures
            )

            if has_systemic_or_cluster or major_count >= 3:
                rationale = f"Artifact requires repair: {major_count} major warnings with systemic/cluster impact."
                return UnifiedDecisionStatus.NEEDS_REPAIR, False, True, has_ambiguous_cause, rationale
            else:
                # Isolated local major warning in large document (e.g. 1 page out of 20)
                rationale = f"Approved with warning: {major_count} localized major warning on {len(major_failures[0].affected_pages)} page."
                return UnifiedDecisionStatus.PASS_WITH_WARNINGS, True, False, has_ambiguous_cause, rationale

        # 4. MINOR Failures or Suboptimal score
        if minor_count > 0 or overall_score < 0.90:
            rationale = f"Approved with minor warnings ({minor_count} warnings, score {overall_score:.3f})."
            return UnifiedDecisionStatus.PASS_WITH_WARNINGS, True, False, has_ambiguous_cause, rationale

        # 5. Clean Pass
        return UnifiedDecisionStatus.PASS, True, False, False, f"Clean pass across all dimensions (score {overall_score:.3f})."
