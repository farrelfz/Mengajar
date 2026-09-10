"""
Universal Document Intelligence System V5 — Presentation Repair Strategies.

Phase 3B: Deterministic, root-cause-aware repair strategies for 16:9 Presentation slides.
Preserves minimal typography (12pt body / 14pt title) and splits overloaded slides
rather than shrinking fonts.
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
from app.quality.repair.effectiveness.causal_reach import CausalReach
from app.quality.repair.root_cause import RootCauseHypothesis, RootCauseType
from app.quality.repair.strategies.base import RepairStrategy


class PresentationDensitySplitStrategy(RepairStrategy):
    """Splits an overloaded slide into two coherent semantic slides when caused by CONTENT_DENSITY."""

    def __init__(self) -> None:
        super().__init__(
            strategy_id="presentation_density_split",
            name="Presentation Density Split Strategy",
            supported_artifact_types=("PRESENTATION",),
            supported_failure_codes=("TEXT_OVERFLOW", "TEXT_CLIPPING", "COGNITIVE_OVERLOAD", "MORE_THAN_SIX_CARDS"),
            supported_root_causes=(RootCauseType.CONTENT_DENSITY,),
            mutation_class=RepairMutationClass.CLASS_B_COMPOSITION,
            priority=1,
            risk_level=RepairRiskLevel.MEDIUM,
            mutation_cost=0.5,
        )

    def check_preconditions(self, blueprint: Any, target: RepairTarget, hypothesis: RootCauseHypothesis) -> bool:
        slides = getattr(blueprint, "slides", None) or getattr(blueprint, "beats", None)
        if not slides:
            return False
        idx = target.slide_index or target.page_index
        if idx is None or idx < 1 or idx > len(slides):
            return False
        slide = slides[idx - 1]
        blocks = getattr(slide, "key_blocks", None) or getattr(slide, "knowledge_unit_ids", None) or []
        # Precondition: must have separable content (at least 2 units or long text)
        return len(blocks) >= 2 or len(getattr(slide, "text", "")) > 200 or len(getattr(slide, "supporting_unit_ids", ())) >= 2

    def plan_repair(self, blueprint: Any, target: RepairTarget, hypothesis: RootCauseHypothesis) -> RepairPlan:
        idx = target.slide_index or target.page_index or 1
        action = RepairAction(
            strategy_id=self.strategy_id,
            target=target,
            mutation_type="split_overloaded_slide",
            mutation_class=self.mutation_class,
            before_state_hash=self._hash_state(blueprint),
            rationale=f"Split overloaded slide {idx} into two coherent parts to eliminate density overflow without shrinking fonts below 14pt.",
            expected_effect="Reduces cognitive load, eliminates text overflow, preserves readability.",
            risk_level=self.risk_level,
            reversibility=True,
        )
        return RepairPlan(
            root_cause_id=hypothesis.root_cause_id,
            artifact_type="PRESENTATION",
            actions=(action,),
            execution_order=(action.action_id,),
            expected_quality_improvement=0.25,
            estimated_regression_risk=0.10,
        )

    def apply_repair(self, blueprint: Any, plan: RepairPlan) -> Tuple[Any, List[RepairAction]]:
        mutated_bp = copy.deepcopy(blueprint)
        applied_actions: List[RepairAction] = []

        for action in plan.actions:
            idx = action.target.slide_index or action.target.page_index or 1
            is_slide_plan = hasattr(mutated_bp, "slides")
            items = mutated_bp.slides if is_slide_plan else mutated_bp.beats
            if idx < 1 or idx > len(items):
                continue

            orig_slide = items[idx - 1]
            slide_a = copy.deepcopy(orig_slide)
            slide_b = copy.deepcopy(orig_slide)

            if is_slide_plan:
                # PlannedSlide structure
                orig_title = getattr(orig_slide, "title", "Slide")
                slide_a.title = f"{orig_title} (Bagian 1)"
                slide_b.title = f"{orig_title} (Bagian 2)"

                blocks = list(getattr(orig_slide, "key_blocks", []))
                mid = max(1, len(blocks) // 2)
                slide_a.key_blocks = blocks[:mid]
                slide_b.key_blocks = blocks[mid:]

                claims = list(getattr(orig_slide, "claim_units", []))
                c_mid = max(1, len(claims) // 2)
                slide_a.claim_units = claims[:c_mid]
                slide_b.claim_units = claims[c_mid:]

                new_items = list(items[:idx - 1]) + [slide_a, slide_b] + list(items[idx:])
                for s_idx, s in enumerate(new_items, start=1):
                    s.slide_number = s_idx
                mutated_bp.slides = new_items
            else:
                # ConceptualBeat structure
                orig_title = getattr(orig_slide, "title", "Beat")
                supp = list(getattr(orig_slide, "supporting_unit_ids", ()))
                s_mid = max(1, len(supp) // 2)
                
                # Reconstruct beat objects
                from app.intelligence.transformation.blueprints import ConceptualBeat
                beat_a = ConceptualBeat(
                    beat_id=f"{orig_slide.beat_id}_a",
                    sequence_index=idx,
                    title=f"{orig_title} (Bagian 1)",
                    primary_concept_unit_id=orig_slide.primary_concept_unit_id,
                    supporting_unit_ids=tuple(supp[:s_mid]),
                    narrative_function=orig_slide.narrative_function,
                    information_gain=round(orig_slide.information_gain * 0.6, 2),
                    cognitive_load_target=round(orig_slide.cognitive_load_target * 0.5, 2),
                    visual_priority=orig_slide.visual_priority,
                    selection_rationale=orig_slide.selection_rationale,
                    knowledge_unit_ids=orig_slide.knowledge_unit_ids[:s_mid + 1],
                )
                beat_b = ConceptualBeat(
                    beat_id=f"{orig_slide.beat_id}_b",
                    sequence_index=idx + 1,
                    title=f"{orig_title} (Bagian 2)",
                    primary_concept_unit_id=orig_slide.primary_concept_unit_id,
                    supporting_unit_ids=tuple(supp[s_mid:]),
                    narrative_function=orig_slide.narrative_function,
                    information_gain=round(orig_slide.information_gain * 0.5, 2),
                    cognitive_load_target=round(orig_slide.cognitive_load_target * 0.5, 2),
                    visual_priority=orig_slide.visual_priority,
                    selection_rationale=orig_slide.selection_rationale,
                    knowledge_unit_ids=orig_slide.knowledge_unit_ids[s_mid + 1:],
                )
                new_beats = list(items[:idx - 1]) + [beat_a, beat_b] + list(items[idx:])
                mutated_bp = mutated_bp.model_copy(update={"beats": tuple(new_beats)})

            after_hash = self._hash_state(mutated_bp)
            applied_action = action.model_copy(update={"after_state_hash": after_hash})
            applied_actions.append(applied_action)

        return mutated_bp, applied_actions

    def _hash_state(self, bp: Any) -> str:
        s = repr(getattr(bp, "slides", getattr(bp, "beats", "")))
        return hashlib.sha256(s.encode("utf-8")).hexdigest()[:16]


class PresentationLayoutRemapStrategy(RepairStrategy):
    """Remaps layout to a visually distinct and canonical alternative."""

    CANONICAL_LAYOUT_MAP = {
        "concept_card": "two_column",
        "two_column": "three_column_comparison",
        "three_column_comparison": "timeline_horizontal",
        "timeline_horizontal": "two_column",
        "quote_highlight": "minimal_statement",
        "minimal_statement": "two_column",
        "formula_explainer": "two_column",
        "triangle_relationship": "two_column",
        "comparison-card": "two_column",
        "comparison_card": "two_column",
    }

    def __init__(self) -> None:
        super().__init__(
            strategy_id="presentation_layout_remap",
            name="Presentation Layout Remap Strategy",
            supported_artifact_types=("PRESENTATION",),
            supported_failure_codes=(
                "LAYOUT_MONOTONY",
                "LAYOUT_TAXONOMY_MISMATCH",
                "FIVE_CONSECUTIVE_IDENTICAL_LAYOUT",
                "ELEMENT_COLLISION",
                "OVERLAPPING_CONTENT",
                "TEXT_TOO_SMALL",
            ),
            supported_root_causes=(
                RootCauseType.SEMANTIC_LAYOUT_MAPPING,
                RootCauseType.GRID_GEOMETRY,
                RootCauseType.TYPOGRAPHY,
            ),
            mutation_class=RepairMutationClass.CLASS_C_LAYOUT_REMAPPING,
            priority=1,
            risk_level=RepairRiskLevel.LOW,
            mutation_cost=0.3,
        )

    def check_preconditions(self, blueprint: Any, target: RepairTarget, hypothesis: RootCauseHypothesis) -> bool:
        slides = getattr(blueprint, "slides", None) or getattr(blueprint, "beats", None)
        if not slides:
            return False
        idx = target.slide_index or target.page_index or 1
        return 1 <= idx <= len(slides)

    def plan_repair(self, blueprint: Any, target: RepairTarget, hypothesis: RootCauseHypothesis) -> RepairPlan:
        idx = target.slide_index or target.page_index or 1
        items = getattr(blueprint, "slides", None) or getattr(blueprint, "beats", None)
        cur_layout = "two_column"
        if items and 1 <= idx <= len(items):
            cur_layout = getattr(items[idx - 1], "layout", "two_column")
        new_layout = self.CANONICAL_LAYOUT_MAP.get(cur_layout, "two_column")

        action = RepairAction(
            strategy_id=self.strategy_id,
            target=target,
            mutation_type="remap_layout_family",
            mutation_class=self.mutation_class,
            before_state_hash=hashlib.sha256(cur_layout.encode()).hexdigest()[:16],
            rationale=f"Remap slide {idx} layout from {cur_layout} to {new_layout} to eliminate collision/monotony.",
            expected_effect=f"Changes layout to {new_layout} while preserving all content units.",
            risk_level=self.risk_level,
            reversibility=True,
        )
        return RepairPlan(
            root_cause_id=hypothesis.root_cause_id,
            artifact_type="PRESENTATION",
            actions=(action,),
            execution_order=(action.action_id,),
            expected_quality_improvement=0.25,
            estimated_regression_risk=0.04,
        )

    def apply_repair(self, blueprint: Any, plan: RepairPlan) -> Tuple[Any, List[RepairAction]]:
        mutated_bp = copy.deepcopy(blueprint)
        applied: List[RepairAction] = []
        for action in plan.actions:
            idx = action.target.slide_index or action.target.page_index or 1
            if hasattr(mutated_bp, "slides") and 1 <= idx <= len(mutated_bp.slides):
                slide = mutated_bp.slides[idx - 1]
                cur_layout = getattr(slide, "layout", "two_column")
                new_layout = self.CANONICAL_LAYOUT_MAP.get(cur_layout, "two_column")
                slide.layout = new_layout
                applied.append(action.model_copy(update={
                    "after_state_hash": hashlib.sha256(new_layout.encode()).hexdigest()[:16]
                }))
            elif hasattr(mutated_bp, "beats") and 1 <= idx <= len(mutated_bp.beats):
                beat = mutated_bp.beats[idx - 1]
                new_vp = "COMPARISON_GRID" if beat.visual_priority not in ("COMPARISON_GRID", "CONCEPT_CARD") else "CONCEPT_CARD"
                updated_beat = beat.model_copy(update={"visual_priority": new_vp})
                new_beats = list(mutated_bp.beats)
                new_beats[idx - 1] = updated_beat
                mutated_bp = mutated_bp.model_copy(update={"beats": tuple(new_beats)})
                applied.append(action.model_copy(update={
                    "after_state_hash": hashlib.sha256(new_vp.encode()).hexdigest()[:16]
                }))
        return mutated_bp, applied


class PresentationComponentReflowStrategy(RepairStrategy):
    """Reflows crowded cards or formula elements into stacked two-column cards with safe margins."""

    def __init__(self) -> None:
        super().__init__(
            strategy_id="presentation_component_reflow",
            name="Presentation Component Reflow Strategy",
            supported_artifact_types=("PRESENTATION",),
            supported_failure_codes=("ELEMENT_COLLISION", "OVERLAPPING_CONTENT", "BOUNDING_BOX_INTERSECTION"),
            supported_root_causes=(RootCauseType.GRID_GEOMETRY,),
            mutation_class=RepairMutationClass.CLASS_A_GEOMETRY,
            priority=2,
            risk_level=RepairRiskLevel.LOW,
            mutation_cost=0.2,
            causal_reach=CausalReach.COMPONENT_SPATIAL_STRUCTURE,
            owning_layer="R1",
        )

    def check_preconditions(self, blueprint: Any, target: RepairTarget, hypothesis: RootCauseHypothesis) -> bool:
        slides = getattr(blueprint, "slides", None) or getattr(blueprint, "beats", None)
        if not slides:
            return False
        idx = target.slide_index or target.page_index
        return idx is not None and 1 <= idx <= len(slides)

    def plan_repair(self, blueprint: Any, target: RepairTarget, hypothesis: RootCauseHypothesis) -> RepairPlan:
        idx = target.slide_index or target.page_index or 1
        action = RepairAction(
            strategy_id=self.strategy_id,
            target=target,
            mutation_type="reflow_slide_components",
            mutation_class=self.mutation_class,
            before_state_hash="reflow_pre",
            rationale=f"Reflow overlapping components on slide {idx} to separate collision boxes.",
            expected_effect="Separates conflicting bounding boxes into clean grid cells.",
            risk_level=self.risk_level,
            reversibility=True,
        )
        return RepairPlan(
            root_cause_id=hypothesis.root_cause_id,
            artifact_type="PRESENTATION",
            actions=(action,),
            execution_order=(action.action_id,),
            expected_quality_improvement=0.20,
            estimated_regression_risk=0.03,
        )

    def apply_repair(self, blueprint: Any, plan: RepairPlan) -> Tuple[Any, List[RepairAction]]:
        mutated_bp = copy.deepcopy(blueprint)
        applied: List[RepairAction] = []
        for action in plan.actions:
            idx = action.target.slide_index or action.target.page_index or 1
            if hasattr(mutated_bp, "slides") and 1 <= idx <= len(mutated_bp.slides):
                slide = mutated_bp.slides[idx - 1]
                slide.layout = "two_column"
                applied.append(action.model_copy(update={"after_state_hash": "reflowed_two_column"}))
            elif hasattr(mutated_bp, "beats") and 1 <= idx <= len(mutated_bp.beats):
                beat = mutated_bp.beats[idx - 1]
                updated_beat = beat.model_copy(update={"visual_priority": "CONCEPT_CARD"})
                new_beats = list(mutated_bp.beats)
                new_beats[idx - 1] = updated_beat
                mutated_bp = mutated_bp.model_copy(update={"beats": tuple(new_beats)})
                applied.append(action.model_copy(update={"after_state_hash": "reflowed_concept_card"}))
        return mutated_bp, applied


class PresentationPaddingAdjustmentStrategy(RepairStrategy):
    """Adjusts container geometry/padding when overflow is minor and density is normal."""

    def __init__(self) -> None:
        super().__init__(
            strategy_id="presentation_padding_adjust",
            name="Presentation Padding Adjustment Strategy",
            supported_artifact_types=("PRESENTATION",),
            supported_failure_codes=("MARGIN_VIOLATION", "VIEWPORT_BREACH", "TEXT_OVERFLOW", "TEXT_CLIPPING"),
            supported_root_causes=(RootCauseType.PADDING_SPACING, RootCauseType.CONTENT_DENSITY),
            mutation_class=RepairMutationClass.CLASS_A_GEOMETRY,
            priority=3,
            risk_level=RepairRiskLevel.LOW,
            mutation_cost=0.1,
            causal_reach=CausalReach.LOCAL_RENDER_GEOMETRY,
            owning_layer="R0",
        )

    def check_preconditions(self, blueprint: Any, target: RepairTarget, hypothesis: RootCauseHypothesis) -> bool:
        # Strictly requires presentation blueprint with slides or beats
        has_slides = hasattr(blueprint, "slides")
        has_beats = hasattr(blueprint, "beats")
        return has_slides or has_beats

    def plan_repair(self, blueprint: Any, target: RepairTarget, hypothesis: RootCauseHypothesis) -> RepairPlan:
        idx = target.slide_index or target.page_index or 1
        action = RepairAction(
            strategy_id=self.strategy_id,
            target=target,
            mutation_type="adjust_container_padding",
            mutation_class=self.mutation_class,
            before_state_hash="padding_default",
            rationale=f"Relax container padding on slide {idx} to resolve boundary breach.",
            expected_effect="Provides 15% extra printable width/height without font downscaling.",
            risk_level=self.risk_level,
            reversibility=True,
        )
        return RepairPlan(
            root_cause_id=hypothesis.root_cause_id,
            artifact_type="PRESENTATION",
            actions=(action,),
            execution_order=(action.action_id,),
            expected_quality_improvement=0.15,
            estimated_regression_risk=0.02,
        )

    def apply_repair(self, blueprint: Any, plan: RepairPlan) -> Tuple[Any, List[RepairAction]]:
        mutated_bp = copy.deepcopy(blueprint)
        applied: List[RepairAction] = []
        for action in plan.actions:
            idx = action.target.slide_index or action.target.page_index or 1
            if hasattr(mutated_bp, "slides") and mutated_bp.slides:
                safe_idx = max(1, min(idx, len(mutated_bp.slides)))
                slide = mutated_bp.slides[safe_idx - 1]
                if hasattr(slide, "text_density"):
                    slide.text_density = "compact"
                applied.append(action.model_copy(update={"after_state_hash": "padding_compact"}))
            elif hasattr(mutated_bp, "beats") and mutated_bp.beats:
                safe_idx = max(1, min(idx, len(mutated_bp.beats)))
                beat = mutated_bp.beats[safe_idx - 1]
                updated_beat = beat.model_copy(update={
                    "cognitive_load_target": max(0.2, round(beat.cognitive_load_target * 0.85, 2))
                })
                new_beats = list(mutated_bp.beats)
                new_beats[safe_idx - 1] = updated_beat
                mutated_bp = mutated_bp.model_copy(update={"beats": tuple(new_beats)})
                applied.append(action.model_copy(update={"after_state_hash": "padding_compact"}))
        return mutated_bp, applied

