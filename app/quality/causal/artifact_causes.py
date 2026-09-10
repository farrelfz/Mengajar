"""
Universal Document Intelligence System V5 — Artifact-Specific Causal Rules.

Phase 3A.1: Domain-specific causal heuristics for Presentation, Handout,
Worksheet, and Scientific Document to ensure precise layer attribution.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from app.quality.causal.contracts import CanonicalFailure, RootCauseHypothesis
from app.quality.causal.evidence_collector import MultiLayerEvidence
from app.quality.causal.taxonomy import (
    ArchitectureLayer,
    CanonicalFailureCode,
    CanonicalRepairClass,
    CausalConfidenceLevel,
    FailureScope,
)


class ArtifactCausalRules:
    """Evaluates artifact-specific failures and derives calibrated root cause hypotheses."""

    @classmethod
    def evaluate_presentation_cause(
        cls,
        failure: CanonicalFailure,
        evidence: MultiLayerEvidence,
    ) -> RootCauseHypothesis | None:
        code = failure.failure_code

        # 1. Presentation Handout Collapse
        if code == CanonicalFailureCode.PRESENTATION_HANDOUT_COLLAPSE or (
            code == CanonicalFailureCode.DENSITY_OVERLOAD and evidence.mean_raster_density > 0.25
        ):
            return RootCauseHypothesis(
                cause_code="COMPRESSION_FAILURE",
                cause_layer=ArchitectureLayer.TRANSFORMATION,
                confidence_score=0.88,
                confidence_level=CausalConfidenceLevel.HIGH,
                supporting_evidence=(
                    "Dense reading text transferred directly into slide format without semantic compression",
                    "Slide text length exceeds presentation cognitive capacity",
                ),
                contradicting_evidence=(),
                affected_scope=failure.scope,
                repair_authority=ArchitectureLayer.TRANSFORMATION,
                allowed_repair_classes=(
                    CanonicalRepairClass.CLASS_E_TRANSFORMATION_STRATEGY,
                    CanonicalRepairClass.CLASS_D_BLUEPRINT_REGROUPING,
                ),
                forbidden_repairs=("REDUCE_LINE_HEIGHT", "TINY_FONT_SHRINK"),
            )

        # 2. Card Overload
        if code == CanonicalFailureCode.CARD_OVERLOAD:
            return RootCauseHypothesis(
                cause_code="BLUEPRINT_CAPACITY_MISMATCH",
                cause_layer=ArchitectureLayer.BLUEPRINT,
                confidence_score=0.85,
                confidence_level=CausalConfidenceLevel.HIGH,
                supporting_evidence=(
                    f"Slide contains >8 discrete cards/blocks, exceeding working memory limits",
                    f"Planned blocks per slide ({evidence.max_blocks_per_page}) > limit 5",
                ),
                contradicting_evidence=(),
                affected_scope=failure.scope,
                repair_authority=ArchitectureLayer.BLUEPRINT,
                allowed_repair_classes=(
                    CanonicalRepairClass.CLASS_D_BLUEPRINT_REGROUPING,
                    CanonicalRepairClass.CLASS_C_LAYOUT_REMAPPING,
                ),
                forbidden_repairs=("TINY_FONT_SHRINK",),
            )

        return None

    @classmethod
    def evaluate_handout_cause(
        cls,
        failure: CanonicalFailure,
        evidence: MultiLayerEvidence,
    ) -> RootCauseHypothesis | None:
        code = failure.failure_code

        # 1. Orphan Heading
        if code == CanonicalFailureCode.ORPHAN_HEADING:
            return RootCauseHypothesis(
                cause_code="PAGINATION_BREAK_PLACEMENT_FAILURE",
                cause_layer=ArchitectureLayer.COMPOSITION,
                confidence_score=0.92,
                confidence_level=CausalConfidenceLevel.HIGH,
                supporting_evidence=(
                    "Section heading placed near bottom of page without room for body continuation",
                ),
                contradicting_evidence=(),
                affected_scope=failure.scope,
                repair_authority=ArchitectureLayer.COMPOSITION,
                allowed_repair_classes=(
                    CanonicalRepairClass.CLASS_A_GEOMETRY,
                    CanonicalRepairClass.CLASS_C_LAYOUT_REMAPPING,
                ),
                forbidden_repairs=("DELETE_HEADING",),
            )

        # 2. Wall of Text
        if code == CanonicalFailureCode.WALL_OF_TEXT:
            return RootCauseHypothesis(
                cause_code="SEMANTIC_GROUPING_FAILURE",
                cause_layer=ArchitectureLayer.TRANSFORMATION,
                confidence_score=0.86,
                confidence_level=CausalConfidenceLevel.HIGH,
                supporting_evidence=(
                    "Single unbroken paragraph block exceeds 2200 characters",
                    "Missing explanatory section chunking or callout boxes",
                ),
                contradicting_evidence=(),
                affected_scope=failure.scope,
                repair_authority=ArchitectureLayer.TRANSFORMATION,
                allowed_repair_classes=(
                    CanonicalRepairClass.CLASS_E_TRANSFORMATION_STRATEGY,
                    CanonicalRepairClass.CLASS_D_BLUEPRINT_REGROUPING,
                ),
                forbidden_repairs=("JUST_INCREASE_MARGINS",),
            )

        return None

    @classmethod
    def evaluate_worksheet_cause(
        cls,
        failure: CanonicalFailure,
        evidence: MultiLayerEvidence,
    ) -> RootCauseHypothesis | None:
        code = failure.failure_code

        # 1. Quiz Collapse
        if code == CanonicalFailureCode.WORKSHEET_QUIZ_COLLAPSE:
            return RootCauseHypothesis(
                cause_code="TRANSFORMATION_SELECTION_FAILURE",
                cause_layer=ArchitectureLayer.TRANSFORMATION,
                confidence_score=0.89,
                confidence_level=CausalConfidenceLevel.HIGH,
                supporting_evidence=(
                    "Worksheet transformed into monolithic question list lacking inquiry progression",
                    "Phenomenon observation and student analysis phases missing",
                ),
                contradicting_evidence=(),
                affected_scope=FailureScope.ARTIFACT_WIDE,
                repair_authority=ArchitectureLayer.TRANSFORMATION,
                allowed_repair_classes=(
                    CanonicalRepairClass.CLASS_E_TRANSFORMATION_STRATEGY,
                ),
                forbidden_repairs=("LAYOUT_CSS_PATCH",),
            )

        # 2. Anti-Spoiling Failure
        if code == CanonicalFailureCode.WORKSHEET_SPOILING_FAILURE:
            return RootCauseHypothesis(
                cause_code="ANTI_SPOILING_POLICY_BREACH",
                cause_layer=ArchitectureLayer.ARTIFACT_POLICY,
                confidence_score=0.96,
                confidence_level=CausalConfidenceLevel.HIGH,
                supporting_evidence=(
                    "Solution / explanation text rendered into student workspace area",
                ),
                contradicting_evidence=(),
                affected_scope=failure.scope,
                repair_authority=ArchitectureLayer.ARTIFACT_POLICY,
                allowed_repair_classes=(
                    CanonicalRepairClass.CLASS_F_ARTIFACT_POLICY,
                    CanonicalRepairClass.CLASS_E_TRANSFORMATION_STRATEGY,
                ),
                forbidden_repairs=("CSS_OPACITY_ZERO",),
            )

        # 3. Insufficient Workspace
        if code in (CanonicalFailureCode.WORKSHEET_WORKSPACE_FAILURE, CanonicalFailureCode.WORKSHEET_WORKSPACE_INSUFFICIENT):
            return RootCauseHypothesis(
                cause_code="WORKSPACE_ALLOCATION_FAILURE",
                cause_layer=ArchitectureLayer.BLUEPRINT,
                confidence_score=0.85,
                confidence_level=CausalConfidenceLevel.HIGH,
                supporting_evidence=(
                    "Questions lack designated vector drawing response boxes of height >= 35pt",
                ),
                contradicting_evidence=(),
                affected_scope=failure.scope,
                repair_authority=ArchitectureLayer.BLUEPRINT,
                allowed_repair_classes=(
                    CanonicalRepairClass.CLASS_A_GEOMETRY,
                    CanonicalRepairClass.CLASS_D_BLUEPRINT_REGROUPING,
                ),
                forbidden_repairs=("SUPPRESS_WORKSPACE_CHECK",),
            )

        return None

    @classmethod
    def evaluate_scientific_cause(
        cls,
        failure: CanonicalFailure,
        evidence: MultiLayerEvidence,
    ) -> RootCauseHypothesis | None:
        code = failure.failure_code

        # 1. Scientific Citation Invisible
        if code == CanonicalFailureCode.SCIENTIFIC_CITATION_INVISIBLE:
            # Check if citations exist in source metadata
            source_has_citations = evidence.raw_metadata.get("source_citations_count", 1) > 0
            if source_has_citations:
                return RootCauseHypothesis(
                    cause_code="CITATION_RENDER_SUPPRESSION",
                    cause_layer=ArchitectureLayer.COMPOSITION,
                    confidence_score=0.87,
                    confidence_level=CausalConfidenceLevel.HIGH,
                    supporting_evidence=(
                        "Citations exist in source metadata but zero citation markers appear in rendered PDF text",
                        "Renderer template omitted bibliography or bracketed in-text references",
                    ),
                    contradicting_evidence=(),
                    affected_scope=FailureScope.ARTIFACT_WIDE,
                    repair_authority=ArchitectureLayer.COMPOSITION,
                    allowed_repair_classes=(
                        CanonicalRepairClass.CLASS_F_ARTIFACT_POLICY,
                        CanonicalRepairClass.CLASS_C_LAYOUT_REMAPPING,
                    ),
                    forbidden_repairs=("REWRITE_SOURCE_CLAIMS",),
                )
            else:
                return RootCauseHypothesis(
                    cause_code="EVIDENCE_DISCIPLINE_FAILURE",
                    cause_layer=ArchitectureLayer.SOURCE,
                    confidence_score=0.82,
                    confidence_level=CausalConfidenceLevel.HIGH,
                    supporting_evidence=("Source document itself contains zero academic citations",),
                    contradicting_evidence=(),
                    affected_scope=FailureScope.ARTIFACT_WIDE,
                    repair_authority=ArchitectureLayer.SOURCE,
                    allowed_repair_classes=(CanonicalRepairClass.CLASS_F_ARTIFACT_POLICY,),
                    forbidden_repairs=("FABRICATE_FAKE_CITATIONS",),
                )

        # 2. BAB Hierarchy Inversion
        if code == CanonicalFailureCode.SCIENTIFIC_HIERARCHY_FAILURE:
            return RootCauseHypothesis(
                cause_code="SEQUENCING_FAILURE",
                cause_layer=ArchitectureLayer.TRANSFORMATION,
                confidence_score=0.94,
                confidence_level=CausalConfidenceLevel.HIGH,
                supporting_evidence=(
                    "Canonical academic chapter sequence violated (BAB I-V out of order)",
                ),
                contradicting_evidence=(),
                affected_scope=FailureScope.ARTIFACT_WIDE,
                repair_authority=ArchitectureLayer.TRANSFORMATION,
                allowed_repair_classes=(
                    CanonicalRepairClass.CLASS_E_TRANSFORMATION_STRATEGY,
                ),
                forbidden_repairs=("IGNORE_ACADEMIC_CONVENTIONS",),
            )

        return None
