"""
Universal Document Intelligence System V5 — Causal Confidence Estimator.

Phase 3A.1: Quantifies certainty in causal hypotheses. Strictly flags LOW
and AMBIGUOUS confidence to prevent automated repair engines from guessing.
"""

from __future__ import annotations

from typing import List, Tuple
from app.quality.causal.contracts import RootCauseHypothesis
from app.quality.causal.taxonomy import ArchitectureLayer, CanonicalRepairClass, CausalConfidenceLevel


class CausalConfidenceEstimator:
    """Evaluates supporting and contradicting evidence to compute calibrated confidence."""

    @classmethod
    def evaluate_confidence(
        cls,
        supporting_count: int,
        contradicting_count: int,
        evidence_quality_weight: float = 1.0,
    ) -> Tuple[float, CausalConfidenceLevel]:
        # If there is any contradicting evidence, cause cannot be HIGH confidence
        if contradicting_count > 0:
            score = max(0.10, round(0.40 / (contradicting_count + 1), 2))
            return score, CausalConfidenceLevel.LOW

        # If zero supporting evidence
        if supporting_count == 0:
            return 0.20, CausalConfidenceLevel.LOW

        # Baseline calculation
        raw_score = (supporting_count / (supporting_count + 1.0)) * evidence_quality_weight
        score = round(min(0.95, max(0.10, raw_score)), 2)

        if score >= 0.80:
            return score, CausalConfidenceLevel.HIGH
        elif score >= 0.50:
            return score, CausalConfidenceLevel.MEDIUM
        else:
            return score, CausalConfidenceLevel.LOW

    @classmethod
    def arbitrate_competing_hypotheses(
        cls,
        hypotheses: List[RootCauseHypothesis],
    ) -> Tuple[RootCauseHypothesis | None, List[RootCauseHypothesis], bool]:
        """Disentangles multiple hypotheses. Flags ambiguity if top two are too close."""
        if not hypotheses:
            return None, [], False

        # Sort by confidence descending
        sorted_hyps = sorted(hypotheses, key=lambda h: h.confidence_score, reverse=True)
        top = sorted_hyps[0]

        # Single hypothesis
        if len(sorted_hyps) == 1:
            is_ambig = top.confidence_level == CausalConfidenceLevel.LOW
            return top, sorted_hyps[1:], is_ambig

        second = sorted_hyps[1]
        delta = round(top.confidence_score - second.confidence_score, 2)

        # Ambiguity condition: delta < 0.15 or both < 0.50
        is_ambiguous = (delta < 0.15) or (top.confidence_score < 0.50)

        if is_ambiguous:
            # Reclassify top as AMBIGUOUS and forbid automatic repair
            ambiguous_top = RootCauseHypothesis(
                cause_code="CAUSE_AMBIGUOUS",
                cause_layer=top.cause_layer,
                confidence_score=top.confidence_score,
                confidence_level=CausalConfidenceLevel.AMBIGUOUS,
                supporting_evidence=top.supporting_evidence,
                contradicting_evidence=top.contradicting_evidence + (f"Competing hypothesis {second.cause_code} with score {second.confidence_score}",),
                affected_scope=top.affected_scope,
                repair_authority=ArchitectureLayer.ARTIFACT_POLICY,
                allowed_repair_classes=(CanonicalRepairClass.CLASS_G_MANUAL_REVIEW,),
                forbidden_repairs=("AUTOMATIC_REPAIR_FORBIDDEN",),
            )
            return ambiguous_top, sorted_hyps, True

        return top, sorted_hyps[1:], False
