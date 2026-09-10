"""
Universal Document Intelligence System V5 — Presentation Structural Diversity Guard.

Phase 4: Guard and transformation operator preventing and resolving visual monotony
streaks across presentation slides by introducing rhythmic visual alternation.
"""

from __future__ import annotations

import copy
import logging
from typing import Any, Dict, List, Optional, Sequence, Tuple

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

logger = logging.getLogger("quality.repair.actuation.presentation.diversity")


class PresentationStructuralDiversityGuard:
    """Detects and repairs monotonous sequences of identical presentation layouts."""

    ALTERNATING_VP_SEQUENCE = (
        "CONCEPT_TEXT",
        "COMPARISON_GRID",
        "HIGH_DIAGRAM",
        "CONCEPT_TEXT",
        "EQUATION_FOCUS",
    )

    @classmethod
    def detect_monotony_streaks(
        cls,
        blueprint: Any,
        max_allowed_identical: int = 3,
    ) -> List[Tuple[int, int, str]]:
        """Returns list of (start_idx, end_idx, pattern_type) for streaks exceeding threshold."""
        patterns: List[str] = []
        if hasattr(blueprint, "beats") and blueprint.beats:
            patterns = [b.visual_priority for b in blueprint.beats]
        elif hasattr(blueprint, "slides") and blueprint.slides:
            patterns = [getattr(s, "layout", "concept_card") for s in blueprint.slides]

        if len(patterns) <= max_allowed_identical:
            return []

        streaks: List[Tuple[int, int, str]] = []
        cur_pattern = patterns[0]
        cur_start = 1
        cur_len = 1

        for i in range(1, len(patterns)):
            if patterns[i] == cur_pattern:
                cur_len += 1
            else:
                if cur_len > max_allowed_identical:
                    streaks.append((cur_start, cur_start + cur_len - 1, cur_pattern))
                cur_pattern = patterns[i]
                cur_start = i + 1
                cur_len = 1

        if cur_len > max_allowed_identical:
            streaks.append((cur_start, cur_start + cur_len - 1, cur_pattern))

        return streaks


class PresentationDiversityActuator:
    """Actuator breaking layout monotony by applying rhythmic diversity to slide sequences."""

    @property
    def actuator_id(self) -> str:
        return "presentation_diversity_actuator"

    @property
    def supported_artifact_types(self) -> Tuple[str, ...]:
        return ("PRESENTATION",)

    @property
    def supported_root_causes(self) -> Tuple[RootCauseType, ...]:
        return (
            RootCauseType.LAYOUT_MONOTONY,
            RootCauseType.SEMANTIC_LAYOUT_MAPPING,
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
        streaks = PresentationStructuralDiversityGuard.detect_monotony_streaks(blueprint, max_allowed_identical=2)
        return len(streaks) > 0 or hasattr(blueprint, "beats") or hasattr(blueprint, "slides")

    def actuate(
        self,
        request: RepairActuationRequest,
        blueprint: Any,
    ) -> Tuple[Any, RepairActuationResult]:
        before_fp = DomainFingerprinter.fingerprint("PRESENTATION", blueprint)
        mutated = copy.deepcopy(blueprint)
        changed_elements: List[str] = []
        changed_bp_ids: List[str] = []

        if hasattr(mutated, "beats") and mutated.beats:
            beats = list(mutated.beats)
            vp_seq = PresentationStructuralDiversityGuard.ALTERNATING_VP_SEQUENCE
            for idx, beat in enumerate(beats):
                # Apply alternation to break monotony
                chosen_vp = vp_seq[idx % len(vp_seq)]
                if chosen_vp != beat.visual_priority:
                    upd = ConceptualBeat(
                        beat_id=f"{beat.beat_id}_div",
                        sequence_index=beat.sequence_index,
                        title=beat.title,
                        primary_concept_unit_id=beat.primary_concept_unit_id,
                        supporting_unit_ids=beat.supporting_unit_ids,
                        narrative_function=beat.narrative_function,
                        information_gain=beat.information_gain,
                        cognitive_load_target=beat.cognitive_load_target,
                        visual_priority=chosen_vp,
                        selection_rationale=f"{beat.selection_rationale} [diversity_rhythm]",
                        knowledge_unit_ids=beat.knowledge_unit_ids,
                    )
                    beats[idx] = upd
                    changed_elements.append(upd.beat_id)
            mutated = mutated.model_copy(update={"beats": tuple(beats)})
            changed_bp_ids.append(getattr(mutated, "blueprint_id", "bp_pres"))

        elif hasattr(mutated, "slides") and mutated.slides:
            slides = list(mutated.slides)
            layouts = ("concept_card", "three_column_comparison", "timeline_horizontal", "concept_card")
            for idx, slide in enumerate(slides):
                slide.layout = layouts[idx % len(layouts)]
                changed_elements.append(getattr(slide, "slide_id", f"s_{idx}"))
            changed_bp_ids.append("deck")

        after_fp = DomainFingerprinter.fingerprint("PRESENTATION", mutated)

        result = RepairActuationResult(
            actuator_id=self.actuator_id,
            execution_status=RepairExecutionStatus.APPLIED,
            transformation_applied="Structural diversity: injected rhythmic layout alternation to eliminate monotony.",
            changed_artifact_layers=(TransformationLayer.LAYER_2_PAGE_COMPOSITION,),
            before_fingerprint=before_fp,
            after_fingerprint=after_fp,
            changed_element_ids=tuple(changed_elements),
            changed_blueprint_ids=tuple(changed_bp_ids),
            changed_knowledge_refs=(),
            causal_reach_achieved=CausalReach.PAGE_COMPOSITION,
            mutation_cost=0.30,
            rollback_capability=True,
            provenance={"diversity_injection": True},
            rationale="Injected structural rhythm across slide sequence to eradicate visual monotony.",
        )

        return mutated, result
