"""
Universal Knowledge Core — Worksheet Contract Adapter.

Phase 2A Controlled Renderer Adapter Integration:
Translates Worksheet RenderArtifact (LearningActivities) into LegacyWorksheetDocument
(PedagogicalBlueprint, ContentGroups, and LegacyWorksheetSections).

Preserves:
- Typed learning activities (PHENOMENON, PREDICTION, OBSERVATION, INVESTIGATION, DATA_ANALYSIS, REFLECTION)
- Inquiry ordering and scaffolding progression
- Withhold explanation policy (MUST remain True)
- Student workspace requirements (MUST remain True)
- Strict typed activity identity — NEVER flattened into generic paragraphs
- Complete bidirectional traceability (Many-to-One mapping supported)

Contains zero AI calls, answer generation, or renderer imports.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple
from collections import defaultdict

from app.blueprints.pedagogical import (
    PedagogicalBlueprint,
    PedagogicalPattern,
    PedagogicalStep,
    SemanticStepType,
)
from app.intelligence.schemas import (
    BlueprintCandidateType,
    ContentDensity,
    ContentGroup,
    VisualIntent,
)
from app.integration.artifact_bridge.contracts import RenderArtifact, RenderUnit
from app.integration.renderer_adapters.base import RendererContractAdapter
from app.integration.renderer_adapters.contracts import (
    GroupingDecisionTrace,
    LegacyWorksheetActivity,
    LegacyWorksheetDocument,
    LegacyWorksheetSection,
)

INQUIRY_FORWARD_ORDER = {
    "PHENOMENON": 1,
    "PREDICTION": 2,
    "QUESTION": 2,
    "OBSERVATION": 3,
    "INVESTIGATION": 4,
    "DATA_ANALYSIS": 5,
    "REFLECTION": 6,
}

# Deterministic mapping from Worksheet Activity Types to Pedagogical Step Types
ACTIVITY_TO_STEP_TYPE = {
    "PHENOMENON": SemanticStepType.PHENOMENON,
    "PREDICTION": SemanticStepType.QUESTION,
    "QUESTION": SemanticStepType.QUESTION,
    "OBSERVATION": SemanticStepType.OBSERVATION,
    "INVESTIGATION": SemanticStepType.PRACTICE,
    "DATA_ANALYSIS": SemanticStepType.OBSERVATION,
    "REFLECTION": SemanticStepType.REFLECTION,
}


class WorksheetContractAdapter(RendererContractAdapter):
    """Adapts Worksheet RenderArtifact into LegacyWorksheetDocument."""

    @property
    def supported_artifact_type(self) -> str:
        return "WORKSHEET"

    def adapt(
        self,
        render_artifact: RenderArtifact,
        activities_per_section: int = 3,
        grouping_mode: str = "chunk",
    ) -> LegacyWorksheetDocument:
        """Deterministically adapts worksheet RenderArtifact into LegacyWorksheetDocument.

        Args:
            render_artifact: Certified worksheet RenderArtifact contract.
            activities_per_section: Target number of activities grouped per worksheet section.
            grouping_mode: "chunk", "compatibility", or "1_to_1".

        Returns:
            LegacyWorksheetDocument with PedagogicalBlueprint, ContentGroups, Sections, and Traces.
        """
        self.validate_artifact(render_artifact)

        # 1. Validate render units and activity types
        legacy_activities: List[LegacyWorksheetActivity] = []
        for unit in render_artifact.units:
            if unit.role != "LEARNING_ACTIVITY":
                raise ValueError(
                    f"Unsupported unit role '{unit.role}' in worksheet RenderArtifact. "
                    f"Expected 'LEARNING_ACTIVITY'."
                )

            act_type = unit.semantic_metadata.get("inquiry_activity_type")
            if not act_type:
                raise ValueError(
                    f"RenderUnit '{unit.unit_id}' missing required 'inquiry_activity_type' metadata."
                )

            withhold_expl = unit.semantic_metadata.get("withhold_explanation", True)
            req_workspace = unit.semantic_metadata.get("requires_student_workspace", True)
            scaffolding = unit.semantic_metadata.get("scaffolding_level", "MEDIUM")
            reasoning = unit.semantic_metadata.get("expected_reasoning_type", "")
            target_kus = tuple(
                unit.semantic_metadata.get("target_knowledge_unit_ids", unit.supporting_content)
            )

            # Preserve strictly as typed activity
            act = LegacyWorksheetActivity(
                activity_id=unit.unit_id,
                activity_type=act_type,
                title=unit.title,
                prompt_text=unit.content,
                scaffolding_level=scaffolding,
                withhold_explanation=withhold_expl,
                requires_student_workspace=req_workspace,
                expected_reasoning_type=reasoning,
                sequence_index=unit.sequence_index,
                source_element_ids=(unit.traceability_refs.blueprint_element_id,),
                target_knowledge_unit_ids=target_kus,
                metadata=unit.semantic_metadata,
            )
            legacy_activities.append(act)

        # 2. Group activities into logical worksheet sections (Many-to-One mapping)
        act_chunks: List[List[LegacyWorksheetActivity]] = []
        decision_traces: List[GroupingDecisionTrace] = []

        if grouping_mode == "1_to_1" or activities_per_section == 1:
            for act in legacy_activities:
                act_chunks.append([act])
                decision_traces.append(
                    GroupingDecisionTrace(
                        group_id=f"ws_sec_{act.activity_id}",
                        source_element_ids=act.source_element_ids,
                        grouping_reason="1-to-1 inquiry activity allocation requested",
                        compatibility_signals=(f"activity_{act.activity_type}",),
                        continuity_signals=(f"sequence_index_{act.sequence_index}",),
                        capacity_constraint="activities_per_section=1",
                    )
                )
        elif grouping_mode == "compatibility":
            curr_chunk: List[LegacyWorksheetActivity] = []
            rejected_candidates: List[str] = []
            sec_idx = 1

            for act in legacy_activities:
                act_order = INQUIRY_FORWARD_ORDER.get(act.activity_type, 0)
                if not curr_chunk:
                    curr_chunk.append(act)
                    rejected_candidates = []
                    continue

                last_act = curr_chunk[-1]
                last_order = INQUIRY_FORWARD_ORDER.get(last_act.activity_type, 0)

                is_forward_order = (act_order >= last_order)
                is_contiguous = (act.sequence_index == last_act.sequence_index + 1)
                is_withhold_ok = (act.withhold_explanation == last_act.withhold_explanation)
                capacity_ok = (len(curr_chunk) < activities_per_section and len(curr_chunk) < 4)

                if is_forward_order and is_contiguous and is_withhold_ok and capacity_ok:
                    curr_chunk.append(act)
                else:
                    if not is_forward_order:
                        rejected_candidates.append(f"{act.activity_id}: inquiry_order_regression ({last_act.activity_type}->{act.activity_type})")
                    elif not is_contiguous:
                        rejected_candidates.append(f"{act.activity_id}: non_contiguous_sequence")
                    elif not capacity_ok:
                        rejected_candidates.append(f"{act.activity_id}: capacity_limit_reached")

                    act_chunks.append(curr_chunk)
                    decision_traces.append(
                        GroupingDecisionTrace(
                            group_id=f"ws_sec_{sec_idx:02d}",
                            source_element_ids=tuple(a.source_element_ids[0] for a in curr_chunk),
                            grouping_reason=f"Inquiry stage continuity: {[a.activity_type for a in curr_chunk]}",
                            compatibility_signals=tuple(f"activity_{a.activity_type}" for a in curr_chunk),
                            continuity_signals=(f"sequence_indices_{curr_chunk[0].sequence_index}_to_{curr_chunk[-1].sequence_index}",),
                            capacity_constraint=f"activities_per_section={activities_per_section}",
                            rejected_candidates=tuple(rejected_candidates),
                        )
                    )
                    sec_idx += 1
                    curr_chunk = [act]
                    rejected_candidates = []

            if curr_chunk:
                act_chunks.append(curr_chunk)
                decision_traces.append(
                    GroupingDecisionTrace(
                        group_id=f"ws_sec_{sec_idx:02d}",
                        source_element_ids=tuple(a.source_element_ids[0] for a in curr_chunk),
                        grouping_reason=f"Inquiry stage continuity: {[a.activity_type for a in curr_chunk]}",
                        compatibility_signals=tuple(f"activity_{a.activity_type}" for a in curr_chunk),
                        continuity_signals=(f"sequence_indices_{curr_chunk[0].sequence_index}_to_{curr_chunk[-1].sequence_index}",),
                        capacity_constraint=f"activities_per_section={activities_per_section}",
                        rejected_candidates=tuple(rejected_candidates),
                    )
                )
        else:  # grouping_mode == "chunk"
            chunk_size = max(1, activities_per_section)
            act_chunks = [
                legacy_activities[i : i + chunk_size]
                for i in range(0, len(legacy_activities), chunk_size)
            ]
            for idx, chunk in enumerate(act_chunks, 1):
                decision_traces.append(
                    GroupingDecisionTrace(
                        group_id=f"ws_sec_{idx:02d}",
                        source_element_ids=tuple(a.source_element_ids[0] for a in chunk),
                        grouping_reason=f"Capacity-constrained inquiry section grouping ({len(chunk)} activities)",
                        compatibility_signals=tuple(f"activity_{a.activity_type}" for a in chunk),
                        continuity_signals=(f"sequence_indices_{chunk[0].sequence_index}_to_{chunk[-1].sequence_index}",),
                        capacity_constraint=f"activities_per_section={activities_per_section}",
                    )
                )

        sections: List[LegacyWorksheetSection] = []
        content_groups: List[ContentGroup] = []
        source_to_act_map: Dict[str, List[str]] = defaultdict(list)

        sec_counter = 1
        for chunk in act_chunks:
            sec_source_elem_ids = tuple(act.source_element_ids[0] for act in chunk)
            first_act = chunk[0]
            sec_title = f"Section {sec_counter}: {first_act.activity_type.title()} Inquiry"

            sec = LegacyWorksheetSection(
                section_id=f"ws_sec_{sec_counter:02d}",
                title=sec_title,
                sequence_index=sec_counter,
                activities=tuple(chunk),
                source_element_ids=sec_source_elem_ids,
                metadata={
                    "activity_count": len(chunk),
                    "activity_types": [a.activity_type for a in chunk],
                },
            )
            sections.append(sec)

            # Legacy ContentGroup representation
            group_unit_ids: List[str] = []
            for a in chunk:
                group_unit_ids.extend(a.target_knowledge_unit_ids)

            cg = ContentGroup(
                group_id=f"cg_ws_{sec_counter:02d}",
                title=sec_title,
                unit_ids=list(dict.fromkeys(group_unit_ids)),
                blueprint_candidate=BlueprintCandidateType.PROCESS_SEQUENCE,
                primary_visual_intent=VisualIntent.STEP_BY_STEP,
                density=ContentDensity.MEDIUM,
                notes=f"Inquiry phase covering {', '.join(a.activity_type for a in chunk)}",
            )
            content_groups.append(cg)

            for act in chunk:
                for bp_id in act.source_element_ids:
                    source_to_act_map[bp_id].append(act.activity_id)

            sec_counter += 1

        # 3. Generate legacy PedagogicalBlueprint
        pedagogical_steps: List[PedagogicalStep] = []
        for act in legacy_activities:
            step_type = ACTIVITY_TO_STEP_TYPE.get(act.activity_type, SemanticStepType.PRACTICE)
            ped_step = PedagogicalStep(
                id=f"step_{act.activity_id}",
                semantic_type=step_type,
                purpose=act.prompt_text,
                target_concept_id=act.target_knowledge_unit_ids[0] if act.target_knowledge_unit_ids else None,
                content_ref_ids=list(act.target_knowledge_unit_ids),
                visual_intent="worksheet_activity",
                notes=f"Scaffolding: {act.scaffolding_level}, Withhold: {act.withhold_explanation}",
                metadata={
                    "activity_id": act.activity_id,
                    "activity_type": act.activity_type,
                    "expected_reasoning_type": act.expected_reasoning_type,
                    "withhold_explanation": act.withhold_explanation,
                    "requires_student_workspace": act.requires_student_workspace,
                },
            )
            pedagogical_steps.append(ped_step)

        pedagogical_blueprint = PedagogicalBlueprint(
            blueprint_id=f"ped_{render_artifact.source_blueprint_id}",
            primary_pattern=PedagogicalPattern.SCIENTIFIC_REASONING,
            narrative_rationale=f"Inquiry sequence for {render_artifact.document_title}",
            target_cognitive_load="balanced",
            sequence=pedagogical_steps,
        )

        return LegacyWorksheetDocument(
            document_id=f"ws_doc_{render_artifact.artifact_id}",
            title=render_artifact.document_title,
            pedagogical_blueprint=pedagogical_blueprint,
            content_groups=tuple(content_groups),
            sections=tuple(sections),
            total_activities=len(legacy_activities),
            source_to_activity_map={k: tuple(v) for k, v in source_to_act_map.items()},
            grouping_decision_traces=tuple(decision_traces),
            metadata={
                "source_artifact_id": render_artifact.artifact_id,
                "source_blueprint_id": render_artifact.source_blueprint_id,
                "audience_level": render_artifact.metadata.audience_level,
                "total_activities_adapted": len(legacy_activities),
                "activities_per_section": activities_per_section,
                "grouping_mode": grouping_mode,
            },
        )
