"""
Universal Document Intelligence System V5 — Presentation Component Reflow Actuator.

Phase 4: Causal transformation operator resolving ELEMENT_COLLISION, OVERLAPPING_CONTENT,
and grid geometry violations by reflowing colliding cards, converting multi-column
grids to structured vertical stacks, and optimizing spacing constraints.
"""

from __future__ import annotations

import copy
import hashlib
import logging
from typing import Any, Dict, List, Optional, Tuple

from app.quality.repair.actuation.contracts import (
    RepairActuationRequest,
    RepairActuationResult,
    RepairActuator,
)
from app.quality.repair.actuation.mutation_layers import TransformationLayer
from app.quality.repair.effectiveness.causal_reach import CausalReach
from app.quality.repair.effectiveness.contracts import RepairExecutionStatus
from app.quality.repair.effectiveness.zero_effect_detector import DomainFingerprinter
from app.quality.repair.root_cause import RootCauseType

logger = logging.getLogger("quality.repair.actuation.presentation.reflow")


class PresentationComponentReflowActuator:
    """Actuator that physically reflows colliding components in presentations."""

    @property
    def actuator_id(self) -> str:
        return "presentation_component_reflow"

    @property
    def supported_artifact_types(self) -> Tuple[str, ...]:
        return ("PRESENTATION",)

    @property
    def supported_root_causes(self) -> Tuple[RootCauseType, ...]:
        return (
            RootCauseType.GRID_GEOMETRY,
            RootCauseType.SEMANTIC_LAYOUT_MAPPING,
            RootCauseType.SPATIAL_COLLISION,
            RootCauseType.TYPOGRAPHY,
        )

    @property
    def maximum_causal_reach(self) -> CausalReach:
        return CausalReach.COMPONENT_SPATIAL_STRUCTURE

    @property
    def transformation_layer(self) -> TransformationLayer:
        return TransformationLayer.LAYER_1_COMPONENT

    def can_actuate(self, request: RepairActuationRequest, blueprint: Any) -> bool:
        if request.artifact_type.strip().upper() != "PRESENTATION":
            return False
        has_beats = hasattr(blueprint, "beats") and bool(blueprint.beats)
        has_slides = hasattr(blueprint, "slides") and bool(blueprint.slides)
        return has_beats or has_slides

    def actuate(
        self,
        request: RepairActuationRequest,
        blueprint: Any,
    ) -> Tuple[Any, RepairActuationResult]:
        before_fp = DomainFingerprinter.fingerprint("PRESENTATION", blueprint)
        mutated = copy.deepcopy(blueprint)
        changed_elements: List[str] = []
        changed_bp_ids: List[str] = []

        target_idx = request.target_slide_or_page_index or 1

        if hasattr(mutated, "beats") and mutated.beats:
            beats = list(mutated.beats)
            idx = max(0, min(target_idx - 1, len(beats) - 1))
            beat = beats[idx]

            # Apply component reflow on target beat
            # If selection_rationale is a string, we adjust beat fields
            new_title = beat.title
            new_load = max(0.2, round(beat.cognitive_load_target * 0.85, 2))
            
            # Switch visual priority to non-colliding layout if formula collision
            new_vp = beat.visual_priority
            if beat.visual_priority in ("EQUATION_FOCUS", "COMPARISON_GRID", "HIGH_DIAGRAM"):
                # Demote dense equation breakdown into concept card with vertical stack
                new_vp = "CONCEPT_TEXT"

            # Create updated beat
            from app.intelligence.transformation.blueprints import ConceptualBeat
            updated_beat = ConceptualBeat(
                beat_id=f"{beat.beat_id}_reflow",
                sequence_index=beat.sequence_index,
                title=new_title,
                primary_concept_unit_id=beat.primary_concept_unit_id,
                supporting_unit_ids=beat.supporting_unit_ids,
                narrative_function=beat.narrative_function,
                information_gain=beat.information_gain,
                cognitive_load_target=new_load,
                visual_priority=new_vp,
                selection_rationale=f"{beat.selection_rationale} [reflowed: single_column_stack]",
                knowledge_unit_ids=beat.knowledge_unit_ids,
            )
            beats[idx] = updated_beat
            mutated = mutated.model_copy(update={"beats": tuple(beats)})
            changed_elements.append(updated_beat.beat_id)
            changed_bp_ids.append(getattr(mutated, "blueprint_id", "bp_pres"))

        elif hasattr(mutated, "slides") and mutated.slides:
            slides = list(mutated.slides)
            idx = max(0, min(target_idx - 1, len(slides) - 1))
            slide = slides[idx]

            # Reflow layout to concept_card or vertical flow
            cur_layout = getattr(slide, "layout", "concept_card")
            if cur_layout in ("formula_explainer", "three_column_comparison", "triangle_relationship"):
                slide.layout = "concept_card"
            slide.visual_intent = "single_column_reflow"
            changed_elements.append(getattr(slide, "slide_id", f"slide_{target_idx}"))
            changed_bp_ids.append("deck")

        after_fp = DomainFingerprinter.fingerprint("PRESENTATION", mutated)

        result = RepairActuationResult(
            actuator_id=self.actuator_id,
            execution_status=RepairExecutionStatus.APPLIED,
            transformation_applied="Component reflow: converted colliding grid to vertical flow, reduced cognitive load target.",
            changed_artifact_layers=(TransformationLayer.LAYER_1_COMPONENT,),
            before_fingerprint=before_fp,
            after_fingerprint=after_fp,
            changed_element_ids=tuple(changed_elements),
            changed_blueprint_ids=tuple(changed_bp_ids),
            changed_knowledge_refs=(),
            causal_reach_achieved=CausalReach.COMPONENT_SPATIAL_STRUCTURE,
            mutation_cost=0.35,
            rollback_capability=True,
            provenance={
                "target_index": target_idx,
                "reflow_strategy": "single_column_stack",
            },
            rationale=f"Reflowed slide/beat {target_idx} components into single-column vertical stack to eliminate geometry collision.",
        )

        return mutated, result
