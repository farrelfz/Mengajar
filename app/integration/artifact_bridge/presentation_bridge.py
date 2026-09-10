"""
Universal Knowledge Core — Presentation Blueprint Bridge.

Phase 1D Artifact Blueprint Bridge Integration:
Translates PresentationBlueprint (ConceptualBeats) into Presentation RenderArtifact.

Preserves narrative function, visual priority, cognitive load, and progressive sequence.
Contains NO CSS, layout coordinates, font sizes, or Playwright imports.
"""

from __future__ import annotations

import time
from typing import Dict, List, Tuple, Type

from app.intelligence.transformation.blueprints import ArtifactBlueprint, PresentationBlueprint
from app.integration.artifact_bridge.base import ArtifactBlueprintBridge
from app.integration.artifact_bridge.contracts import (
    RenderArtifact,
    RenderMetadata,
    RenderSection,
    RenderTraceabilityRef,
    RenderUnit,
)


class PresentationBlueprintBridge(ArtifactBlueprintBridge):
    """Bridge converting PresentationBlueprint to renderer-neutral presentation RenderArtifact."""

    @property
    def supported_blueprint_type(self) -> Type[ArtifactBlueprint]:
        return PresentationBlueprint

    def bridge(self, blueprint: ArtifactBlueprint) -> RenderArtifact:
        self.validate_blueprint(blueprint)
        assert isinstance(blueprint, PresentationBlueprint)

        render_units: List[RenderUnit] = []
        traceability_refs: Dict[str, RenderTraceabilityRef] = {}

        for beat in blueprint.beats:
            ref = RenderTraceabilityRef(
                blueprint_element_id=beat.beat_id,
                knowledge_unit_ids=beat.knowledge_unit_ids,
                relationship_ids=(),
                source_section_ids=(),
            )
            traceability_refs[beat.beat_id] = ref

            metadata = {
                "narrative_function": beat.narrative_function,
                "visual_priority": beat.visual_priority,
                "cognitive_load_target": beat.cognitive_load_target,
                "information_gain": beat.information_gain,
                "primary_concept_unit_id": beat.primary_concept_unit_id,
                "supporting_unit_ids": list(beat.supporting_unit_ids),
                "selection_rationale": beat.selection_rationale,
                "layout_intent": "SLIDE_BEAT",  # Renderer-neutral hint
            }

            unit = RenderUnit(
                unit_id=f"r_beat_{beat.sequence_index:02d}",
                role="CONCEPTUAL_BEAT",
                title=beat.title,
                content=beat.title,
                supporting_content=tuple(beat.supporting_unit_ids),
                sequence_index=beat.sequence_index,
                semantic_metadata=metadata,
                traceability_refs=ref,
            )
            render_units.append(unit)

        # Wrap render units into a presentation section container
        section = RenderSection(
            section_id="sec_pres_deck",
            title=blueprint.document_title,
            sequence_index=1,
            units=tuple(render_units),
            section_metadata={"section_type": "PRESENTATION_DECK"},
        )

        metadata_obj = RenderMetadata(
            artifact_type=blueprint.artifact_type.value,
            document_title=blueprint.document_title,
            domain=blueprint.intent.depth,
            audience_level=blueprint.intent.audience.value,
            total_units=len(render_units),
            total_sections=1,
            rendering_hints={
                "target_format": "presentation_16_9",
                "narrative_mode": blueprint.intent.narrative_mode,
                "compression_strategy": blueprint.intent.compression_strategy,
            },
        )

        artifact_id = f"render_pres_{blueprint.blueprint_id}"
        return RenderArtifact(
            artifact_id=artifact_id,
            artifact_type=blueprint.artifact_type.value,
            document_title=blueprint.document_title,
            source_blueprint_id=blueprint.blueprint_id,
            source_manifest_id=blueprint.source_manifest_id,
            metadata=metadata_obj,
            sections=(section,),
            units=tuple(render_units),
            traceability_refs=traceability_refs,
        )
