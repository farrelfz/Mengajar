"""
Universal Knowledge Core — Presentation Contract Adapter.

Phase 2B Controlled Renderer Execution:
Refactored to Compatibility-First Grouping with auditable GroupingDecisionTrace records.
Eliminates mechanical fixed-size grouping in favor of semantic compatibility and narrative continuity.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple
from collections import defaultdict

from app.integration.artifact_bridge.contracts import RenderArtifact, RenderUnit
from app.integration.renderer_adapters.base import RendererContractAdapter
from app.integration.renderer_adapters.contracts import (
    GroupingDecisionTrace,
    LegacyPresentationDeck,
    SlideBlueprint,
)


class PresentationContractAdapter(RendererContractAdapter):
    """Adapts presentation RenderArtifact into legacy SlideBlueprint structures."""

    @property
    def supported_artifact_type(self) -> str:
        return "PRESENTATION"

    def adapt(
        self,
        render_artifact: RenderArtifact,
        grouping_mode: str = "capacity_constraint",
        max_beats_per_slide: int = 2,
    ) -> LegacyPresentationDeck:
        self.validate_artifact(render_artifact)

        for unit in render_artifact.units:
            if unit.role != "CONCEPTUAL_BEAT":
                raise ValueError(
                    f"Unsupported unit role '{unit.role}' in presentation RenderArtifact. "
                    f"Expected 'CONCEPTUAL_BEAT'."
                )
            if "narrative_function" not in unit.semantic_metadata:
                raise ValueError(
                    f"RenderUnit '{unit.unit_id}' missing required 'narrative_function' metadata."
                )

        # Compatibility-First Grouping
        beat_groups: List[List[RenderUnit]] = []
        decision_traces: List[GroupingDecisionTrace] = []

        if grouping_mode == "1_to_1" or max_beats_per_slide <= 1:
            for u in render_artifact.units:
                beat_groups.append([u])
                decision_traces.append(
                    GroupingDecisionTrace(
                        group_id=f"slide_trace_{u.unit_id}",
                        source_element_ids=(u.traceability_refs.blueprint_element_id,),
                        grouping_reason="1-to-1 beat allocation requested",
                        compatibility_signals=("solitary_focus",),
                        continuity_signals=(f"sequence_index_{u.sequence_index}",),
                        capacity_constraint="max_beats_per_slide=1",
                    )
                )
        else:
            current_group: List[RenderUnit] = []
            rejected_candidates: List[str] = []

            for unit in render_artifact.units:
                if not current_group:
                    current_group.append(unit)
                    rejected_candidates = []
                    continue

                curr_fn = current_group[0].semantic_metadata.get("narrative_function", "")
                unit_fn = unit.semantic_metadata.get("narrative_function", "")
                last_unit = current_group[-1]

                # Compatibility signal: identical narrative segment
                is_compatible_fn = (curr_fn == unit_fn)
                # Continuity signal: strictly contiguous sequence indices
                is_contiguous = (unit.sequence_index == last_unit.sequence_index + 1)
                # Capacity constraint: cognitive load budget and max beats
                curr_load = sum(
                    float(u.semantic_metadata.get("cognitive_load_target", 0.5)) for u in current_group
                )
                cand_load = float(unit.semantic_metadata.get("cognitive_load_target", 0.5))
                load_ok = (curr_load + cand_load) <= 1.5
                capacity_ok = len(current_group) < max_beats_per_slide

                if is_compatible_fn and is_contiguous and load_ok and capacity_ok:
                    current_group.append(unit)
                else:
                    if not is_compatible_fn:
                        rejected_candidates.append(f"{unit.unit_id}: narrative_function_mismatch ({curr_fn} != {unit_fn})")
                    elif not is_contiguous:
                        rejected_candidates.append(f"{unit.unit_id}: non_contiguous_sequence")
                    elif not load_ok:
                        rejected_candidates.append(f"{unit.unit_id}: cognitive_budget_exceeded ({curr_load + cand_load:.2f} > 1.5)")
                    elif not capacity_ok:
                        rejected_candidates.append(f"{unit.unit_id}: capacity_limit_reached ({max_beats_per_slide})")

                    grp_id = f"pres_group_{len(beat_groups) + 1:02d}"
                    decision_traces.append(
                        GroupingDecisionTrace(
                            group_id=grp_id,
                            source_element_ids=tuple(u.traceability_refs.blueprint_element_id for u in current_group),
                            grouping_reason=f"Narrative continuity in {curr_fn} segment",
                            compatibility_signals=(f"shared_narrative_function: {curr_fn}",),
                            continuity_signals=(f"contiguous_sequence_range: {current_group[0].sequence_index}-{current_group[-1].sequence_index}",),
                            capacity_constraint=f"max_beats={max_beats_per_slide}, cognitive_budget=1.5",
                            rejected_candidates=tuple(rejected_candidates),
                        )
                    )
                    beat_groups.append(current_group)
                    current_group = [unit]
                    rejected_candidates = []

            if current_group:
                grp_id = f"pres_group_{len(beat_groups) + 1:02d}"
                curr_fn = current_group[0].semantic_metadata.get("narrative_function", "")
                decision_traces.append(
                    GroupingDecisionTrace(
                        group_id=grp_id,
                        source_element_ids=tuple(u.traceability_refs.blueprint_element_id for u in current_group),
                        grouping_reason=f"Final narrative segment in {curr_fn}",
                        compatibility_signals=(f"shared_narrative_function: {curr_fn}",),
                        continuity_signals=(f"contiguous_sequence_range: {current_group[0].sequence_index}-{current_group[-1].sequence_index}",),
                        capacity_constraint=f"max_beats={max_beats_per_slide}",
                        rejected_candidates=tuple(rejected_candidates),
                    )
                )
                beat_groups.append(current_group)

        slides: List[SlideBlueprint] = []
        source_to_slide_map: Dict[str, List[int]] = defaultdict(list)
        slide_to_source_map: Dict[int, List[str]] = {}
        layout_dist: Dict[str, int] = defaultdict(int)
        priority_rank = {"HIGH_DIAGRAM": 3, "EQUATION_FOCUS": 2, "CONCEPT_TEXT": 1}

        slide_counter = 1
        act_counter = 1
        last_narrative_fn: Optional[str] = None

        for group in beat_groups:
            first_unit = group[0]
            narrative_fn = first_unit.semantic_metadata.get("narrative_function", "CONCEPT_INTRODUCTION")

            if last_narrative_fn is not None and narrative_fn != last_narrative_fn:
                act_counter += 1
            last_narrative_fn = narrative_fn

            act_id = f"act-{act_counter:02d}"
            act_name = f"ACT {act_counter} — {narrative_fn}"
            source_element_ids = tuple(u.traceability_refs.blueprint_element_id for u in group)
            source_refs = tuple(u.unit_id for u in group)

            if len(group) == 1:
                title = first_unit.title
                bullet_points: Tuple[str, ...] = tuple()
            else:
                title = f"{narrative_fn.replace('_', ' ').title()}: {first_unit.title}"
                bullet_points = tuple(u.title for u in group)

            highest_vp = max(
                (u.semantic_metadata.get("visual_priority", "CONCEPT_TEXT") for u in group),
                key=lambda p: priority_rank.get(p, 0),
            )

            if narrative_fn in ("HOOK", "PHENOMENON"):
                layout = "hero_composition"
                visual_intent = "hero_phenomenon"
            elif highest_vp == "EQUATION_FOCUS":
                layout = "formula_explainer"
                visual_intent = "formula_focus"
            elif len(group) > 1:
                layout = "three_column_comparison" if len(group) == 3 else "concept_card"
                visual_intent = "concept_comparison" if len(group) == 3 else "concept_explainer"
            elif highest_vp == "HIGH_DIAGRAM":
                layout = "triangle_relationship"
                visual_intent = "diagram_focus"
            else:
                layout = "concept_card"
                visual_intent = "concept_explainer"

            cog_load = max(
                float(u.semantic_metadata.get("cognitive_load_target", 0.5)) for u in group
            )
            info_gain = sum(
                float(u.semantic_metadata.get("information_gain", 0.5)) for u in group
            ) / len(group)

            slide = SlideBlueprint(
                slide_id=f"slide_{slide_counter:02d}",
                slide_number=slide_counter,
                act_id=act_id,
                act_name=act_name,
                title=title,
                subtitle=first_unit.title if len(group) > 1 else None,
                narrative_function=narrative_fn,
                layout=layout,
                visual_priority=highest_vp,
                visual_intent=visual_intent,
                content=first_unit.content,
                bullet_points=bullet_points,
                source_element_ids=source_element_ids,
                source_refs=source_refs,
                cognitive_load=round(cog_load, 3),
                information_gain=round(info_gain, 3),
                metadata={
                    "group_size": len(group),
                    "progressive_sequence_indices": [u.sequence_index for u in group],
                    "layout_intent": first_unit.semantic_metadata.get("layout_intent", "SLIDE_BEAT"),
                },
            )
            slides.append(slide)
            layout_dist[layout] += 1

            for bp_id in source_element_ids:
                source_to_slide_map[bp_id].append(slide_counter)
            slide_to_source_map[slide_counter] = list(source_element_ids)
            slide_counter += 1

        return LegacyPresentationDeck(
            deck_title=render_artifact.document_title,
            total_slides=len(slides),
            slides=tuple(slides),
            source_to_slide_map={k: tuple(v) for k, v in source_to_slide_map.items()},
            slide_to_source_map={k: tuple(v) for k, v in slide_to_source_map.items()},
            layout_distribution=dict(layout_dist),
            grouping_decision_traces=tuple(decision_traces),
            metadata={
                "source_artifact_id": render_artifact.artifact_id,
                "source_blueprint_id": render_artifact.source_blueprint_id,
                "grouping_mode": grouping_mode,
                "total_beats_adapted": len(render_artifact.units),
            },
        )
