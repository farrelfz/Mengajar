"""
Universal Document Intelligence System V5 — Master Causal Attribution Engine.

Phase 3A.1: Coordinates evidence-based causal analysis across all layers. Disentangles
symptoms from root causes, quantifies confidence, and clusters correlated defects.
"""

from __future__ import annotations

from typing import Dict, List, Tuple
from app.quality.causal.artifact_causes import ArtifactCausalRules
from app.quality.causal.cause_catalog import CausalDefectCatalog
from app.quality.causal.confidence import CausalConfidenceEstimator
from app.quality.causal.contracts import (
    CanonicalFailure,
    FailureCluster,
    RootCauseHypothesis,
)
from app.quality.causal.evidence_collector import MultiLayerEvidence
from app.quality.causal.failure_correlation import FailureCorrelationEngine
from app.quality.causal.repair_authority import RepairAuthorityMatrix
from app.quality.causal.taxonomy import (
    ArchitectureLayer,
    CanonicalFailureCode,
    CanonicalRepairClass,
    CausalConfidenceLevel,
    FailureScope,
)


class CausalAttributionEngine:
    """Attributes observed failures to architectural root causes with calibrated confidence."""

    @classmethod
    def attribute(
        cls,
        failures: List[CanonicalFailure],
        evidence: MultiLayerEvidence,
    ) -> Tuple[List[RootCauseHypothesis], List[FailureCluster]]:
        if not failures:
            return [], []

        hypotheses: List[RootCauseHypothesis] = []
        artifact_type = evidence.artifact_type.upper()

        for failure in failures:
            hyp = cls._attribute_single_failure(failure, evidence, artifact_type)
            if hyp:
                hypotheses.append(hyp)

        # Cluster correlated failures on shared pages
        clusters = FailureCorrelationEngine.cluster_failures(failures, evidence)

        return hypotheses, clusters

    @classmethod
    def _attribute_single_failure(
        cls,
        failure: CanonicalFailure,
        evidence: MultiLayerEvidence,
        artifact_type: str,
    ) -> RootCauseHypothesis:
        # 1. Try artifact-specific causal rules
        artifact_hyp = None
        if artifact_type == "PRESENTATION":
            artifact_hyp = ArtifactCausalRules.evaluate_presentation_cause(failure, evidence)
        elif artifact_type == "HANDOUT":
            artifact_hyp = ArtifactCausalRules.evaluate_handout_cause(failure, evidence)
        elif artifact_type == "WORKSHEET":
            artifact_hyp = ArtifactCausalRules.evaluate_worksheet_cause(failure, evidence)
        elif artifact_type in ("SCIENTIFIC_DOCUMENT", "SCIENTIFIC"):
            artifact_hyp = ArtifactCausalRules.evaluate_scientific_cause(failure, evidence)

        if artifact_hyp:
            return artifact_hyp

        # 2. General causal heuristics for cross-artifact symptoms:
        code = failure.failure_code

        # A. TEXT_TOO_SMALL
        if code == CanonicalFailureCode.TEXT_TOO_SMALL:
            # Differentiate: Blueprint overload vs Typography config vs Render scale
            if evidence.blueprint_capacity_exceeded or evidence.is_font_isolated_to_dense_pages:
                policy = RepairAuthorityMatrix.get_repair_policy("BLUEPRINT_CAPACITY_MISMATCH", CausalConfidenceLevel.HIGH)
                return RootCauseHypothesis(
                    cause_code="BLUEPRINT_CAPACITY_MISMATCH",
                    cause_layer=ArchitectureLayer.BLUEPRINT,
                    confidence_score=0.86,
                    confidence_level=CausalConfidenceLevel.HIGH,
                    supporting_evidence=(
                        f"Blueprint item count ({evidence.max_blocks_per_page}) exceeds slot capacity ({evidence.layout_slot_capacity})",
                        "Font size reduction isolated only to overloaded page(s)",
                    ),
                    contradicting_evidence=(),
                    affected_scope=failure.scope,
                    repair_authority=policy.owning_layer,
                    allowed_repair_classes=policy.allowed_repair_classes,
                    forbidden_repairs=policy.forbidden_repairs,
                )
            elif evidence.is_font_globally_small:
                policy = RepairAuthorityMatrix.get_repair_policy("TYPOGRAPHY_CONFIGURATION_FAILURE", CausalConfidenceLevel.HIGH)
                return RootCauseHypothesis(
                    cause_code="TYPOGRAPHY_CONFIGURATION_FAILURE",
                    cause_layer=ArchitectureLayer.TYPOGRAPHY,
                    confidence_score=0.88,
                    confidence_level=CausalConfidenceLevel.HIGH,
                    supporting_evidence=(
                        "Font is small across >70% of document pages regardless of content",
                        "Blueprint block count is within normal operating limits",
                    ),
                    contradicting_evidence=(),
                    affected_scope=FailureScope.SYSTEMIC,
                    repair_authority=policy.owning_layer,
                    allowed_repair_classes=policy.allowed_repair_classes,
                    forbidden_repairs=policy.forbidden_repairs,
                )
            else:
                # Ambiguous: could be template layout or render scale
                hyp1 = RootCauseHypothesis(
                    cause_code="LAYOUT_CAPACITY_MISMATCH",
                    cause_layer=ArchitectureLayer.LAYOUT,
                    confidence_score=0.45,
                    confidence_level=CausalConfidenceLevel.LOW,
                    supporting_evidence=("Font reduction on isolated page without high blueprint block count",),
                    contradicting_evidence=(),
                    affected_scope=failure.scope,
                    repair_authority=ArchitectureLayer.LAYOUT,
                    allowed_repair_classes=(CanonicalRepairClass.CLASS_C_LAYOUT_REMAPPING,),
                    forbidden_repairs=(),
                )
                hyp2 = RootCauseHypothesis(
                    cause_code="RENDER_SCALE_FAILURE",
                    cause_layer=ArchitectureLayer.RENDER,
                    confidence_score=0.40,
                    confidence_level=CausalConfidenceLevel.LOW,
                    supporting_evidence=("Possible viewport scaling discrepancy",),
                    contradicting_evidence=(),
                    affected_scope=failure.scope,
                    repair_authority=ArchitectureLayer.RENDER,
                    allowed_repair_classes=(CanonicalRepairClass.CLASS_A_GEOMETRY,),
                    forbidden_repairs=(),
                )
                top_hyp, _, _ = CausalConfidenceEstimator.arbitrate_competing_hypotheses([hyp1, hyp2])
                return top_hyp or hyp1

        # B. ELEMENT_COLLISION
        if code == CanonicalFailureCode.ELEMENT_COLLISION:
            if evidence.blueprint_capacity_exceeded:
                policy = RepairAuthorityMatrix.get_repair_policy("BLUEPRINT_CAPACITY_MISMATCH", CausalConfidenceLevel.HIGH)
                return RootCauseHypothesis(
                    cause_code="BLUEPRINT_CAPACITY_MISMATCH",
                    cause_layer=ArchitectureLayer.BLUEPRINT,
                    confidence_score=0.85,
                    confidence_level=CausalConfidenceLevel.HIGH,
                    supporting_evidence=(
                        f"Items forced into container ({evidence.max_blocks_per_page}) collide due to space exhaustion",
                    ),
                    contradicting_evidence=(),
                    affected_scope=failure.scope,
                    repair_authority=policy.owning_layer,
                    allowed_repair_classes=policy.allowed_repair_classes,
                    forbidden_repairs=policy.forbidden_repairs,
                )
            else:
                policy = RepairAuthorityMatrix.get_repair_policy("LAYOUT_CAPACITY_MISMATCH", CausalConfidenceLevel.HIGH)
                return RootCauseHypothesis(
                    cause_code="LAYOUT_CAPACITY_MISMATCH",
                    cause_layer=ArchitectureLayer.LAYOUT,
                    confidence_score=0.80,
                    confidence_level=CausalConfidenceLevel.HIGH,
                    supporting_evidence=("Template flex/grid container overlap without high entity count",),
                    contradicting_evidence=(),
                    affected_scope=failure.scope,
                    repair_authority=policy.owning_layer,
                    allowed_repair_classes=policy.allowed_repair_classes,
                    forbidden_repairs=policy.forbidden_repairs,
                )

        # C. BLANK_PAGE
        if code == CanonicalFailureCode.BLANK_PAGE:
            policy = RepairAuthorityMatrix.get_repair_policy("BLANK_PAGE_INJECTION", CausalConfidenceLevel.HIGH)
            return RootCauseHypothesis(
                cause_code="BLANK_PAGE_INJECTION",
                cause_layer=ArchitectureLayer.COMPOSITION,
                confidence_score=0.92,
                confidence_level=CausalConfidenceLevel.HIGH,
                supporting_evidence=("Physical page has 0 foreground pixels (spurious break or empty container)",),
                contradicting_evidence=(),
                affected_scope=failure.scope,
                repair_authority=policy.owning_layer,
                allowed_repair_classes=policy.allowed_repair_classes,
                forbidden_repairs=policy.forbidden_repairs,
            )

        # D. REPETITION_STREAK / LAYOUT_MONOTONY
        if code in (CanonicalFailureCode.REPETITION_STREAK, CanonicalFailureCode.LAYOUT_MONOTONY):
            policy = RepairAuthorityMatrix.get_repair_policy("MONOTONOUS_TEMPLATE_ASSIGNMENT", CausalConfidenceLevel.HIGH)
            return RootCauseHypothesis(
                cause_code="MONOTONOUS_TEMPLATE_ASSIGNMENT",
                cause_layer=ArchitectureLayer.LAYOUT,
                confidence_score=0.84,
                confidence_level=CausalConfidenceLevel.HIGH,
                supporting_evidence=("Unjustified layout similarity across multiple consecutive pages",),
                contradicting_evidence=(),
                affected_scope=failure.scope,
                repair_authority=policy.owning_layer,
                allowed_repair_classes=policy.allowed_repair_classes,
                forbidden_repairs=policy.forbidden_repairs,
            )

        # Generic default
        return RootCauseHypothesis(
            cause_code="UNCLASSIFIED_DEFECT",
            cause_layer=ArchitectureLayer.RENDER,
            confidence_score=0.35,
            confidence_level=CausalConfidenceLevel.LOW,
            supporting_evidence=(failure.symptom,),
            contradicting_evidence=(),
            affected_scope=failure.scope,
            repair_authority=ArchitectureLayer.ARTIFACT_POLICY,
            allowed_repair_classes=(CanonicalRepairClass.CLASS_G_MANUAL_REVIEW,),
            forbidden_repairs=("AUTOMATIC_REPAIR_FORBIDDEN",),
        )
