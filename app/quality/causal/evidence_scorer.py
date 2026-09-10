"""
Universal Document Intelligence System V5 — Causal Evidence Scorer.

Phase 3B: Explainable multi-dimensional scoring of root cause hypotheses
enforcing strict lineage direction and contradiction penalties.
"""

from __future__ import annotations

from typing import Any, Dict, Optional, Tuple
from pydantic import BaseModel, ConfigDict, Field

from app.quality.causal.causal_taxonomy import (
    CausalArchitecturalLayer,
    CausalConfidenceLevel,
)
from app.quality.causal.config import CausalIntelligenceConfig, DEFAULT_CAUSAL_CONFIG
from app.quality.causal.contracts import FailureCluster


class CausalConfidenceBreakdown(BaseModel):
    """Component score breakdown explaining how causal confidence was derived."""
    model_config = ConfigDict(frozen=True)

    overall: float = Field(ge=0.0, le=1.0)
    explanatory_coverage: float = Field(ge=0.0, le=1.0)
    evidence_strength: float = Field(ge=0.0, le=1.0)
    lineage_consistency: float = Field(ge=0.0, le=1.0)
    pattern_compatibility: float = Field(ge=0.0, le=1.0)
    contradiction_penalty: float = Field(ge=0.0, le=1.0)
    competition_penalty: float = Field(ge=0.0, le=1.0)

    def to_dict(self) -> Dict[str, float]:
        return self.model_dump()


class CausalEvidenceScorer:
    """Calculates deterministic causal confidence and enforces confidence invariants."""

    def __init__(self, config: Optional[CausalIntelligenceConfig] = None):
        self.config = config or DEFAULT_CAUSAL_CONFIG

    def score_hypothesis(
        self,
        cluster: FailureCluster,
        candidate_layer: CausalArchitecturalLayer,
        explains_signal_count: int,
        base_match_score: float,
        has_contradiction: bool = False,
        contradiction_details: str = "",
        competition_count: int = 0,
    ) -> Tuple[float, CausalConfidenceLevel, CausalConfidenceBreakdown, Tuple[str, ...]]:
        """Scores a causal hypothesis with explicit breakdown and invariant enforcement."""
        total_signals = max(1, len(cluster.signals))
        evidence_notes: List[str] = []

        # 1. Explanatory Coverage
        coverage = min(1.0, explains_signal_count / total_signals)
        evidence_notes.append(f"Explanatory coverage: {explains_signal_count}/{total_signals} ({coverage:.0%})")

        # 2. Evidence Strength (derived from cluster correlation and measurements)
        evidence_strength = max(0.50, min(1.0, cluster.correlation_strength if cluster.correlation_strength > 0 else 0.75))
        if any(s.evidence for s in cluster.signals):
            evidence_strength = min(1.0, evidence_strength + 0.10)

        # 3. Lineage Consistency (Upstream vs Downstream)
        # Determine average symptom layer order in cluster
        symptom_order = 7  # Default to RENDER
        if any(s.failure_domain.value == "PHYSICAL_RENDER" for s in cluster.signals):
            symptom_order = 7
        elif any(s.failure_domain.value == "STYLE_DESIGN" for s in cluster.signals):
            symptom_order = 5
        elif any(s.failure_domain.value == "BLUEPRINT_INTEGRITY" for s in cluster.signals):
            symptom_order = 4

        cause_order = candidate_layer.stage_order

        # Strict rule: Downstream cannot cause upstream!
        if cause_order > symptom_order and candidate_layer != CausalArchitecturalLayer.VALIDATION:
            lineage_consistency = 0.10
            evidence_notes.append(
                f"Lineage violation: Cause layer '{candidate_layer.value}' (stage {cause_order}) "
                f"is downstream of symptom layer (stage {symptom_order})"
            )
        else:
            lineage_consistency = 1.0
            evidence_notes.append(f"Lineage consistent: Upstream cause layer '{candidate_layer.value}'")

        # 4. Pattern Compatibility
        pattern_compatibility = base_match_score

        # 5. Contradiction Penalty
        contradiction_penalty = self.config.max_contradiction_penalty if has_contradiction else 0.0
        if has_contradiction:
            evidence_notes.append(f"Contradiction penalty applied: {contradiction_details}")

        # 6. Competition Penalty
        comp_penalty = min(0.20, competition_count * self.config.competition_penalty_rate)
        if competition_count > 0:
            evidence_notes.append(f"Competition penalty applied ({competition_count} competing causes)")

        # Weighted calculation
        raw_score = (
            0.30 * coverage
            + 0.25 * evidence_strength
            + 0.25 * lineage_consistency
            + 0.20 * pattern_compatibility
            - contradiction_penalty
            - comp_penalty
        )
        final_score = round(max(0.0, min(1.0, raw_score)), 4)

        # Invariant checks for VERY_HIGH confidence
        if final_score >= self.config.confidence_thresholds.very_high:
            if lineage_consistency < 0.90 or has_contradiction or coverage < self.config.min_explanatory_coverage_for_high:
                # Demote score if invariants violated
                final_score = min(final_score, self.config.confidence_thresholds.high - 0.01)
                evidence_notes.append("Demoted from VERY_HIGH due to missing invariant proof")

        confidence_level = CausalConfidenceLevel.from_score(final_score)

        breakdown = CausalConfidenceBreakdown(
            overall=final_score,
            explanatory_coverage=round(coverage, 4),
            evidence_strength=round(evidence_strength, 4),
            lineage_consistency=round(lineage_consistency, 4),
            pattern_compatibility=round(pattern_compatibility, 4),
            contradiction_penalty=round(contradiction_penalty, 4),
            competition_penalty=round(comp_penalty, 4),
        )

        return final_score, confidence_level, breakdown, tuple(evidence_notes)
