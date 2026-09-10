"""
Universal Document Intelligence System V5 — Worksheet Inquiry Recomposition Actuator.

Phase 4: Causal transformation operator recomposing monotonous question sequences
into structured pedagogical inquiry arcs (PHENOMENON -> PREDICTION -> OBSERVATION ->
INVESTIGATION -> DATA_ANALYSIS -> REFLECTION) while strictly withholding answers.
"""

from __future__ import annotations

import copy
import logging
from typing import Any, Dict, List, Optional, Tuple

from app.intelligence.transformation.blueprints import LearningActivity, LearningActivityType
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

logger = logging.getLogger("quality.repair.actuation.worksheet.inquiry_recomposition")


class WorksheetInquiryRecompositionActuator:
    """Actuator that restructures worksheet activities into dynamic pedagogical inquiry arcs."""

    INQUIRY_ARC_TYPES = (
        LearningActivityType.PHENOMENON,
        LearningActivityType.PREDICTION,
        LearningActivityType.QUESTION,
        LearningActivityType.OBSERVATION,
        LearningActivityType.INVESTIGATION,
        LearningActivityType.DATA_ANALYSIS,
        LearningActivityType.REFLECTION,
    )

    ACTIVITY_PROMPTS = {
        LearningActivityType.PHENOMENON: (
            "Amati fenomena berikut secara saksama: '{title}'. Catat parameter fisis yang dapat Anda identifikasi.",
            "OBSERVATIONAL_DEDUCTION",
        ),
        LearningActivityType.PREDICTION: (
            "Berdasarkan fenomena tersebut, buatlah prediksi terukur: Apa yang terjadi jika variabel utama pada '{title}' diubah?",
            "HYPOTHESIS_FORMATION",
        ),
        LearningActivityType.QUESTION: (
            "Analisis hubungan kausalitas: Mengapa kondisi pada '{title}' menghasilkan fenomena yang teramati?",
            "CONCEPTUAL_EXPLANATION",
        ),
        LearningActivityType.OBSERVATION: (
            "Lengkapi tabel observasi terstruktur berikut untuk mendokumentasikan dinamika '{title}'.",
            "DATA_COLLECTION_TABLE",
        ),
        LearningActivityType.INVESTIGATION: (
            "Rancang langkah investigasi sistematis untuk menguji batas kestabilan sistem '{title}'.",
            "EXPERIMENTAL_PROTOCOL",
        ),
        LearningActivityType.DATA_ANALYSIS: (
            "Evaluasi grafik data dan parameter numerik terkait '{title}'. Buat inferensi ilmiah dari tren yang tampak.",
            "QUANTITATIVE_REASONING",
        ),
        LearningActivityType.REFLECTION: (
            "Refleksi metakognitif: Bagaimana pemahaman prinsip '{title}' menjelaskan fenomena serupa di dunia nyata?",
            "METACOGNITIVE_SYNTHESIS",
        ),
    }

    @property
    def actuator_id(self) -> str:
        return "worksheet_inquiry_recomposition"

    @property
    def supported_artifact_types(self) -> Tuple[str, ...]:
        return ("WORKSHEET",)

    @property
    def supported_root_causes(self) -> Tuple[RootCauseType, ...]:
        return (
            RootCauseType.INQUIRY_STRUCTURE,
            RootCauseType.LAYOUT_MONOTONY,
            RootCauseType.SEMANTIC_LAYOUT_MAPPING,
            RootCauseType.CONTENT_DENSITY,
        )

    @property
    def maximum_causal_reach(self) -> CausalReach:
        return CausalReach.PEDAGOGICAL_STRUCTURE

    @property
    def transformation_layer(self) -> TransformationLayer:
        return TransformationLayer.LAYER_3_BLUEPRINT_RECOMPOSITION

    def can_actuate(self, request: RepairActuationRequest, blueprint: Any) -> bool:
        if request.artifact_type.strip().upper() != "WORKSHEET":
            return False
        return hasattr(blueprint, "activities") and bool(blueprint.activities)

    def actuate(
        self,
        request: RepairActuationRequest,
        blueprint: Any,
    ) -> Tuple[Any, RepairActuationResult]:
        before_fp = DomainFingerprinter.fingerprint("WORKSHEET", blueprint)
        mutated = copy.deepcopy(blueprint)
        changed_elements: List[str] = []
        changed_bp_ids: List[str] = [getattr(mutated, "blueprint_id", "bp_ws")]

        orig_activities = list(mutated.activities)
        n = len(orig_activities)

        new_activities: List[LearningActivity] = []
        arc_cycle = self.INQUIRY_ARC_TYPES

        for idx, act in enumerate(orig_activities):
            target_type = arc_cycle[idx % len(arc_cycle)]
            template_prompt, reasoning_type = self.ACTIVITY_PROMPTS[target_type]

            # Reconstruct activity with genuine structural differentiation
            clean_title = act.title.split(":")[-1].strip()
            prompt = template_prompt.format(title=clean_title)

            # Preserve all source knowledge references strictly
            recomposed_act = LearningActivity(
                activity_id=f"act_arc_{idx + 1:02d}",
                sequence_index=idx + 1,
                activity_type=target_type,
                title=f"Tahap {idx + 1}: {target_type.value.replace('_', ' ').title()}",
                prompt_text=prompt,
                target_knowledge_unit_ids=act.target_knowledge_unit_ids,
                scaffolding_level="HIGH" if idx < 2 else ("MEDIUM" if idx < 5 else "LOW"),
                withhold_explanation=True,  # Invariant: NEVER leak answers
                expected_reasoning_type=reasoning_type,
                knowledge_unit_ids=act.knowledge_unit_ids,
            )
            new_activities.append(recomposed_act)
            changed_elements.append(recomposed_act.activity_id)

        mutated = mutated.model_copy(update={"activities": tuple(new_activities)})
        after_fp = DomainFingerprinter.fingerprint("WORKSHEET", mutated)

        result = RepairActuationResult(
            actuator_id=self.actuator_id,
            execution_status=RepairExecutionStatus.APPLIED,
            transformation_applied=(
                f"Inquiry recomposition: transformed {n} repetitive activities into a structured "
                "7-stage pedagogical arc (Phenomenon -> Prediction -> Question -> Observation -> "
                "Investigation -> Data Analysis -> Reflection) with answer withholding strictly preserved."
            ),
            changed_artifact_layers=(
                TransformationLayer.LAYER_2_PAGE_COMPOSITION,
                TransformationLayer.LAYER_3_BLUEPRINT_RECOMPOSITION,
            ),
            before_fingerprint=before_fp,
            after_fingerprint=after_fp,
            changed_element_ids=tuple(changed_elements),
            changed_blueprint_ids=tuple(changed_bp_ids),
            changed_knowledge_refs=(),
            causal_reach_achieved=CausalReach.PEDAGOGICAL_STRUCTURE,
            mutation_cost=0.55,
            rollback_capability=True,
            provenance={
                "original_count": n,
                "recomposed_count": len(new_activities),
                "inquiry_stages": [a.activity_type.value for a in new_activities],
                "withhold_explanation": True,
            },
            rationale=(
                "Recomposed monotonous questions into progressive pedagogical inquiry sequence "
                "to eliminate visual and structural repetition while maintaining zero answer leakage."
            ),
        )

        return mutated, result
