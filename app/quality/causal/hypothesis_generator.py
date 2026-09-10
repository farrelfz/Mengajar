"""
Universal Document Intelligence System V5 — Causal Hypothesis Generator.

Phase 3B: Generates ranked, explainable RootCauseHypothesis candidates for a FailureCluster
without discarding competing alternatives.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Sequence, Tuple

from app.quality.causal.causal_taxonomy import (
    CausalArchitecturalLayer,
    CausalConfidenceLevel,
    HypothesisStatus,
    RootCauseCategory,
)
from app.quality.causal.config import CausalIntelligenceConfig, DEFAULT_CAUSAL_CONFIG
from app.quality.causal.contracts import FailureCluster, RootCauseHypothesis
from app.quality.causal.evidence_scorer import CausalEvidenceScorer
from app.quality.causal.rules import CausalRuleCatalog, CausalRuleMatch


class CausalHypothesisGenerator:
    """Generates competing root cause hypotheses for a failure cluster using calibrated rule matching."""

    def __init__(
        self,
        config: Optional[CausalIntelligenceConfig] = None,
        scorer: Optional[CausalEvidenceScorer] = None,
    ):
        self.config = config or DEFAULT_CAUSAL_CONFIG
        self.scorer = scorer or CausalEvidenceScorer(self.config)

    def generate_hypotheses(
        self,
        cluster: FailureCluster,
        artifact_type: str = "UNKNOWN",
    ) -> List[RootCauseHypothesis]:
        """Produces a ranked list of competing RootCauseHypothesis objects for a FailureCluster."""
        matches = CausalRuleCatalog.match_rules(cluster, artifact_type=artifact_type)
        hypotheses: List[RootCauseHypothesis] = []
        cluster_codes = {s.failure_code.value for s in cluster.signals}
        if not cluster_codes and cluster.symptoms:
            cluster_codes = {c.value for c in cluster.symptoms}

        competition_count = len(matches) - 1 if len(matches) > 1 else 0

        for match in matches:
            rule = match.rule

            # Check for contradiction conditions
            has_contradiction = False
            contra_msg = ""
            if rule.rule_id == "RULE_PRES_TYPOGRAPHY_SCALE":
                if "DENSITY_OVERLOAD" in cluster_codes or "COGNITIVE_LOAD_OVERFLOW" in cluster_codes:
                    has_contradiction = True
                    contra_msg = "Content density overload indicates root issue is capacity rather than pure font scale."

            # Score hypothesis via CausalEvidenceScorer
            score, conf_level, breakdown, evidence_notes = self.scorer.score_hypothesis(
                cluster=cluster,
                candidate_layer=rule.architectural_layer,
                explains_signal_count=len(match.matched_signal_ids),
                base_match_score=match.match_score,
                has_contradiction=has_contradiction,
                contradiction_details=contra_msg,
                competition_count=competition_count,
            )

            # Determine hypothesis status
            if score >= 0.85:
                status = HypothesisStatus.STRONG.value
            elif score >= 0.70:
                status = HypothesisStatus.LIKELY.value
            elif score >= 0.35:
                status = HypothesisStatus.CANDIDATE.value
            else:
                status = HypothesisStatus.REJECTED.value

            # Format causal path trace
            if rule.causal_path_template:
                path_str = " → ".join(f"{evt} [{layer.value}]" for layer, evt in rule.causal_path_template)
            else:
                path_str = f"Root cause '{rule.candidate_root_cause.value}' in {rule.architectural_layer.value} produces observed cluster symptoms."

            supporting_ev = match.supporting_evidence + evidence_notes
            contradicting_ev = (contra_msg,) if has_contradiction else ()

            hyp = RootCauseHypothesis(
                cause_code=rule.candidate_root_cause.value,
                cause_layer=rule.architectural_layer.value,
                confidence_score=score,
                confidence_level=conf_level,
                supporting_evidence=supporting_ev,
                contradicting_evidence=contradicting_ev,
                affected_scope=cluster.scope,
                repair_authority=rule.architectural_layer.value,
                confidence_components=breakdown.to_dict(),
                causal_path=path_str,
                status=status,
                explains_signal_ids=match.matched_signal_ids,
            )
            hypotheses.append(hyp)

        # Fallback if no rules matched
        if not hypotheses:
            fallback_score = 0.25
            hyp = RootCauseHypothesis(
                cause_code=RootCauseCategory.UNKNOWN_CAUSE.value,
                cause_layer=CausalArchitecturalLayer.RENDERING.value,
                confidence_score=fallback_score,
                confidence_level=CausalConfidenceLevel.VERY_LOW,
                supporting_evidence=("No deterministic causal rule matched the observed cluster pattern.",),
                affected_scope=cluster.scope,
                repair_authority=CausalArchitecturalLayer.RENDERING.value,
                confidence_components={"overall": fallback_score},
                causal_path="Unknown upstream defect",
                status=HypothesisStatus.UNKNOWN.value,
                explains_signal_ids=tuple(s.signal_id for s in cluster.signals),
            )
            hypotheses.append(hyp)

        # Sort by confidence descending and assign alternative ranks
        hypotheses.sort(key=lambda h: h.confidence_score, reverse=True)
        ranked_hypotheses: List[RootCauseHypothesis] = []
        for rank, h in enumerate(hypotheses, 1):
            ranked_h = RootCauseHypothesis(
                hypothesis_id=h.hypothesis_id,
                cause_code=h.cause_code,
                cause_layer=h.cause_layer,
                confidence_score=h.confidence_score,
                confidence_level=h.confidence_level,
                supporting_evidence=h.supporting_evidence,
                contradicting_evidence=h.contradicting_evidence,
                affected_scope=h.affected_scope,
                repair_authority=h.repair_authority,
                allowed_repair_classes=h.allowed_repair_classes,
                forbidden_repairs=h.forbidden_repairs,
                confidence_components=h.confidence_components,
                causal_path=h.causal_path,
                status=h.status,
                explains_signal_ids=h.explains_signal_ids,
                alternative_rank=rank,
            )
            ranked_hypotheses.append(ranked_h)

        return ranked_hypotheses
