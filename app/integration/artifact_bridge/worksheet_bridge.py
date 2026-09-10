"""
Universal Knowledge Core — Worksheet Blueprint Bridge.

Phase 1C.1 & Phase 1D Integration:
Translates WorksheetBlueprint (LearningActivities) into Worksheet RenderArtifact.

Preserves activity types (PHENOMENON, PREDICTION, QUESTION, INVESTIGATION, etc.), inquiry ordering,
and withhold_explanation policies. Does NOT flatten activities into generic paragraphs.
"""

from __future__ import annotations

import time
from typing import Dict, List, Tuple, Type

from app.intelligence.transformation.blueprints import ArtifactBlueprint, WorksheetBlueprint
from app.integration.artifact_bridge.base import ArtifactBlueprintBridge
from app.integration.artifact_bridge.contracts import (
    RenderArtifact,
    RenderMetadata,
    RenderSection,
    RenderTraceabilityRef,
    RenderUnit,
)


class WorksheetBlueprintBridge(ArtifactBlueprintBridge):
    """Bridge converting WorksheetBlueprint to renderer-neutral worksheet RenderArtifact."""

    @property
    def supported_blueprint_type(self) -> Type[ArtifactBlueprint]:
        return WorksheetBlueprint

    def bridge(self, blueprint: ArtifactBlueprint) -> RenderArtifact:
        self.validate_blueprint(blueprint)
        assert isinstance(blueprint, WorksheetBlueprint)

        sections: List[RenderSection] = []
        all_units: List[RenderUnit] = []
        traceability_refs: Dict[str, RenderTraceabilityRef] = {}

        for act in blueprint.activities:
            ref = RenderTraceabilityRef(
                blueprint_element_id=act.activity_id,
                knowledge_unit_ids=act.knowledge_unit_ids,
                relationship_ids=(),
                source_section_ids=(),
            )
            traceability_refs[act.activity_id] = ref

            metadata = {
                "inquiry_activity_type": act.activity_type.value,
                "scaffolding_level": act.scaffolding_level,
                "withhold_explanation": act.withhold_explanation,
                "expected_reasoning_type": act.expected_reasoning_type,
                "target_knowledge_unit_ids": list(act.target_knowledge_unit_ids),
                "layout_intent": "INQUIRY_ACTIVITY_BOX",
                "requires_student_workspace": True,
            }

            unit = RenderUnit(
                unit_id=f"r_act_{act.sequence_index:02d}",
                role="LEARNING_ACTIVITY",
                title=act.title,
                content=act.prompt_text,
                supporting_content=act.target_knowledge_unit_ids,
                sequence_index=act.sequence_index,
                semantic_metadata=metadata,
                traceability_refs=ref,
            )
            all_units.append(unit)

            render_sec = RenderSection(
                section_id=f"sec_act_{act.sequence_index:02d}",
                title=act.title,
                sequence_index=act.sequence_index,
                units=(unit,),
                section_metadata=metadata,
            )
            sections.append(render_sec)

        metadata_obj = RenderMetadata(
            artifact_type=blueprint.artifact_type.value,
            document_title=blueprint.document_title,
            domain=blueprint.intent.depth,
            audience_level=blueprint.intent.audience.value,
            total_units=len(all_units),
            total_sections=len(sections),
            rendering_hints={
                "target_format": "a4_portrait_worksheet",
                "narrative_mode": blueprint.intent.narrative_mode,
                "withhold_explanation_policy": True,
            },
        )

        artifact_id = f"render_ws_{blueprint.blueprint_id}"
        return RenderArtifact(
            artifact_id=artifact_id,
            artifact_type=blueprint.artifact_type.value,
            document_title=blueprint.document_title,
            source_blueprint_id=blueprint.blueprint_id,
            source_manifest_id=blueprint.source_manifest_id,
            metadata=metadata_obj,
            sections=tuple(sections),
            units=tuple(all_units),
            traceability_refs=traceability_refs,
        )
