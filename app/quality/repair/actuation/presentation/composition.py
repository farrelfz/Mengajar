"""
Universal Document Intelligence System V5 — Presentation Composition Actuator.

Phase 4: Causal transformation operator re-allocating layout archetypes,
promoting dominant cards, and establishing dynamic visual hierarchy.
"""

from __future__ import annotations

import copy
import logging
from typing import Any, Dict, List, Optional, Tuple

from app.intelligence.transformation.blueprints import ConceptualBeat
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

logger = logging.getLogger("quality.repair.actuation.presentation.composition")


class PresentationCompositionActuator:
    """Actuator re-allocating presentation layout archetypes and visual priorities."""

    @property
    def actuator_id(self) -> str:
        return "presentation_composition_actuator"

    @property
    def supported_artifact_types(self) -> Tuple[str, ...]:
        return ("PRESENTATION",)

    @property
    def supported_root_causes(self) -> Tuple[RootCauseType, ...]:
        return (
            RootCauseType.SEMANTIC_LAYOUT_MAPPING,
            RootCauseType.LAYOUT_MONOTONY,
            RootCauseType.GRID_GEOMETRY,
            RootCauseType.TYPOGRAPHY,
        )

    @property
    def maximum_causal_reach(self) -> CausalReach:
        return CausalReach.PAGE_COMPOSITION

    @property
    def transformation_layer(self) -> TransformationLayer:
        return TransformationLayer.LAYER_2_PAGE_COMPOSITION

    def can_actuate(self, request: RepairActuationRequest, blueprint: Any) -> bool:
        if request.artifact_type.strip().upper() != "PRESENTATION":
            return False
        return (hasattr(blueprint, "beats") and bool(blueprint.beats)) or (
            hasattr(blueprint, "slides") and bool(blueprint.slides)
        )

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

            # Alternate visual priority to create rhythm and eliminate collision
            vp_cycle = {
                "EQUATION_FOCUS": "CONCEPT_TEXT",
                "HIGH_DIAGRAM": "COMPARISON_GRID",
                "COMPARISON_GRID": "CONCEPT_TEXT",
                "CONCEPT_TEXT": "HIGH_DIAGRAM",
            }
            new_vp = vp_cycle.get(beat.visual_priority, "CONCEPT_TEXT")

            updated_beat = ConceptualBeat(
                beat_id=f"{beat.beat_id}_comp",
                sequence_index=beat.sequence_index,
                title=beat.title,
                primary_concept_unit_id=beat.primary_concept_unit_id,
                supporting_unit_ids=beat.supporting_unit_ids,
                narrative_function=beat.narrative_function,
                information_gain=beat.information_gain,
                cognitive_load_target=beat.cognitive_load_target,
                visual_priority=new_vp,
                selection_rationale=f"{beat.selection_rationale} [composition: {new_vp}]",
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

            layout_cycle = {
                "formula_explainer": "concept_card",
                "concept_card": "three_column_comparison",
                "three_column_comparison": "timeline_horizontal",
                "timeline_horizontal": "concept_card",
            }
            slide.layout = layout_cycle.get(getattr(slide, "layout", "concept_card"), "concept_card")
            changed_elements.append(getattr(slide, "slide_id", f"slide_{target_idx}"))
            changed_bp_ids.append("deck")

        after_fp = DomainFingerprinter.fingerprint("PRESENTATION", mutated)

        result = RepairActuationResult(
            actuator_id=self.actuator_id,
            execution_status=RepairExecutionStatus.APPLIED,
            transformation_applied="Composition re-allocation: alternated layout archetype and visual priority.",
            changed_artifact_layers=(TransformationLayer.LAYER_2_PAGE_COMPOSITION,),
            before_fingerprint=before_fp,
            after_fingerprint=after_fp,
            changed_element_ids=tuple(changed_elements),
            changed_blueprint_ids=tuple(changed_bp_ids),
            changed_knowledge_refs=(),
            causal_reach_achieved=CausalReach.PAGE_COMPOSITION,
            mutation_cost=0.40,
            rollback_capability=True,
            provenance={"target_index": target_idx, "reallocation": "layout_cycle"},
            rationale=f"Re-allocated layout archetype on slide/beat {target_idx} to resolve monotony/collision.",
        )

        return mutated, result
