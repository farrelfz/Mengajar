"""
Universal Document Intelligence System V5 — Presentation Formula Recomposition Actuator.

Phase 4: Causal transformation operator decomposing overloaded formula and derivation
slides into clean, collision-free progressive conceptual beats.
"""

from __future__ import annotations

import copy
import hashlib
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

logger = logging.getLogger("quality.repair.actuation.presentation.formula")


class PresentationFormulaRecompositionActuator:
    """Actuator that recomposes dense formula slides into progressive beats."""

    @property
    def actuator_id(self) -> str:
        return "presentation_formula_recomposition"

    @property
    def supported_artifact_types(self) -> Tuple[str, ...]:
        return ("PRESENTATION",)

    @property
    def supported_root_causes(self) -> Tuple[RootCauseType, ...]:
        return (
            RootCauseType.GRID_GEOMETRY,
            RootCauseType.CONTENT_DENSITY,
            RootCauseType.SPATIAL_COLLISION,
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
        if hasattr(blueprint, "beats") and blueprint.beats:
            target_idx = request.target_slide_or_page_index or 1
            idx = max(0, min(target_idx - 1, len(blueprint.beats) - 1))
            beat = blueprint.beats[idx]
            return beat.visual_priority == "EQUATION_FOCUS" or "formula" in beat.title.lower() or "persamaan" in beat.title.lower() or len(beat.supporting_unit_ids) >= 1
        if hasattr(blueprint, "slides") and blueprint.slides:
            return True
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

            # Decompose into 2 progressive beats:
            # Beat 1: Core Formula Statement & Physical Principle
            # Beat 2: Parameter Breakdown & Physical Application
            supp = list(orig_beat.supporting_unit_ids)
            half = max(1, len(supp) // 2)

            beat_core = ConceptualBeat(
                beat_id=f"{orig_beat.beat_id}_core",
                sequence_index=orig_beat.sequence_index,
                title=f"{orig_beat.title} — Prinsip Utama",
                primary_concept_unit_id=orig_beat.primary_concept_unit_id,
                supporting_unit_ids=tuple(supp[:half]),
                narrative_function=orig_beat.narrative_function,
                information_gain=round(orig_beat.information_gain * 0.6, 2),
                cognitive_load_target=round(orig_beat.cognitive_load_target * 0.5, 2),
                visual_priority="EQUATION_FOCUS",
                selection_rationale=f"{orig_beat.selection_rationale} [core equation]",
                knowledge_unit_ids=orig_beat.knowledge_unit_ids[:half + 1],
            )

            beat_breakdown = ConceptualBeat(
                beat_id=f"{orig_beat.beat_id}_params",
                sequence_index=orig_beat.sequence_index + 1,
                title=f"{orig_beat.title} — Analisis Variabel",
                primary_concept_unit_id=orig_beat.primary_concept_unit_id,
                supporting_unit_ids=tuple(supp[half:]),
                narrative_function=orig_beat.narrative_function,
                information_gain=round(orig_beat.information_gain * 0.5, 2),
                cognitive_load_target=round(orig_beat.cognitive_load_target * 0.5, 2),
                visual_priority="CONCEPT_TEXT",
                selection_rationale=f"{orig_beat.selection_rationale} [parameter breakdown]",
                knowledge_unit_ids=orig_beat.knowledge_unit_ids[half + 1:],
            )

            new_beats = beats[:idx] + [beat_core, beat_breakdown] + beats[idx + 1:]
            for s_idx, b in enumerate(new_beats, start=1):
                # Update sequence indices
                object.__setattr__(b, "sequence_index", s_idx)

            mutated = mutated.model_copy(update={"beats": tuple(new_beats)})
            changed_elements.extend([beat_core.beat_id, beat_breakdown.beat_id])
            changed_bp_ids.append(getattr(mutated, "blueprint_id", "bp_pres"))

        elif hasattr(mutated, "slides") and mutated.slides:
            slides = list(mutated.slides)
            idx = max(0, min(target_idx - 1, len(slides) - 1))
            orig_slide = slides[idx]

            s1 = copy.deepcopy(orig_slide)
            s2 = copy.deepcopy(orig_slide)
            s1.title = f"{orig_slide.title} (Persamaan Inti)"
            s2.title = f"{orig_slide.title} (Analisis Variabel)"
            s1.layout = "formula_explainer"
            s2.layout = "concept_card"

            new_slides = slides[:idx] + [s1, s2] + slides[idx + 1:]
            for s_num, s in enumerate(new_slides, start=1):
                s.slide_number = s_num
            mutated.slides = new_slides
            changed_elements.extend([getattr(s1, "slide_id", "s1"), getattr(s2, "slide_id", "s2")])
            changed_bp_ids.append("deck")

        after_fp = DomainFingerprinter.fingerprint("PRESENTATION", mutated)

        result = RepairActuationResult(
            actuator_id=self.actuator_id,
            execution_status=RepairExecutionStatus.APPLIED,
            transformation_applied="Formula recomposition: decomposed equation and variable breakdown into progressive beats.",
            changed_artifact_layers=(
                TransformationLayer.LAYER_1_COMPONENT,
                TransformationLayer.LAYER_2_PAGE_COMPOSITION,
            ),
            before_fingerprint=before_fp,
            after_fingerprint=after_fp,
            changed_element_ids=tuple(changed_elements),
            changed_blueprint_ids=tuple(changed_bp_ids),
            changed_knowledge_refs=(),
            causal_reach_achieved=CausalReach.PAGE_COMPOSITION,
            mutation_cost=0.45,
            rollback_capability=True,
            provenance={"target_index": target_idx, "recomposition": "progressive_equation_split"},
            rationale=f"Recomposed formula slide {target_idx} into progressive equation and variable breakdown beats to eliminate collision.",
        )

        return mutated, result
