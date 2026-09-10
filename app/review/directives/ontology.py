"""
Universal Document Intelligence System V5 — Review Directive Ontology.

Phase 6: Defines canonical rules, architectural layer mapping (R0–R5),
and artifact format compatibility for all review directives.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Set, Tuple
from pydantic import BaseModel, ConfigDict, Field

from app.review.contracts.enums import DirectiveCategory, DirectiveType


class DirectiveSpec(BaseModel):
    """Specification of an allowed review directive."""
    model_config = ConfigDict(frozen=True)

    directive_type: DirectiveType
    category: DirectiveCategory
    applicable_artifacts: Tuple[str, ...]
    escalation_layer: str  # LEVEL_R0 to LEVEL_R5
    required_parameters: Tuple[str, ...] = Field(default_factory=tuple)
    forbidden_parameters: Tuple[str, ...] = Field(default_factory=tuple)
    description: str


class DirectiveOntology:
    """Registry of canonical directive definitions and constraints."""

    SPECS: Dict[DirectiveType, DirectiveSpec] = {
        DirectiveType.SPLIT_SLIDE: DirectiveSpec(
            directive_type=DirectiveType.SPLIT_SLIDE,
            category=DirectiveCategory.REPAIR,
            applicable_artifacts=("PRESENTATION",),
            escalation_layer="LEVEL_R3_ARTIFACT_STRUCTURE",
            required_parameters=("split_index",),
            description="Splits an overcrowded slide into two progressive reveal slides.",
        ),
        DirectiveType.REMAP_COMPONENT: DirectiveSpec(
            directive_type=DirectiveType.REMAP_COMPONENT,
            category=DirectiveCategory.REPAIR,
            applicable_artifacts=("PRESENTATION", "HANDOUT", "WORKSHEET"),
            escalation_layer="LEVEL_R2_LAYOUT_STRUCTURE",
            required_parameters=("target_container",),
            description="Remaps a content block to a different spatial slot or container.",
        ),
        DirectiveType.ADJUST_TOKEN: DirectiveSpec(
            directive_type=DirectiveType.ADJUST_TOKEN,
            category=DirectiveCategory.REPAIR,
            applicable_artifacts=("PRESENTATION", "HANDOUT", "WORKSHEET", "SCIENTIFIC_DOCUMENT", "KTI"),
            escalation_layer="LEVEL_R0_RENDER_TOKEN",
            required_parameters=("token_name", "value"),
            description="Adjusts fine-grained layout token (e.g., padding, font-size, line-height).",
        ),
        DirectiveType.RECOMPOSE_PAGE: DirectiveSpec(
            directive_type=DirectiveType.RECOMPOSE_PAGE,
            category=DirectiveCategory.REPAIR,
            applicable_artifacts=("HANDOUT", "WORKSHEET", "SCIENTIFIC_DOCUMENT", "KTI"),
            escalation_layer="LEVEL_R3_ARTIFACT_STRUCTURE",
            description="Recomposes section layout to fix overflow or awkward column wrapping.",
        ),
        DirectiveType.REPAGINATE: DirectiveSpec(
            directive_type=DirectiveType.REPAGINATE,
            category=DirectiveCategory.REPAIR,
            applicable_artifacts=("HANDOUT", "WORKSHEET", "SCIENTIFIC_DOCUMENT", "KTI"),
            escalation_layer="LEVEL_R2_LAYOUT_STRUCTURE",
            description="Forces explicit page-break before or after designated section.",
        ),
        DirectiveType.REQUEST_SOURCE_RECHECK: DirectiveSpec(
            directive_type=DirectiveType.REQUEST_SOURCE_RECHECK,
            category=DirectiveCategory.EVIDENCE,
            applicable_artifacts=("PRESENTATION", "HANDOUT", "WORKSHEET", "SCIENTIFIC_DOCUMENT", "KTI"),
            escalation_layer="LEVEL_R5_SOURCE_INTELLIGENCE",
            description="Flags source manifest discrepancy requiring upstream re-verification.",
        ),
        DirectiveType.REQUEST_CITATION_BACKING: DirectiveSpec(
            directive_type=DirectiveType.REQUEST_CITATION_BACKING,
            category=DirectiveCategory.EVIDENCE,
            applicable_artifacts=("SCIENTIFIC_DOCUMENT", "KTI"),
            escalation_layer="LEVEL_R5_SOURCE_INTELLIGENCE",
            required_parameters=("claim_id",),
            description="Demands verified primary source or DOI for scientific claim.",
        ),
        DirectiveType.WITHHOLD_EXPLANATION: DirectiveSpec(
            directive_type=DirectiveType.WITHHOLD_EXPLANATION,
            category=DirectiveCategory.PEDAGOGICAL,
            applicable_artifacts=("WORKSHEET",),
            escalation_layer="LEVEL_R4_SEMANTIC_TRANSFORMATION",
            description="Enforces anti-spoiling by withholding solution text from student activity section.",
        ),
        DirectiveType.RESTORE_INQUIRY_ARC: DirectiveSpec(
            directive_type=DirectiveType.RESTORE_INQUIRY_ARC,
            category=DirectiveCategory.PEDAGOGICAL,
            applicable_artifacts=("WORKSHEET",),
            escalation_layer="LEVEL_R4_SEMANTIC_TRANSFORMATION",
            description="Restores observation -> prediction -> investigation sequence.",
        ),
        DirectiveType.REDUCE_COGNITIVE_LOAD: DirectiveSpec(
            directive_type=DirectiveType.REDUCE_COGNITIVE_LOAD,
            category=DirectiveCategory.PEDAGOGICAL,
            applicable_artifacts=("PRESENTATION", "HANDOUT"),
            escalation_layer="LEVEL_R3_ARTIFACT_STRUCTURE",
            description="Prunes tertiary details or bullet points to restore visual focus.",
        ),
        DirectiveType.CONFIRM_ROOT_CAUSE: DirectiveSpec(
            directive_type=DirectiveType.CONFIRM_ROOT_CAUSE,
            category=DirectiveCategory.DIAGNOSIS,
            applicable_artifacts=("PRESENTATION", "HANDOUT", "WORKSHEET", "SCIENTIFIC_DOCUMENT", "KTI"),
            escalation_layer="LEVEL_R1_COMPONENT_PARAM",
            description="Confirms automated root-cause hypothesis.",
        ),
        DirectiveType.RECLASSIFY_ROOT_CAUSE: DirectiveSpec(
            directive_type=DirectiveType.RECLASSIFY_ROOT_CAUSE,
            category=DirectiveCategory.DIAGNOSIS,
            applicable_artifacts=("PRESENTATION", "HANDOUT", "WORKSHEET", "SCIENTIFIC_DOCUMENT", "KTI"),
            escalation_layer="LEVEL_R1_COMPONENT_PARAM",
            required_parameters=("new_root_cause",),
            description="Reclassifies root-cause diagnosis to different architectural layer.",
        ),
        DirectiveType.ESCALATE: DirectiveSpec(
            directive_type=DirectiveType.ESCALATE,
            category=DirectiveCategory.GOVERNANCE,
            applicable_artifacts=("PRESENTATION", "HANDOUT", "WORKSHEET", "SCIENTIFIC_DOCUMENT", "KTI"),
            escalation_layer="LEVEL_R5_SOURCE_INTELLIGENCE",
            description="Escalates case to senior disciplinary specialist or principal investigator.",
        ),
        DirectiveType.PROPOSE_GOLDEN_CASE: DirectiveSpec(
            directive_type=DirectiveType.PROPOSE_GOLDEN_CASE,
            category=DirectiveCategory.GOVERNANCE,
            applicable_artifacts=("PRESENTATION", "HANDOUT", "WORKSHEET", "SCIENTIFIC_DOCUMENT", "KTI"),
            escalation_layer="LEVEL_R5_SOURCE_INTELLIGENCE",
            description="Proposes reviewed artifact as a new Golden Corpus reference or test case.",
        ),
    }

    @classmethod
    def get_spec(cls, dtype: DirectiveType) -> Optional[DirectiveSpec]:
        return cls.SPECS.get(dtype)

    @classmethod
    def is_compatible(cls, dtype: DirectiveType, artifact_type: str) -> bool:
        spec = cls.get_spec(dtype)
        if not spec:
            return False
        return artifact_type.upper() in [a.upper() for a in spec.applicable_artifacts]
