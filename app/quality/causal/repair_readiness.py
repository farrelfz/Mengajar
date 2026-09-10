"""
Universal Document Intelligence System V5 — Repair Readiness Assessor.

Phase 3B: Bridge between causal intelligence (Phase 3B) and repair strategy (Phase 3C).
Assesses whether an attributed root cause is safe, deterministic, and bounded enough
for repair, or whether it requires manual review or passive observation.

STRICT CONTRACT INVARIANT:
This module NEVER executes any repair. It is strictly read-only and analytical.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from app.quality.causal.causal_taxonomy import (
    CausalArchitecturalLayer,
    CausalConfidenceLevel,
    CausalDecision,
    RootCauseCategory,
)
from app.quality.causal.competing_analysis import CompetingAnalysisResult
from app.quality.causal.contracts import FailureCluster, RootCauseHypothesis
from app.quality.causal.taxonomy import CanonicalFailureSeverity, CanonicalRepairClass, FailureScope


class RepairAuthorityLevel(str, Enum):
    """Authoritative tier recommended for addressing an identified failure."""
    NO_ACTION = "NO_ACTION"
    OBSERVE = "OBSERVE"
    MANUAL_REVIEW = "MANUAL_REVIEW"
    DETERMINISTIC_REPAIR_CANDIDATE = "DETERMINISTIC_REPAIR_CANDIDATE"
    HIGH_RISK_REPAIR = "HIGH_RISK_REPAIR"


class RepairReadinessAssessment(BaseModel):
    """Exhaustive, explainable readiness assessment for a failure cluster."""
    cluster_id: str
    causal_decision: CausalDecision
    root_cause_category: Optional[RootCauseCategory] = None
    root_cause_confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    affected_scope: FailureScope
    blast_radius: float = Field(default=0.0, ge=0.0, le=1.0)
    reversibility: float = Field(default=0.0, ge=0.0, le=1.0)
    determinism: float = Field(default=0.0, ge=0.0, le=1.0)
    alternative_ambiguity: float = Field(default=0.0, ge=0.0, le=1.0)
    evidence_sufficiency: float = Field(default=0.0, ge=0.0, le=1.0)
    recommended_authority: RepairAuthorityLevel
    recommended_action_class: CanonicalRepairClass = CanonicalRepairClass.NONE
    blocking_reasons: List[str] = Field(default_factory=list)
    candidate_repair_scope: Dict[str, Any] = Field(default_factory=dict)
    rationale: str

    def is_repair_ready(self) -> bool:
        """True if safe to proceed to automated deterministic repair planning."""
        return self.recommended_authority == RepairAuthorityLevel.DETERMINISTIC_REPAIR_CANDIDATE


class RepairReadinessAssessor:
    """Evaluates causal analysis results and determines repair readiness."""

    def assess(
        self,
        cluster: FailureCluster,
        competing_result: CompetingAnalysisResult,
        total_pages: int = 1,
    ) -> RepairReadinessAssessment:
        """Assesses cluster repair readiness based on causal attribution and safety bounds."""
        top_hyp = competing_result.winning_hypothesis
        decision = competing_result.decision
        scope = cluster.scope

        # Calculate blast radius
        blast_radius = self._calculate_blast_radius(cluster, total_pages)

        # Calculate reversibility and determinism based on root cause
        reversibility = self._calculate_reversibility(top_hyp)
        determinism = self._calculate_determinism(top_hyp, competing_result)

        # Evidence sufficiency & alternative ambiguity
        ev_sufficiency = top_hyp.confidence_score if top_hyp else 0.0
        alt_ambiguity = competing_result.ambiguity_score

        # Candidate repair class
        action_class = self._determine_repair_class(top_hyp)

        blocking_reasons: List[str] = []
        authority: RepairAuthorityLevel = RepairAuthorityLevel.MANUAL_REVIEW
        rationale: str = ""

        # Evaluate gating conditions
        if top_hyp is None or decision in (CausalDecision.NO_CAUSAL_LINK, CausalDecision.INSUFFICIENT_EVIDENCE):
            if cluster.max_severity == CanonicalFailureSeverity.INFO:
                authority = RepairAuthorityLevel.NO_ACTION
                rationale = "No actionable failure identified; informational signals only."
            else:
                authority = RepairAuthorityLevel.OBSERVE
                blocking_reasons.append("Insufficient causal evidence to identify root cause.")
                rationale = "Failure observed but lacks sufficient causal attribution; observe and monitor."

        elif decision == CausalDecision.VALIDATOR_ANOMALY_SUSPECTED:
            authority = RepairAuthorityLevel.MANUAL_REVIEW
            blocking_reasons.append("Suspected validator false positive or contradictory signals.")
            rationale = "Conflicting inspection measurements indicate validator anomaly. Automated repair forbidden."

        elif decision == CausalDecision.MULTIPLE_PLAUSIBLE_CAUSES or competing_result.is_ambiguous:
            authority = RepairAuthorityLevel.MANUAL_REVIEW
            blocking_reasons.append(
                f"Competing hypotheses margin ({competing_result.top_hypotheses_delta:.3f}) <= threshold. "
                f"Alternative ambiguity is {alt_ambiguity:.2f}."
            )
            rationale = (
                "Multiple plausible root causes detected with similar evidence support. "
                "Automated repair strictly forbidden to avoid addressing the wrong cause."
            )

        elif ev_sufficiency < 0.55:
            authority = RepairAuthorityLevel.OBSERVE
            blocking_reasons.append(f"Evidence sufficiency ({ev_sufficiency:.2f}) is below minimum threshold (0.55).")
            rationale = "Low confidence root cause hypothesis. Observe without active intervention."

        elif blast_radius >= 0.70 or scope in (FailureScope.SYSTEMIC, FailureScope.ARTIFACT_WIDE):
            authority = RepairAuthorityLevel.HIGH_RISK_REPAIR
            blocking_reasons.append(
                f"High blast radius ({blast_radius:.2f}) or scope ({scope.value}) spans document-wide architecture."
            )
            rationale = (
                f"Confirmed root cause ({top_hyp.category.value if hasattr(top_hyp.category, 'value') else str(top_hyp.category)}) "
                f"carries high blast radius ({blast_radius:.2f}). Requires high-risk controlled repair."
            )

        elif reversibility < 0.50 or determinism < 0.60:
            authority = RepairAuthorityLevel.HIGH_RISK_REPAIR
            blocking_reasons.append(
                f"Low reversibility ({reversibility:.2f}) or low determinism ({determinism:.2f})."
            )
            rationale = "Action is irreversible or has unpredictable side-effects. Requires high-risk protocol."

        elif top_hyp.confidence_score >= 0.70 and decision in (CausalDecision.ROOT_CAUSE_CONFIRMED, CausalDecision.ROOT_CAUSE_LIKELY):
            authority = RepairAuthorityLevel.DETERMINISTIC_REPAIR_CANDIDATE
            rationale = (
                f"High-confidence root cause ({top_hyp.category.value if hasattr(top_hyp.category, 'value') else str(top_hyp.category)}) "
                f"with bounded blast radius ({blast_radius:.2f}) and high determinism ({determinism:.2f}). "
                "Safe for deterministic repair strategy generation."
            )

        else:
            authority = RepairAuthorityLevel.MANUAL_REVIEW
            blocking_reasons.append("Failure characteristics do not satisfy deterministic automated repair criteria.")
            rationale = "Moderate confidence or unclassified failure boundary requires manual inspection."

        # Build candidate repair scope
        candidate_scope = {
            "scope": scope.value,
            "affected_pages": cluster.affected_pages,
            "primary_symptoms": [s.signal_id for s in cluster.signals if getattr(s, "severity", None) in (CanonicalFailureSeverity.BLOCKING, CanonicalFailureSeverity.CRITICAL, CanonicalFailureSeverity.MAJOR)],
            "target_layer": top_hyp.origin_layer.value if (top_hyp and hasattr(top_hyp.origin_layer, "value")) else (str(top_hyp.origin_layer) if top_hyp else None),
            "repair_class": action_class.value,
        }

        cat_enum = None
        if top_hyp and top_hyp.category:
            cat_val = top_hyp.category.value if hasattr(top_hyp.category, "value") else str(top_hyp.category)
            try:
                cat_enum = RootCauseCategory(cat_val)
            except ValueError:
                cat_enum = None

        return RepairReadinessAssessment(
            cluster_id=cluster.cluster_id,
            causal_decision=decision,
            root_cause_category=cat_enum,
            root_cause_confidence=top_hyp.confidence_score if top_hyp else 0.0,
            affected_scope=scope,
            blast_radius=round(blast_radius, 3),
            reversibility=round(reversibility, 3),
            determinism=round(determinism, 3),
            alternative_ambiguity=round(alt_ambiguity, 3),
            evidence_sufficiency=round(ev_sufficiency, 3),
            recommended_authority=authority,
            recommended_action_class=action_class,
            blocking_reasons=blocking_reasons,
            candidate_repair_scope=candidate_scope,
            rationale=rationale,
        )

    def _calculate_blast_radius(self, cluster: FailureCluster, total_pages: int) -> float:
        base_scope_radius = {
            FailureScope.LOCAL: 0.15,
            FailureScope.CLUSTER: 0.40,
            FailureScope.SYSTEMIC: 0.75,
            FailureScope.ARTIFACT_WIDE: 0.95,
        }
        radius = base_scope_radius.get(cluster.scope, 0.50)

        # Adjust by page coverage if known
        if total_pages > 0 and cluster.affected_pages:
            page_coverage = len(cluster.affected_pages) / float(total_pages)
            # Weighted blend: 60% scope baseline + 40% exact page coverage
            radius = 0.60 * radius + 0.40 * min(1.0, page_coverage)

        return min(1.0, max(0.0, radius))

    def _calculate_reversibility(self, hypothesis: Optional[RootCauseHypothesis]) -> float:
        if not hypothesis:
            return 0.50
        layer = hypothesis.origin_layer
        layer_str = layer.value if hasattr(layer, "value") else str(layer)
        # Presentation styling, typography, CSS geometry are easily rolled back
        if layer_str in ("RENDERING", "COMPOSITION"):
            return 0.90
        if layer_str == "SEMANTIC_LAYOUT":
            return 0.75
        if layer_str == "BLUEPRINT":
            return 0.60
        if layer_str in ("TRANSFORMATION", "KNOWLEDGE_MODEL"):
            return 0.35
        if layer_str == "SOURCE_CONTENT":
            return 0.20
        return 0.50

    def _calculate_determinism(
        self,
        hypothesis: Optional[RootCauseHypothesis],
        competing: CompetingAnalysisResult,
    ) -> float:
        if not hypothesis:
            return 0.0
        # If ambiguous, determinism drops significantly
        if competing.is_ambiguous:
            return 0.25

        layer = hypothesis.origin_layer
        layer_str = layer.value if hasattr(layer, "value") else str(layer)
        if layer_str in ("RENDERING", "COMPOSITION"):
            return 0.85
        if layer_str == "SEMANTIC_LAYOUT":
            return 0.80
        if layer_str == "BLUEPRINT":
            return 0.70
        if layer_str == "TRANSFORMATION":
            return 0.50
        if layer_str == "SOURCE_CONTENT":
            return 0.30
        return 0.50

    def _determine_repair_class(self, hypothesis: Optional[RootCauseHypothesis]) -> CanonicalRepairClass:
        if not hypothesis:
            return CanonicalRepairClass.NONE
        cat = hypothesis.category
        cat_str = cat.value if hasattr(cat, "value") else str(cat)
        layer = hypothesis.origin_layer
        layer_str = layer.value if hasattr(layer, "value") else str(layer)

        if cat_str == "TYPOGRAPHY_SCALE_FAILURE":
            return CanonicalRepairClass.CLASS_B_TYPOGRAPHY
        if cat_str in ("GRID_COMPOSITION_FAILURE", "RENDERING_ENGINE_ANOMALY"):
            return CanonicalRepairClass.CLASS_A_GEOMETRY
        if cat_str in ("SEMANTIC_LAYOUT_MISMATCH", "LAYOUT_CAPACITY_EXCEEDED"):
            return CanonicalRepairClass.CLASS_C_LAYOUT_REMAPPING
        if cat_str in ("CONTENT_OVERDENSITY", "CONCEPT_FRAGMENTATION", "INVALID_GROUPING"):
            return CanonicalRepairClass.CLASS_D_BLUEPRINT_REGROUPING
        if cat_str in ("NARRATIVE_DISCONTINUITY", "COGNITIVE_OVERLOAD"):
            return CanonicalRepairClass.CLASS_E_TRANSFORMATION_STRATEGY
        if cat_str in ("WORKSHEET_ANSWER_LEAKAGE", "WORKSHEET_ANTI_INQUIRY_FAILURE",
                       "CITATION_STRUCTURE_FAILURE", "SCIENTIFIC_ARGUMENT_FAILURE"):
            return CanonicalRepairClass.CLASS_F_ARTIFACT_POLICY
        if cat_str == "VALIDATOR_FALSE_POSITIVE":
            return CanonicalRepairClass.CLASS_G_MANUAL_REVIEW

        # Layer fallbacks
        if layer_str == "RENDERING":
            return CanonicalRepairClass.CLASS_A_GEOMETRY
        if layer_str == "SEMANTIC_LAYOUT":
            return CanonicalRepairClass.CLASS_C_LAYOUT_REMAPPING
        if layer_str == "BLUEPRINT":
            return CanonicalRepairClass.CLASS_D_BLUEPRINT_REGROUPING
        if layer_str == "TRANSFORMATION":
            return CanonicalRepairClass.CLASS_E_TRANSFORMATION_STRATEGY

        return CanonicalRepairClass.CLASS_G_MANUAL_REVIEW

        # Layer fallbacks
        if layer == CausalArchitecturalLayer.RENDERING:
            return CanonicalRepairClass.CLASS_A_GEOMETRY
        if layer == CausalArchitecturalLayer.SEMANTIC_LAYOUT:
            return CanonicalRepairClass.CLASS_C_LAYOUT_REMAPPING
        if layer == CausalArchitecturalLayer.BLUEPRINT:
            return CanonicalRepairClass.CLASS_D_BLUEPRINT_REGROUPING
        if layer == CausalArchitecturalLayer.TRANSFORMATION:
            return CanonicalRepairClass.CLASS_E_TRANSFORMATION_STRATEGY

        return CanonicalRepairClass.CLASS_G_MANUAL_REVIEW
