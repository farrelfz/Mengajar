"""
Universal Document Intelligence System V5 — Presentation Slide Split Actuator.

Phase 4: Causal transformation operator splitting overloaded conceptual beats
or slides into coherent, sequential units to eliminate density overload.
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

logger = logging.getLogger("quality.repair.actuation.presentation.split")


class PresentationSlideSplitActuator:
    """Actuator that physically splits overloaded presentation slides/beats."""

    @property
    def actuator_id(self) -> str:
        return "presentation_slide_split_actuator"

    @property
    def supported_artifact_types(self) -> Tuple[str, ...]:
        return ("PRESENTATION",)

    @property
    def supported_root_causes(self) -> Tuple[RootCauseType, ...]:
        return (
            RootCauseType.CONTENT_DENSITY,
            RootCauseType.SPATIAL_COLLISION,
            RootCauseType.GRID_GEOMETRY,
        )

    @property
    def maximum_causal_reach(self) -> CausalReach:
        return CausalReach.PAGE_COMPOSITION

    @property
    def transformation_layer(self) -> TransformationLayer:
        return TransformationLayer.LAYER_3_BLUEPRINT_RECOMPOSITION

    def can_actuate(self, request: RepairActuationRequest, blueprint: Any) -> bool:
        if request.artifact_type.strip().upper() != "PRESENTATION":
            return False
        if hasattr(blueprint, "beats") and blueprint.beats:
            target_idx = request.target_slide_or_page_index or 1
            return 1 <= target_idx <= len(blueprint.beats)
        if hasattr(blueprint, "slides") and blueprint.slides:
            target_idx = request.target_slide_or_page_index or 1
            return 1 <= target_idx <= len(blueprint.slides)
        return False

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
            orig_beat = beats[idx]

            supp = list(orig_beat.supporting_unit_ids)
            s_mid = max(1, len(supp) // 2)

            beat_a = ConceptualBeat(
                beat_id=f"{orig_beat.beat_id}_part1",
                sequence_index=orig_beat.sequence_index,
                title=f"{orig_beat.title} (Bagian 1)",
                primary_concept_unit_id=orig_beat.primary_concept_unit_id,
                supporting_unit_ids=tuple(supp[:s_mid]),
                narrative_function=orig_beat.narrative_function,
                information_gain=round(orig_beat.information_gain * 0.6, 2),
                cognitive_load_target=round(orig_beat.cognitive_load_target * 0.5, 2),
                visual_priority=orig_beat.visual_priority,
                selection_rationale=f"{orig_beat.selection_rationale} [split_part_1]",
                knowledge_unit_ids=orig_beat.knowledge_unit_ids[:s_mid + 1],
            )
            beat_b = ConceptualBeat(
                beat_id=f"{orig_beat.beat_id}_part2",
                sequence_index=orig_beat.sequence_index + 1,
                title=f"{orig_beat.title} (Bagian 2)",
                primary_concept_unit_id=orig_beat.primary_concept_unit_id,
                supporting_unit_ids=tuple(supp[s_mid:]),
                narrative_function=orig_beat.narrative_function,
                information_gain=round(orig_beat.information_gain * 0.5, 2),
                cognitive_load_target=round(orig_beat.cognitive_load_target * 0.5, 2),
                visual_priority="CONCEPT_TEXT",
                selection_rationale=f"{orig_beat.selection_rationale} [split_part_2]",
                knowledge_unit_ids=orig_beat.knowledge_unit_ids[s_mid + 1:],
            )

            new_beats = beats[:idx] + [beat_a, beat_b] + beats[idx + 1:]
            for s_idx, b in enumerate(new_beats, start=1):
                object.__setattr__(b, "sequence_index", s_idx)

            mutated = mutated.model_copy(update={"beats": tuple(new_beats)})
            changed_elements.extend([beat_a.beat_id, beat_b.beat_id])
            changed_bp_ids.append(getattr(mutated, "blueprint_id", "bp_pres"))

        elif hasattr(mutated, "slides") and mutated.slides:
            slides = list(mutated.slides)
            idx = max(0, min(target_idx - 1, len(slides) - 1))
            orig_slide = slides[idx]

            s_a = copy.deepcopy(orig_slide)
            s_b = copy.deepcopy(orig_slide)
            s_a.title = f"{orig_slide.title} (Bagian 1)"
            s_b.title = f"{orig_slide.title} (Bagian 2)"

            blocks = list(getattr(orig_slide, "key_blocks", []))
            mid = max(1, len(blocks) // 2)
            s_a.key_blocks = blocks[:mid]
            s_b.key_blocks = blocks[mid:]

            new_slides = slides[:idx] + [s_a, s_b] + slides[idx + 1:]
            for s_num, s in enumerate(new_slides, start=1):
                s.slide_number = s_num
            mutated.slides = new_slides
            changed_elements.extend([getattr(s_a, "slide_id", "sa"), getattr(s_b, "slide_id", "sb")])
            changed_bp_ids.append("deck")

        after_fp = DomainFingerprinter.fingerprint("PRESENTATION", mutated)

        result = RepairActuationResult(
            actuator_id=self.actuator_id,
            execution_status=RepairExecutionStatus.APPLIED,
            transformation_applied="Slide split: partitioned overloaded beat into two coherent parts.",
            changed_artifact_layers=(
                TransformationLayer.LAYER_2_PAGE_COMPOSITION,
                TransformationLayer.LAYER_3_BLUEPRINT_RECOMPOSITION,
            ),
            before_fingerprint=before_fp,
            after_fingerprint=after_fp,
            changed_element_ids=tuple(changed_elements),
            changed_blueprint_ids=tuple(changed_bp_ids),
            changed_knowledge_refs=(),
            causal_reach_achieved=CausalReach.PAGE_COMPOSITION,
            mutation_cost=0.50,
            rollback_capability=True,
            provenance={"target_index": target_idx, "split_operation": "binary_partition"},
            rationale=f"Split overloaded slide/beat {target_idx} to reduce cognitive density and resolve collision.",
        )

        return mutated, result
