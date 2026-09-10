"""
Universal Document Intelligence System V5 — Review Repair Bridge.

Phase 6: Bridges validated review directives to the deterministic repair planner.
Human directives are INPUTS to repair planning, NOT direct mutation authority.
All mutations must still satisfy RepairSafetyInvariants and pass UQA evaluation.
"""

from __future__ import annotations

from typing import Any, Dict, Optional, Tuple
from pydantic import BaseModel, ConfigDict, Field

from app.quality.repair.mutation_contract import RepairMutationScope
from app.review.contracts.directives import ReviewDirective
from app.review.directives.ontology import DirectiveOntology
from app.review.safety.directive_safety_validator import DirectiveSafetyValidator
from app.review.safety.exceptions import IllegalDirectiveException


class DirectiveRepairHint(BaseModel):
    """Constrained hint delivered to MinimalInterventionRepairPlanner."""
    model_config = ConfigDict(frozen=True)

    directive_id: str
    target_layer: str
    mutation_scope: RepairMutationScope
    target_element_id: Optional[str] = None
    target_page_or_slide: Optional[int] = None
    parameters: Dict[str, Any] = Field(default_factory=dict)
    rationale: str
    validation_signature: str


class ReviewRepairBridge:
    """Translates validated directives into constrained planner hints."""

    LAYER_SCOPE_MAP: Dict[str, RepairMutationScope] = {
        "LEVEL_R0_RENDER_TOKEN": RepairMutationScope.LEVEL_1_LOCAL_TOKEN,
        "LEVEL_R1_COMPONENT_PARAM": RepairMutationScope.LEVEL_2_COMPONENT_GEOMETRY,
        "LEVEL_R2_LAYOUT_STRUCTURE": RepairMutationScope.LEVEL_3_PAGE_COMPOSITION,
        "LEVEL_R3_ARTIFACT_STRUCTURE": RepairMutationScope.LEVEL_4_BLUEPRINT_REGROUPING,
        "LEVEL_R4_SEMANTIC_TRANSFORMATION": RepairMutationScope.LEVEL_5_ARTIFACT_STRUCTURE,
        "LEVEL_R5_SOURCE_INTELLIGENCE": RepairMutationScope.LEVEL_5_ARTIFACT_STRUCTURE,
    }

    @classmethod
    def translate_directive(
        cls,
        directive: ReviewDirective,
        artifact_type: str,
    ) -> DirectiveRepairHint:
        """
        Validates directive through DirectiveSafetyValidator and produces a DirectiveRepairHint.
        Raises IllegalDirectiveException if directive fails safety validation.
        """
        val_res = DirectiveSafetyValidator.validate(directive, artifact_type=artifact_type)
        if not val_res.is_valid:
            raise IllegalDirectiveException(
                directive_id=directive.directive_id,
                violation="; ".join(val_res.violations),
                responsible_subsystem="ReviewRepairBridge",
            )

        spec = DirectiveOntology.get_spec(directive.directive_type)
        layer = spec.escalation_layer if spec else "LEVEL_R2_LAYOUT_STRUCTURE"
        scope = cls.LAYER_SCOPE_MAP.get(layer, RepairMutationScope.LEVEL_2_COMPONENT_GEOMETRY)

        return DirectiveRepairHint(
            directive_id=directive.directive_id,
            target_layer=layer,
            mutation_scope=scope,
            target_element_id=directive.target_element_id,
            target_page_or_slide=directive.target_page_or_slide,
            parameters=dict(directive.parameters),
            rationale=directive.rationale,
            validation_signature=val_res.signature or "",
        )
