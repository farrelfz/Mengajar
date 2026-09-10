"""
Universal Document Intelligence System V5 — Causal Defect Catalog.

Phase 3A.1: Formal catalog of architectural root causes with observable signatures,
evidence prerequisites, owning layer attribution, and safe repair permissions.
"""

from __future__ import annotations

from typing import Dict, List, Tuple
from pydantic import BaseModel, ConfigDict, Field

from app.quality.causal.taxonomy import (
    ArchitectureLayer,
    CanonicalFailureCode,
    CanonicalRepairClass,
)


class CauseDefinition(BaseModel):
    """Formal definition of a potential root cause."""
    model_config = ConfigDict(frozen=True)

    cause_code: str
    layer: ArchitectureLayer
    description: str
    observable_signatures: Tuple[str, ...]
    possible_symptoms: Tuple[CanonicalFailureCode, ...]
    required_evidence: Tuple[str, ...] = Field(default_factory=tuple)
    contradicting_evidence: Tuple[str, ...] = Field(default_factory=tuple)
    repair_authority: ArchitectureLayer
    allowed_repair_classes: Tuple[CanonicalRepairClass, ...] = Field(default_factory=tuple)
    forbidden_repairs: Tuple[str, ...] = Field(default_factory=tuple)


class CausalDefectCatalog:
    """Canonical registry of root causes across all architectural layers."""

    DEFINITIONS: Dict[str, CauseDefinition] = {
        # 1. Blueprint Capacity Mismatch
        "BLUEPRINT_CAPACITY_MISMATCH": CauseDefinition(
            cause_code="BLUEPRINT_CAPACITY_MISMATCH",
            layer=ArchitectureLayer.BLUEPRINT,
            description="Artifact blueprint planned more content items/beats on a page than the physical viewport can accommodate.",
            observable_signatures=(
                "High planned block count on affected page",
                "Cognitive load index > 1.2",
                "Font reduction isolated only to overloaded page(s)",
            ),
            possible_symptoms=(
                CanonicalFailureCode.TEXT_TOO_SMALL,
                CanonicalFailureCode.ELEMENT_COLLISION,
                CanonicalFailureCode.DENSITY_OVERLOAD,
                CanonicalFailureCode.CARD_OVERLOAD,
            ),
            required_evidence=("blueprint_blocks > capacity", "font_isolated_to_dense_pages"),
            contradicting_evidence=("font_globally_small", "blueprint_blocks <= capacity"),
            repair_authority=ArchitectureLayer.BLUEPRINT,
            allowed_repair_classes=(
                CanonicalRepairClass.CLASS_D_BLUEPRINT_REGROUPING,
                CanonicalRepairClass.CLASS_C_LAYOUT_REMAPPING,
            ),
            forbidden_repairs=("GLOBAL_FONT_SHRINK", "TEXT_CLIPPING_SUPPRESSION"),
        ),

        # 2. Typography Configuration Failure
        "TYPOGRAPHY_CONFIGURATION_FAILURE": CauseDefinition(
            cause_code="TYPOGRAPHY_CONFIGURATION_FAILURE",
            layer=ArchitectureLayer.TYPOGRAPHY,
            description="CSS type scale or base font size configuration specifies an unreadable or disproportionate font.",
            observable_signatures=(
                "Globally small font size across all pages regardless of content density",
                "Normal blueprint block counts",
                "No layout overflow",
            ),
            possible_symptoms=(
                CanonicalFailureCode.TEXT_TOO_SMALL,
                CanonicalFailureCode.VISUAL_HIERARCHY_FAILURE,
            ),
            required_evidence=("is_font_globally_small", "not blueprint_capacity_exceeded"),
            contradicting_evidence=("font_isolated_to_dense_pages",),
            repair_authority=ArchitectureLayer.TYPOGRAPHY,
            allowed_repair_classes=(
                CanonicalRepairClass.CLASS_B_TYPOGRAPHY,
            ),
            forbidden_repairs=("CONTENT_SPLIT", "REGENERATE_BLUEPRINT"),
        ),

        # 3. Layout Capacity Mismatch
        "LAYOUT_CAPACITY_MISMATCH": CauseDefinition(
            cause_code="LAYOUT_CAPACITY_MISMATCH",
            layer=ArchitectureLayer.LAYOUT,
            description="The selected layout template (e.g. 2-card grid) cannot hold the planned items without element collision.",
            observable_signatures=(
                "Items exceed template slot capacity",
                "Element collision occurs within card containers",
            ),
            possible_symptoms=(
                CanonicalFailureCode.ELEMENT_COLLISION,
                CanonicalFailureCode.TEXT_CLIPPING,
                CanonicalFailureCode.CARD_OVERLOAD,
            ),
            required_evidence=("template_slots_exceeded",),
            contradicting_evidence=(),
            repair_authority=ArchitectureLayer.LAYOUT,
            allowed_repair_classes=(
                CanonicalRepairClass.CLASS_C_LAYOUT_REMAPPING,
                CanonicalRepairClass.CLASS_A_GEOMETRY,
            ),
            forbidden_repairs=("TEXT_CLIPPING_SUPPRESSION",),
        ),

        # 4. Render Viewport Scaling Failure
        "RENDER_SCALE_FAILURE": CauseDefinition(
            cause_code="RENDER_SCALE_FAILURE",
            layer=ArchitectureLayer.RENDER,
            description="Headless browser viewport zoom or print media CSS DPI scaling resulted in off-boundary clipping.",
            observable_signatures=(
                "Text clipping outside page boundaries across multiple pages",
                "Normal font sizes and content counts",
            ),
            possible_symptoms=(
                CanonicalFailureCode.TEXT_CLIPPING,
                CanonicalFailureCode.PAGE_BOUNDARY_VIOLATION,
            ),
            required_evidence=("clipping_without_overload",),
            contradicting_evidence=("dense_content_overflow",),
            repair_authority=ArchitectureLayer.RENDER,
            allowed_repair_classes=(
                CanonicalRepairClass.CLASS_A_GEOMETRY,
            ),
            forbidden_repairs=("CONTENT_DELETION",),
        ),

        # 5. Transformation Selection Failure (Quiz Collapse)
        "TRANSFORMATION_SELECTION_FAILURE": CauseDefinition(
            cause_code="TRANSFORMATION_SELECTION_FAILURE",
            layer=ArchitectureLayer.TRANSFORMATION,
            description="Artifact transformer repeatedly selected question entities without scaffolding phenomenon or inquiry phases.",
            observable_signatures=(
                "High question count but <35% inquiry keyword presence",
                "Missing prediction, observation, or analysis phases",
            ),
            possible_symptoms=(
                CanonicalFailureCode.WORKSHEET_QUIZ_COLLAPSE,
                CanonicalFailureCode.WORKSHEET_INQUIRY_FLOW_FAILURE,
            ),
            required_evidence=("high_quiz_low_inquiry",),
            contradicting_evidence=("inquiry_coverage_adequate",),
            repair_authority=ArchitectureLayer.TRANSFORMATION,
            allowed_repair_classes=(
                CanonicalRepairClass.CLASS_E_TRANSFORMATION_STRATEGY,
            ),
            forbidden_repairs=("LAYOUT_CSS_PATCH",),
        ),

        # 6. Anti-Spoiling Policy Breach
        "ANTI_SPOILING_POLICY_BREACH": CauseDefinition(
            cause_code="ANTI_SPOILING_POLICY_BREACH",
            layer=ArchitectureLayer.ARTIFACT_POLICY,
            description="Renderer template or transformation included answers/explanations directly in student activity sheet.",
            observable_signatures=(
                "Kunci jawaban or full answer text printed in student activity workspace",
            ),
            possible_symptoms=(
                CanonicalFailureCode.WORKSHEET_SPOILING_FAILURE,
            ),
            required_evidence=("answer_text_in_student_canvas",),
            contradicting_evidence=(),
            repair_authority=ArchitectureLayer.ARTIFACT_POLICY,
            allowed_repair_classes=(
                CanonicalRepairClass.CLASS_F_ARTIFACT_POLICY,
                CanonicalRepairClass.CLASS_E_TRANSFORMATION_STRATEGY,
            ),
            forbidden_repairs=("CSS_OPACITY_ZERO",),
        ),

        # 7. Citation Render Suppression
        "CITATION_RENDER_SUPPRESSION": CauseDefinition(
            cause_code="CITATION_RENDER_SUPPRESSION",
            layer=ArchitectureLayer.COMPOSITION,
            description="Academic citations exist in the source metadata and blueprint, but were omitted from the rendered HTML/PDF body.",
            observable_signatures=(
                "Source and blueprint have valid citations",
                "Rendered PDF contains 0 citation anchors in body",
            ),
            possible_symptoms=(
                CanonicalFailureCode.SCIENTIFIC_CITATION_INVISIBLE,
            ),
            required_evidence=("citations_exist_in_source_but_missing_in_pdf",),
            contradicting_evidence=("source_has_zero_citations",),
            repair_authority=ArchitectureLayer.COMPOSITION,
            allowed_repair_classes=(
                CanonicalRepairClass.CLASS_F_ARTIFACT_POLICY,
                CanonicalRepairClass.CLASS_C_LAYOUT_REMAPPING,
            ),
            forbidden_repairs=("SOURCE_REWRITE",),
        ),

        # 8. Source Grounding Breakdown
        "SOURCE_GROUNDING_BREAKDOWN": CauseDefinition(
            cause_code="SOURCE_GROUNDING_BREAKDOWN",
            layer=ArchitectureLayer.SOURCE,
            description="Claims or metrics in the artifact have no factual grounding in the source manifest.",
            observable_signatures=(
                "Unreferenced claims in final text",
                "Fabricated metrics",
            ),
            possible_symptoms=(
                CanonicalFailureCode.UNSUPPORTED_CLAIM,
                CanonicalFailureCode.SOURCE_GROUNDING_FAILURE,
            ),
            required_evidence=("ungrounded_entities",),
            contradicting_evidence=(),
            repair_authority=ArchitectureLayer.SOURCE,
            allowed_repair_classes=(
                CanonicalRepairClass.CLASS_F_ARTIFACT_POLICY,
            ),
            forbidden_repairs=("AUTO_FABRICATE_SOURCE",),
        ),

        # 9. Monotonous Template Assignment
        "MONOTONOUS_TEMPLATE_ASSIGNMENT": CauseDefinition(
            cause_code="MONOTONOUS_TEMPLATE_ASSIGNMENT",
            layer=ArchitectureLayer.LAYOUT,
            description="Renderer or layout engine assigned identical visual templates across 4+ consecutive slides with low information gain.",
            observable_signatures=(
                "Consecutive slides share same quadrant occupancy",
                "Low semantic information delta",
            ),
            possible_symptoms=(
                CanonicalFailureCode.REPETITION_STREAK,
                CanonicalFailureCode.LAYOUT_MONOTONY,
            ),
            required_evidence=("high_similarity_low_info_gain",),
            contradicting_evidence=("progressive_reveal_sequence",),
            repair_authority=ArchitectureLayer.LAYOUT,
            allowed_repair_classes=(
                CanonicalRepairClass.CLASS_C_LAYOUT_REMAPPING,
            ),
            forbidden_repairs=("MERGE_ALL_SLIDES",),
        ),

        # 10. Blank Page Injection
        "BLANK_PAGE_INJECTION": CauseDefinition(
            cause_code="BLANK_PAGE_INJECTION",
            layer=ArchitectureLayer.COMPOSITION,
            description="Spurious CSS page-break-after or empty DOM container created an unpopulated physical page.",
            observable_signatures=(
                "Physical PDF page has 0 foreground pixels or visual density < 0.0005",
            ),
            possible_symptoms=(
                CanonicalFailureCode.BLANK_PAGE,
            ),
            required_evidence=("zero_foreground_pixels",),
            contradicting_evidence=(),
            repair_authority=ArchitectureLayer.COMPOSITION,
            allowed_repair_classes=(
                CanonicalRepairClass.CLASS_A_GEOMETRY,
            ),
            forbidden_repairs=("FILL_WITH_LOREM_IPSUM",),
        ),
    }

    @classmethod
    def get_cause(cls, cause_code: str) -> CauseDefinition | None:
        return cls.DEFINITIONS.get(cause_code)
