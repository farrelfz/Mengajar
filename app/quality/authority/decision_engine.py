"""
Universal Document Intelligence System V5 — Authoritative Decision Engine.

Phase 3A.1: Master decision policy adjudicating export readiness, blocking criteria,
warning tolerances, and targeted repair routing across all artifact profiles.
"""

from __future__ import annotations

from typing import Any, Dict, List, Sequence, Tuple

from app.quality.authority.profiles import ArtifactQualityProfile
from app.quality.contracts.decisions import ExportDecision, UnifiedQualityDecision
from app.quality.contracts.dimensions import QualityDimensionScore
from app.quality.contracts.findings import FindingCluster, QualityFinding
from app.quality.contracts.signals import QualityDomain, QualitySignal, SignalSeverity


class AuthoritativeDecisionEngine:
    """Deterministic arbiter of quality export decisions."""

    @classmethod
    def arbitrate(
        cls,
        artifact_type: str,
        profile: ArtifactQualityProfile,
        signals: Sequence[QualitySignal],
        findings: Sequence[QualityFinding],
        clusters: Sequence[FindingCluster],
        dim_scores: Dict[str, QualityDimensionScore],
        domain_scores: Dict[str, float],
        overall_score: float,
        degeneracy_info: Dict[str, Any],
    ) -> UnifiedQualityDecision:
        hard_blockers: List[str] = []
        warnings: List[str] = []

        # 1. Identify Hard Blockers and Invariant Violations
        for f in findings:
            code = f.failure_code
            if profile.is_hard_blocker(code) or f.is_blocking():
                hard_blockers.append(f"{code}: {f.message}")
            elif f.severity == SignalSeverity.WARNING:
                warnings.append(f"{code}: {f.message}")
            elif f.severity == SignalSeverity.ERROR:
                # Errors that are not explicit hard blockers still count as major defects
                pass

        for s in signals:
            if profile.is_hard_blocker(s.canonical_code) or s.severity == SignalSeverity.BLOCKING:
                desc = f"{s.canonical_code}: {s.description}"
                if desc not in hard_blockers:
                    hard_blockers.append(desc)

        # 2. Hard Blocker Adjudication (Strict Zero Tolerance)
        if hard_blockers:
            return UnifiedQualityDecision(
                decision=ExportDecision.BLOCKED,
                can_export=False,
                repair_required=True,
                manual_review_required=False,
                hard_blockers=tuple(hard_blockers),
                warnings=tuple(warnings),
                rationale=f"Export blocked for {artifact_type} due to {len(hard_blockers)} hard invariant violations: {', '.join([h.split(':')[0] for h in hard_blockers[:3]])}.",
            )

        # 3. Check for Fatal Score Drops or Systemic Errors
        has_errors = any(f.severity == SignalSeverity.ERROR for f in findings) or any(
            s.severity == SignalSeverity.ERROR for s in signals
        )
        score_below_minimum = overall_score < profile.min_overall_score

        # Check dimension score minimums
        crit_dim_drop = any(ds.score < profile.min_dimension_score for ds in dim_scores.values())

        if has_errors or score_below_minimum or crit_dim_drop:
            # Determine repair class based on domain defect dominance
            render_defects = sum(1 for s in signals if s.domain == QualityDomain.RENDERED)
            semantic_defects = sum(
                1 for s in signals if s.domain in (QualityDomain.SEMANTIC, QualityDomain.ARTIFACT)
            )

            if render_defects > semantic_defects:
                target_decision = ExportDecision.RENDER_REPAIR_REQUIRED
                cat_desc = "physical rendered geometry"
            elif semantic_defects > render_defects:
                target_decision = ExportDecision.SEMANTIC_REPAIR_REQUIRED
                cat_desc = "semantic/pedagogical structure"
            else:
                target_decision = ExportDecision.REPAIR_REQUIRED
                cat_desc = "multi-layer quality non-conformance"

            return UnifiedQualityDecision(
                decision=target_decision,
                can_export=False,
                repair_required=True,
                manual_review_required=False,
                hard_blockers=(),
                warnings=tuple(warnings),
                rationale=f"Artifact {artifact_type} requires repair in {cat_desc} (overall score: {overall_score}, min: {profile.min_overall_score}).",
            )

        # 4. Warning Tolerance Adjudication
        if len(warnings) > profile.warning_tolerance:
            return UnifiedQualityDecision(
                decision=ExportDecision.REPAIR_REQUIRED,
                can_export=False,
                repair_required=True,
                manual_review_required=False,
                hard_blockers=(),
                warnings=tuple(warnings),
                rationale=f"Warning threshold exceeded for {artifact_type} ({len(warnings)} > tolerance {profile.warning_tolerance}).",
            )

        # 5. Degeneracy Safeguard
        if degeneracy_info.get("is_degenerate", False):
            return UnifiedQualityDecision(
                decision=ExportDecision.MANUAL_REVIEW_REQUIRED,
                can_export=False,
                repair_required=True,
                manual_review_required=True,
                hard_blockers=(),
                warnings=tuple(warnings) + ("Pathological score degeneracy detected across evaluators",),
                rationale=f"Manual review required: Degeneracy detected (universal_one={degeneracy_info.get('universal_one')}, zero_variance={degeneracy_info.get('zero_variance')}).",
            )

        # 6. Clean or Warn Approval
        if warnings:
            return UnifiedQualityDecision(
                decision=ExportDecision.EXPORT_APPROVED_WITH_WARNINGS,
                can_export=True,
                repair_required=False,
                manual_review_required=False,
                hard_blockers=(),
                warnings=tuple(warnings),
                rationale=f"Export approved for {artifact_type} with {len(warnings)} acceptable non-blocking warnings (score: {overall_score}).",
            )

        return UnifiedQualityDecision(
            decision=ExportDecision.EXPORT_APPROVED,
            can_export=True,
            repair_required=False,
            manual_review_required=False,
            hard_blockers=(),
            warnings=(),
            rationale=f"Export fully approved for {artifact_type} with high fidelity and zero defect warnings (score: {overall_score}).",
        )
