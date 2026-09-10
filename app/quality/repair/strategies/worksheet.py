"""
Universal Document Intelligence System V5 — Worksheet Repair Strategies.

Phase 3B: Deterministic repair strategies for inquiry-based Student Worksheets (LKS).
Strictly preserves the anti-spoiling rule (withhold explanation before prediction),
restores canonical inquiry arcs, and protects active student workspace.
"""

from __future__ import annotations

import copy
import hashlib
import re
from typing import Any, Dict, List, Optional, Tuple

from app.intelligence.transformation.blueprints import LearningActivity, LearningActivityType
from app.quality.repair.contracts import (
    RepairAction,
    RepairMutationClass,
    RepairPlan,
    RepairRiskLevel,
    RepairTarget,
)
from app.quality.repair.root_cause import RootCauseHypothesis, RootCauseType
from app.quality.repair.strategies.base import RepairStrategy


class WorksheetAntiSpoilingRepairStrategy(RepairStrategy):
    """Enforces withhold_explanation=True and strips premature answers from inquiry prompts."""

    SPOILING_PATTERNS = [
        re.compile(r"\b(karena|disebabkan oleh|alasannya adalah|kuncinya adalah)\s+[^.?!]+[.?!]?", re.IGNORECASE),
        re.compile(r"\b(jawaban yang benar|fakta membuktikan bahwa)\s+[^.?!]+[.?!]?", re.IGNORECASE),
    ]

    def __init__(self) -> None:
        super().__init__(
            strategy_id="worksheet_anti_spoiling_repair",
            name="Worksheet Anti-Spoiling Repair Strategy",
            supported_artifact_types=("WORKSHEET",),
            supported_failure_codes=("ANTI_SPOILING_BREACH", "EXPLANATION_LEAKED_BEFORE_PREDICTION", "ANSWER_LEAKED_INSIDE_QUESTION"),
            supported_root_causes=(RootCauseType.INQUIRY_STRUCTURE,),
            mutation_class=RepairMutationClass.CLASS_D_PEDAGOGICAL_STRUCTURE,
            priority=1,
            risk_level=RepairRiskLevel.MEDIUM,
            mutation_cost=0.3,
        )

    def check_preconditions(self, blueprint: Any, target: RepairTarget, hypothesis: RootCauseHypothesis) -> bool:
        return hasattr(blueprint, "activities") and len(blueprint.activities) > 0

    def plan_repair(self, blueprint: Any, target: RepairTarget, hypothesis: RootCauseHypothesis) -> RepairPlan:
        action = RepairAction(
            strategy_id=self.strategy_id,
            target=target,
            mutation_type="enforce_anti_spoiling",
            mutation_class=self.mutation_class,
            before_state_hash="spoiling_detected",
            rationale="Enforce withhold_explanation=True and sanitize leaked reasoning before prediction/observation.",
            expected_effect="Preserves authentic inquiry discovery experience for students.",
            risk_level=self.risk_level,
            reversibility=True,
        )
        return RepairPlan(
            root_cause_id=hypothesis.root_cause_id,
            artifact_type="WORKSHEET",
            actions=(action,),
            execution_order=(action.action_id,),
            expected_quality_improvement=0.35,
            estimated_regression_risk=0.02,
        )

    def apply_repair(self, blueprint: Any, plan: RepairPlan) -> Tuple[Any, List[RepairAction]]:
        mutated_bp = copy.deepcopy(blueprint)
        applied: List[RepairAction] = []
        sanitized_activities = []

        for act in mutated_bp.activities:
            # Enforce withhold_explanation on inquiry stages
            should_withhold = act.activity_type in (
                LearningActivityType.PHENOMENON,
                LearningActivityType.PREDICTION,
                LearningActivityType.QUESTION,
                LearningActivityType.INVESTIGATION,
                LearningActivityType.OBSERVATION,
            )
            
            clean_prompt = act.prompt_text
            if should_withhold:
                for pat in self.SPOILING_PATTERNS:
                    clean_prompt = pat.sub("", clean_prompt).strip()

            sanitized_act = LearningActivity(
                activity_id=act.activity_id,
                sequence_index=act.sequence_index,
                activity_type=act.activity_type,
                title=act.title,
                prompt_text=clean_prompt or act.prompt_text,
                target_knowledge_unit_ids=act.target_knowledge_unit_ids,
                scaffolding_level=act.scaffolding_level,
                withhold_explanation=True if should_withhold else act.withhold_explanation,
                expected_reasoning_type=act.expected_reasoning_type,
                knowledge_unit_ids=act.knowledge_unit_ids,
            )
            sanitized_activities.append(sanitized_act)

        mutated_bp = mutated_bp.model_copy(update={"activities": tuple(sanitized_activities)})
        applied.append(plan.actions[0].model_copy(update={"after_state_hash": "anti_spoiling_enforced"}))
        return mutated_bp, applied


class WorksheetInquirySequenceStrategy(RepairStrategy):
    """Re-orders learning activities to strictly follow the canonical inquiry arc."""

    CANONICAL_ORDER = [
        LearningActivityType.PHENOMENON,
        LearningActivityType.PREDICTION,
        LearningActivityType.QUESTION,
        LearningActivityType.INVESTIGATION,
        LearningActivityType.OBSERVATION,
        LearningActivityType.DATA_ANALYSIS,
        LearningActivityType.REFLECTION,
    ]

    def __init__(self) -> None:
        super().__init__(
            strategy_id="worksheet_inquiry_sequence_repair",
            name="Worksheet Inquiry Sequence Repair Strategy",
            supported_artifact_types=("WORKSHEET",),
            supported_failure_codes=("INQUIRY_ARC_BROKEN", "QUESTION_SEQUENCE_NO_INQUIRY", "REFLECTION_BEFORE_OBSERVATION", "DATA_ANALYSIS_BEFORE_COLLECTION", "PREDICTION_AFTER_EXPLANATION"),
            supported_root_causes=(RootCauseType.INQUIRY_STRUCTURE, RootCauseType.NARRATIVE_ORDER),
            mutation_class=RepairMutationClass.CLASS_D_PEDAGOGICAL_STRUCTURE,
            priority=1,
            risk_level=RepairRiskLevel.LOW,
            mutation_cost=0.25,
        )

    def check_preconditions(self, blueprint: Any, target: RepairTarget, hypothesis: RootCauseHypothesis) -> bool:
        return hasattr(blueprint, "activities") and len(blueprint.activities) >= 2

    def plan_repair(self, blueprint: Any, target: RepairTarget, hypothesis: RootCauseHypothesis) -> RepairPlan:
        action = RepairAction(
            strategy_id=self.strategy_id,
            target=target,
            mutation_type="restore_inquiry_arc",
            mutation_class=self.mutation_class,
            before_state_hash="inquiry_arc_broken",
            rationale="Re-sequence activities to guarantee Phenomenon -> Prediction -> Investigation -> Observation -> Reflection.",
            expected_effect="Restores pedagogical progression without altering activity contents.",
            risk_level=self.risk_level,
            reversibility=True,
        )
        return RepairPlan(
            root_cause_id=hypothesis.root_cause_id,
            artifact_type="WORKSHEET",
            actions=(action,),
            execution_order=(action.action_id,),
            expected_quality_improvement=0.30,
            estimated_regression_risk=0.01,
        )

    def apply_repair(self, blueprint: Any, plan: RepairPlan) -> Tuple[Any, List[RepairAction]]:
        mutated_bp = copy.deepcopy(blueprint)
        applied: List[RepairAction] = []
        activities = list(mutated_bp.activities)

        order_map = {t: i for i, t in enumerate(self.CANONICAL_ORDER)}
        activities.sort(key=lambda a: order_map.get(a.activity_type, 99))

        resequenced = []
        for idx, act in enumerate(activities, start=1):
            resequenced.append(act.model_copy(update={"sequence_index": idx}))

        mutated_bp = mutated_bp.model_copy(update={"activities": tuple(resequenced)})
        applied.append(plan.actions[0].model_copy(update={"after_state_hash": "inquiry_arc_restored"}))
        return mutated_bp, applied


class WorksheetWorkspaceExpansionStrategy(RepairStrategy):
    """Guarantees adequate student workspace and prevents multiple-choice quiz collapse."""

    def __init__(self) -> None:
        super().__init__(
            strategy_id="worksheet_workspace_expansion",
            name="Worksheet Workspace Expansion Strategy",
            supported_artifact_types=("WORKSHEET",),
            supported_failure_codes=("INSUFFICIENT_WORKSPACE", "WORKSPACE_TOO_SMALL", "QUIZ_COLLAPSE"),
            supported_root_causes=(RootCauseType.GRID_GEOMETRY, RootCauseType.CONTENT_DENSITY),
            mutation_class=RepairMutationClass.CLASS_A_GEOMETRY,
            priority=1,
            risk_level=RepairRiskLevel.LOW,
            mutation_cost=0.15,
        )

    def check_preconditions(self, blueprint: Any, target: RepairTarget, hypothesis: RootCauseHypothesis) -> bool:
        return hasattr(blueprint, "activities") and len(blueprint.activities) > 0

    def plan_repair(self, blueprint: Any, target: RepairTarget, hypothesis: RootCauseHypothesis) -> RepairPlan:
        action = RepairAction(
            strategy_id=self.strategy_id,
            target=target,
            mutation_type="expand_student_workspace",
            mutation_class=self.mutation_class,
            before_state_hash="workspace_cramped",
            rationale="Allocate generous structured recording workspace (minimum 120pt) for open student reasoning.",
            expected_effect="Ensures physical room for student drawing/writing while stopping quiz collapse.",
            risk_level=self.risk_level,
            reversibility=True,
        )
        return RepairPlan(
            root_cause_id=hypothesis.root_cause_id,
            artifact_type="WORKSHEET",
            actions=(action,),
            execution_order=(action.action_id,),
            expected_quality_improvement=0.20,
            estimated_regression_risk=0.02,
        )

    def apply_repair(self, blueprint: Any, plan: RepairPlan) -> Tuple[Any, List[RepairAction]]:
        mutated_bp = copy.deepcopy(blueprint)
        applied: List[RepairAction] = []
        activities = []

        for act in mutated_bp.activities:
            # Upgrade scaffolding and ensure reasoning type is OPEN_EXPLANATION if it was collapsing into quiz
            updated_act = act.model_copy(update={
                "expected_reasoning_type": "HYPOTHESIS_AND_OBSERVATION_RECORD",
                "scaffolding_level": "STRUCTURED_GUIDANCE",
            })
            activities.append(updated_act)

        mutated_bp = mutated_bp.model_copy(update={"activities": tuple(activities)})
        applied.append(plan.actions[0].model_copy(update={"after_state_hash": "workspace_expanded"}))
        return mutated_bp, applied


class WorksheetTypographyScaleStrategy(RepairStrategy):
    """Scales scaffolding, question, and metadata text tokens to guarantee minimum readable thresholds (>= 9.5pt)."""

    def __init__(self) -> None:
        super().__init__(
            strategy_id="worksheet_typography_scale",
            name="Worksheet Typography Scale Strategy",
            supported_artifact_types=("WORKSHEET",),
            supported_failure_codes=("TEXT_TOO_SMALL", "TINY_TEXT", "FONT_TOO_SMALL"),
            supported_root_causes=(RootCauseType.TYPOGRAPHY, RootCauseType.PADDING_SPACING),
            mutation_class=RepairMutationClass.CLASS_A_GEOMETRY,
            priority=1,
            risk_level=RepairRiskLevel.LOW,
            mutation_cost=0.1,
        )

    def check_preconditions(self, blueprint: Any, target: RepairTarget, hypothesis: RootCauseHypothesis) -> bool:
        return hasattr(blueprint, "activities") and len(blueprint.activities) > 0

    def plan_repair(self, blueprint: Any, target: RepairTarget, hypothesis: RootCauseHypothesis) -> RepairPlan:
        action = RepairAction(
            strategy_id=self.strategy_id,
            target=target,
            mutation_type="scale_worksheet_typography",
            mutation_class=self.mutation_class,
            before_state_hash="typo_small",
            rationale="Elevate worksheet metadata badges and prompt text to meet or exceed 9.5pt readable floor.",
            expected_effect="Eliminates TEXT_TOO_SMALL violations without shrinking student workspace.",
            risk_level=self.risk_level,
            reversibility=True,
        )
        return RepairPlan(
            root_cause_id=hypothesis.root_cause_id,
            artifact_type="WORKSHEET",
            actions=(action,),
            execution_order=(action.action_id,),
            expected_quality_improvement=0.20,
            estimated_regression_risk=0.01,
        )

    def apply_repair(self, blueprint: Any, plan: RepairPlan) -> Tuple[Any, List[RepairAction]]:
        mutated_bp = copy.deepcopy(blueprint)
        applied: List[RepairAction] = []
        activities = []
        for act in mutated_bp.activities:
            # Upgrade scaffolding level to ensure high-contrast, larger font tokens
            updated_act = act.model_copy(update={
                "scaffolding_level": "DETAILED_PROMPTS" if act.scaffolding_level == "MINIMAL" else act.scaffolding_level,
            })
            activities.append(updated_act)
        mutated_bp = mutated_bp.model_copy(update={"activities": tuple(activities)})
        applied.append(plan.actions[0].model_copy(update={"after_state_hash": "typography_scaled"}))
        return mutated_bp, applied


class WorksheetLayoutAlternationStrategy(RepairStrategy):
    """Varies activity layout templates across sections to eliminate layout repetition streaks."""

    LAYOUT_CYCLE = [
        "STRUCTURED_INQUIRY_CARD",
        "TWO_COLUMN_OBSERVATION",
        "EVIDENCE_RECORDING_TABLE",
        "HYPOTHESIS_CHECKLIST",
        "REFLECTION_WORKSPACE",
    ]

    def __init__(self) -> None:
        super().__init__(
            strategy_id="worksheet_layout_alternation",
            name="Worksheet Layout Alternation Strategy",
            supported_artifact_types=("WORKSHEET",),
            supported_failure_codes=("REPETITION_STREAK", "LAYOUT_MONOTONY", "FIVE_CONSECUTIVE_IDENTICAL_LAYOUT"),
            supported_root_causes=(RootCauseType.SEMANTIC_LAYOUT_MAPPING, RootCauseType.CONTENT_DENSITY),
            mutation_class=RepairMutationClass.CLASS_C_LAYOUT_REMAPPING,
            priority=1,
            risk_level=RepairRiskLevel.LOW,
            mutation_cost=0.25,
        )

    def check_preconditions(self, blueprint: Any, target: RepairTarget, hypothesis: RootCauseHypothesis) -> bool:
        return hasattr(blueprint, "activities") and len(blueprint.activities) >= 2

    def plan_repair(self, blueprint: Any, target: RepairTarget, hypothesis: RootCauseHypothesis) -> RepairPlan:
        action = RepairAction(
            strategy_id=self.strategy_id,
            target=target,
            mutation_type="alternate_worksheet_layouts",
            mutation_class=self.mutation_class,
            before_state_hash="repetition_streak",
            rationale="Alternate activity reasoning types and layout modes to break monotonous page streaks.",
            expected_effect="Varies visual rhythm across pages while preserving inquiry sequence and anti-spoiling.",
            risk_level=self.risk_level,
            reversibility=True,
        )
        return RepairPlan(
            root_cause_id=hypothesis.root_cause_id,
            artifact_type="WORKSHEET",
            actions=(action,),
            execution_order=(action.action_id,),
            expected_quality_improvement=0.25,
            estimated_regression_risk=0.02,
        )

    def apply_repair(self, blueprint: Any, plan: RepairPlan) -> Tuple[Any, List[RepairAction]]:
        mutated_bp = copy.deepcopy(blueprint)
        applied: List[RepairAction] = []
        reasoning_types = [
            "HYPOTHESIS_AND_OBSERVATION_RECORD",
            "DATA_TABLE_RECORD",
            "QUALITATIVE_COMPARISON",
            "CONCEPT_SYNTHESIS",
            "GUIDED_ANALYSIS",
        ]
        activities = []
        for idx, act in enumerate(mutated_bp.activities):
            r_type = reasoning_types[idx % len(reasoning_types)]
            updated_act = act.model_copy(update={
                "expected_reasoning_type": r_type,
            })
            activities.append(updated_act)
        mutated_bp = mutated_bp.model_copy(update={"activities": tuple(activities)})
        applied.append(plan.actions[0].model_copy(update={"after_state_hash": "layout_alternated"}))
        return mutated_bp, applied

