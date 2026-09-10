"""
Universal Document Intelligence System V5 — Blueprint Recomposition Engine & Semantic Grouping Optimizer.

Phase 4: Multi-layer structural recomposition engine and semantic grouping optimizer
governing causal artifact transformations across Layers 0 through 4.
"""

from __future__ import annotations

import copy
import logging
from typing import Any, Dict, List, Optional, Sequence, Tuple

from app.quality.repair.actuation.contracts import (
    RepairActuationRequest,
    RepairActuationResult,
    RepairActuator,
)
from app.quality.repair.actuation.mutation_layers import TransformationLayer
from app.quality.repair.actuation.registry import RepairActuatorRegistry
from app.quality.repair.effectiveness.causal_reach import CausalReach
from app.quality.repair.effectiveness.contracts import RepairExecutionStatus
from app.quality.repair.effectiveness.zero_effect_detector import DomainFingerprinter
from app.quality.repair.root_cause import RootCauseType

logger = logging.getLogger("quality.repair.actuation.blueprint_recomposition")


class SemanticGroupingOptimizer:
    """Optimizes semantic unit allocations and cognitive load distribution across pages/slides."""

    @classmethod
    def optimize_presentation_beats(
        cls,
        beats: Sequence[Any],
        max_cognitive_load: float = 1.0,
    ) -> List[Any]:
        """Reclusters presentation beats so no individual beat exceeds max_cognitive_load."""
        optimized: List[Any] = []
        for b in beats:
            cog = getattr(b, "cognitive_load_target", 0.5)
            supp = getattr(b, "supporting_unit_ids", ())
            if cog > max_cognitive_load and len(supp) >= 2:
                # Partition overloaded beat
                mid = len(supp) // 2
                from app.intelligence.transformation.blueprints import ConceptualBeat
                b1 = ConceptualBeat(
                    beat_id=f"{b.beat_id}_opt1",
                    sequence_index=b.sequence_index,
                    title=f"{b.title} (Part 1)",
                    primary_concept_unit_id=b.primary_concept_unit_id,
                    supporting_unit_ids=tuple(supp[:mid]),
                    narrative_function=b.narrative_function,
                    information_gain=round(b.information_gain * 0.6, 2),
                    cognitive_load_target=round(cog * 0.5, 2),
                    visual_priority=b.visual_priority,
                    selection_rationale=f"{b.selection_rationale} [load_optimized_1]",
                    knowledge_unit_ids=b.knowledge_unit_ids[:mid + 1],
                )
                b2 = ConceptualBeat(
                    beat_id=f"{b.beat_id}_opt2",
                    sequence_index=b.sequence_index + 1,
                    title=f"{b.title} (Part 2)",
                    primary_concept_unit_id=b.primary_concept_unit_id,
                    supporting_unit_ids=tuple(supp[mid:]),
                    narrative_function=b.narrative_function,
                    information_gain=round(b.information_gain * 0.5, 2),
                    cognitive_load_target=round(cog * 0.5, 2),
                    visual_priority="CONCEPT_TEXT",
                    selection_rationale=f"{b.selection_rationale} [load_optimized_2]",
                    knowledge_unit_ids=b.knowledge_unit_ids[mid + 1:],
                )
                optimized.extend([b1, b2])
            else:
                optimized.append(b)

        # Re-sequence
        for idx, item in enumerate(optimized, start=1):
            if hasattr(item, "sequence_index"):
                object.__setattr__(item, "sequence_index", idx)

        return optimized


class BlueprintRecompositionEngine:
    """Master recomposition engine selecting causal layer and executing real artifact mutations."""

    def __init__(self, registry: Optional[RepairActuatorRegistry] = None) -> None:
        self.registry = registry or RepairActuatorRegistry.get_default()

    def recompose(
        self,
        request: RepairActuationRequest,
        blueprint: Any,
    ) -> Tuple[Any, RepairActuationResult]:
        """Executes targeted structural recomposition using the optimal capable actuator."""
        actuator = self.registry.get_actuator_for_strategy(
            request.repair_strategy_id,
            artifact_type=request.artifact_type,
        )

        if actuator is None or not actuator.can_actuate(request, blueprint):
            # Fallback: attempt direct semantic grouping optimization
            if request.artifact_type.strip().upper() == "PRESENTATION" and hasattr(blueprint, "beats"):
                before_fp = DomainFingerprinter.fingerprint("PRESENTATION", blueprint)
                opt_beats = SemanticGroupingOptimizer.optimize_presentation_beats(blueprint.beats)
                mutated = blueprint.model_copy(update={"beats": tuple(opt_beats)})
                after_fp = DomainFingerprinter.fingerprint("PRESENTATION", mutated)
                res = RepairActuationResult(
                    actuator_id="semantic_grouping_optimizer",
                    execution_status=RepairExecutionStatus.APPLIED,
                    transformation_applied="Semantic grouping: repartitioned overloaded cognitive load units.",
                    changed_artifact_layers=(TransformationLayer.LAYER_3_BLUEPRINT_RECOMPOSITION,),
                    before_fingerprint=before_fp,
                    after_fingerprint=after_fp,
                    changed_element_ids=tuple(b.beat_id for b in opt_beats),
                    changed_blueprint_ids=(getattr(blueprint, "blueprint_id", "bp"),),
                    changed_knowledge_refs=(),
                    causal_reach_achieved=CausalReach.PAGE_COMPOSITION,
                    mutation_cost=0.50,
                    rollback_capability=True,
                    provenance={"semantic_optimizer": True},
                    rationale="Direct semantic grouping optimization applied.",
                )
                return mutated, res

            # Could not actuate
            before_fp = DomainFingerprinter.fingerprint(request.artifact_type, blueprint)
            res = RepairActuationResult(
                actuator_id="none",
                execution_status=RepairExecutionStatus.NO_EFFECT,
                transformation_applied="No capable actuator found for request.",
                changed_artifact_layers=(),
                before_fingerprint=before_fp,
                after_fingerprint=before_fp,
                changed_element_ids=(),
                changed_blueprint_ids=(),
                changed_knowledge_refs=(),
                causal_reach_achieved=CausalReach.LOCAL_RENDER_GEOMETRY,
                mutation_cost=0.0,
                rollback_capability=True,
                provenance={},
                rationale="Actuator unavailable or cannot actuate for target blueprint.",
                error_message=f"No capable actuator registered for strategy '{request.repair_strategy_id}'.",
            )
            return blueprint, res

        return actuator.actuate(request, blueprint)
