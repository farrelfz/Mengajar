"""
Universal Document Intelligence System V5 — Handout Repair Strategies.

Phase 3B: Deterministic repair strategies for continuous A4 educational reading material.
Preserves narrative continuity, deep reading comfort, and monotonic heading hierarchy.
"""

from __future__ import annotations

import copy
import hashlib
from typing import Any, Dict, List, Optional, Tuple

from app.quality.repair.contracts import (
    RepairAction,
    RepairMutationClass,
    RepairPlan,
    RepairRiskLevel,
    RepairTarget,
)
from app.quality.repair.root_cause import RootCauseHypothesis, RootCauseType
from app.quality.repair.strategies.base import RepairStrategy


class HandoutPaginationStrategy(RepairStrategy):
    """Eliminates accidental trailing pages by consolidating orphan sections."""

    def __init__(self) -> None:
        super().__init__(
            strategy_id="handout_pagination_consolidation",
            name="Handout Pagination Consolidation Strategy",
            supported_artifact_types=("HANDOUT",),
            supported_failure_codes=("ACCIDENTAL_PAGE", "ALMOST_EMPTY_PAGE", "ALMOST_EMPTY_ACCIDENTAL_PAGE", "ORPHAN_PAGE"),
            supported_root_causes=(RootCauseType.PAGE_BREAK, RootCauseType.GRID_GEOMETRY),
            mutation_class=RepairMutationClass.CLASS_B_COMPOSITION,
            priority=1,
            risk_level=RepairRiskLevel.LOW,
            mutation_cost=0.2,
        )

    def check_preconditions(self, blueprint: Any, target: RepairTarget, hypothesis: RootCauseHypothesis) -> bool:
        sections = getattr(blueprint, "sections", None)
        return sections is not None and len(sections) >= 2

    def plan_repair(self, blueprint: Any, target: RepairTarget, hypothesis: RootCauseHypothesis) -> RepairPlan:
        action = RepairAction(
            strategy_id=self.strategy_id,
            target=target,
            mutation_type="consolidate_trailing_section",
            mutation_class=self.mutation_class,
            before_state_hash=hashlib.sha256(str(len(blueprint.sections)).encode()).hexdigest()[:16],
            rationale="Consolidate orphan trailing content into predecessor section to eliminate accidental page.",
            expected_effect="Reduces page count by 1, eliminating underutilized trailing page.",
            risk_level=self.risk_level,
            reversibility=True,
        )
        return RepairPlan(
            root_cause_id=hypothesis.root_cause_id,
            artifact_type="HANDOUT",
            actions=(action,),
            execution_order=(action.action_id,),
            expected_quality_improvement=0.20,
            estimated_regression_risk=0.05,
        )

    def apply_repair(self, blueprint: Any, plan: RepairPlan) -> Tuple[Any, List[RepairAction]]:
        mutated_bp = copy.deepcopy(blueprint)
        applied: List[RepairAction] = []
        sections = list(mutated_bp.sections)
        if len(sections) >= 2:
            last_sec = sections[-1]
            prev_sec = sections[-2]

            # Merge last section into predecessor
            from app.intelligence.transformation.blueprints import ExplanatorySection
            merged_sec = ExplanatorySection(
                section_id=prev_sec.section_id,
                sequence_index=prev_sec.sequence_index,
                topic=prev_sec.topic,
                heading_level=prev_sec.heading_level,
                core_unit_ids=prev_sec.core_unit_ids + last_sec.core_unit_ids,
                supporting_unit_ids=prev_sec.supporting_unit_ids + last_sec.supporting_unit_ids,
                definitions=prev_sec.definitions + last_sec.definitions,
                examples=prev_sec.examples + last_sec.examples,
                relationships=prev_sec.relationships + last_sec.relationships,
                reading_depth=prev_sec.reading_depth,
                knowledge_unit_ids=prev_sec.knowledge_unit_ids + last_sec.knowledge_unit_ids,
            )
            new_sections = sections[:-2] + [merged_sec]
            mutated_bp = mutated_bp.model_copy(update={"sections": tuple(new_sections)})
            applied.append(plan.actions[0].model_copy(update={
                "after_state_hash": hashlib.sha256(str(len(new_sections)).encode()).hexdigest()[:16]
            }))

        return mutated_bp, applied


class HandoutHierarchyRepairStrategy(RepairStrategy):
    """Restores monotonic heading hierarchy (H1 -> H2 -> H3) in continuous documents."""

    def __init__(self) -> None:
        super().__init__(
            strategy_id="handout_hierarchy_repair",
            name="Handout Hierarchy Repair Strategy",
            supported_artifact_types=("HANDOUT",),
            supported_failure_codes=("STRUCTURAL_HIERARCHY_INVERSION", "HEADING_HIERARCHY_INVERSION"),
            supported_root_causes=(RootCauseType.NARRATIVE_ORDER,),
            mutation_class=RepairMutationClass.CLASS_D_PEDAGOGICAL_STRUCTURE,
            priority=1,
            risk_level=RepairRiskLevel.LOW,
            mutation_cost=0.15,
        )

    def check_preconditions(self, blueprint: Any, target: RepairTarget, hypothesis: RootCauseHypothesis) -> bool:
        return hasattr(blueprint, "sections") and len(blueprint.sections) > 0

    def plan_repair(self, blueprint: Any, target: RepairTarget, hypothesis: RootCauseHypothesis) -> RepairPlan:
        action = RepairAction(
            strategy_id=self.strategy_id,
            target=target,
            mutation_type="restore_heading_monotonicity",
            mutation_class=self.mutation_class,
            before_state_hash="hierarchy_raw",
            rationale="Normalize heading levels to prevent abrupt level jumps (e.g. H1 to H3).",
            expected_effect="Monotonic heading progression for structured accessibility.",
            risk_level=self.risk_level,
            reversibility=True,
        )
        return RepairPlan(
            root_cause_id=hypothesis.root_cause_id,
            artifact_type="HANDOUT",
            actions=(action,),
            execution_order=(action.action_id,),
            expected_quality_improvement=0.25,
            estimated_regression_risk=0.01,
        )

    def apply_repair(self, blueprint: Any, plan: RepairPlan) -> Tuple[Any, List[RepairAction]]:
        mutated_bp = copy.deepcopy(blueprint)
        applied: List[RepairAction] = []

        from app.intelligence.transformation.blueprints import ExplanatorySection
        current_level = 1
        normalized_sections = []

        for sec in mutated_bp.sections:
            target_level = sec.heading_level
            # Ensure heading depth jumps by at most 1 level
            if target_level > current_level + 1:
                target_level = current_level + 1
            current_level = target_level

            norm_sec = ExplanatorySection(
                section_id=sec.section_id,
                sequence_index=sec.sequence_index,
                topic=sec.topic,
                heading_level=target_level,
                core_unit_ids=sec.core_unit_ids,
                supporting_unit_ids=sec.supporting_unit_ids,
                definitions=sec.definitions,
                examples=sec.examples,
                relationships=sec.relationships,
                reading_depth=sec.reading_depth,
                knowledge_unit_ids=sec.knowledge_unit_ids,
            )
            normalized_sections.append(norm_sec)

        mutated_bp = mutated_bp.model_copy(update={"sections": tuple(normalized_sections)})
        applied.append(plan.actions[0].model_copy(update={"after_state_hash": "hierarchy_normalized"}))
        return mutated_bp, applied


class HandoutDensityBalanceStrategy(RepairStrategy):
    """Rebalances an overloaded explanatory section without fragmenting reading flow."""

    def __init__(self) -> None:
        super().__init__(
            strategy_id="handout_density_balance",
            name="Handout Density Balance Strategy",
            supported_artifact_types=("HANDOUT",),
            supported_failure_codes=("EXTREME_DENSE_PAGE", "COGNITIVE_OVERLOAD"),
            supported_root_causes=(RootCauseType.CONTENT_DENSITY,),
            mutation_class=RepairMutationClass.CLASS_B_COMPOSITION,
            priority=1,
            risk_level=RepairRiskLevel.MEDIUM,
            mutation_cost=0.35,
        )

    def check_preconditions(self, blueprint: Any, target: RepairTarget, hypothesis: RootCauseHypothesis) -> bool:
        sections = getattr(blueprint, "sections", None)
        return sections is not None and len(sections) > 0

    def plan_repair(self, blueprint: Any, target: RepairTarget, hypothesis: RootCauseHypothesis) -> RepairPlan:
        idx = target.page_index or 1
        action = RepairAction(
            strategy_id=self.strategy_id,
            target=target,
            mutation_type="split_dense_explanatory_section",
            mutation_class=self.mutation_class,
            before_state_hash="density_dense",
            rationale=f"Split dense explanatory section around page {idx} into topical subsections.",
            expected_effect="Relieves reading fatigue and prevents physical page overflow.",
            risk_level=self.risk_level,
            reversibility=True,
        )
        return RepairPlan(
            root_cause_id=hypothesis.root_cause_id,
            artifact_type="HANDOUT",
            actions=(action,),
            execution_order=(action.action_id,),
            expected_quality_improvement=0.30,
            estimated_regression_risk=0.05,
        )

    def apply_repair(self, blueprint: Any, plan: RepairPlan) -> Tuple[Any, List[RepairAction]]:
        mutated_bp = copy.deepcopy(blueprint)
        applied: List[RepairAction] = []
        sections = list(mutated_bp.sections)

        from app.intelligence.transformation.blueprints import ExplanatorySection
        new_sections = []
        for sec in sections:
            # If section has many units (> 4), split into part A and part B
            if len(sec.core_unit_ids) + len(sec.supporting_unit_ids) >= 4:
                c_mid = max(1, len(sec.core_unit_ids) // 2)
                s_mid = max(1, len(sec.supporting_unit_ids) // 2)

                sec_a = ExplanatorySection(
                    section_id=f"{sec.section_id}_a",
                    sequence_index=len(new_sections) + 1,
                    topic=f"{sec.topic} — Konsep Dasar",
                    heading_level=sec.heading_level,
                    core_unit_ids=sec.core_unit_ids[:c_mid],
                    supporting_unit_ids=sec.supporting_unit_ids[:s_mid],
                    definitions=sec.definitions[:max(1, len(sec.definitions)//2)],
                    examples=(),
                    relationships=sec.relationships[:max(1, len(sec.relationships)//2)],
                    reading_depth=sec.reading_depth,
                    knowledge_unit_ids=sec.knowledge_unit_ids[:c_mid + s_mid],
                )
                sec_b = ExplanatorySection(
                    section_id=f"{sec.section_id}_b",
                    sequence_index=len(new_sections) + 2,
                    topic=f"{sec.topic} — Pendalaman & Aplikasi",
                    heading_level=sec.heading_level,
                    core_unit_ids=sec.core_unit_ids[c_mid:],
                    supporting_unit_ids=sec.supporting_unit_ids[s_mid:],
                    definitions=sec.definitions[max(1, len(sec.definitions)//2):],
                    examples=sec.examples,
                    relationships=sec.relationships[max(1, len(sec.relationships)//2):],
                    reading_depth=sec.reading_depth,
                    knowledge_unit_ids=sec.knowledge_unit_ids[c_mid + s_mid:],
                )
                new_sections.extend([sec_a, sec_b])
            else:
                new_sections.append(sec)

        # Re-sequence
        resequenced = []
        for idx, s in enumerate(new_sections, start=1):
            resequenced.append(s.model_copy(update={"sequence_index": idx}))

        mutated_bp = mutated_bp.model_copy(update={"sections": tuple(resequenced)})
        applied.append(plan.actions[0].model_copy(update={"after_state_hash": "density_balanced"}))
        return mutated_bp, applied
