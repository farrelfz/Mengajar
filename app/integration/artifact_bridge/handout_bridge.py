"""
Universal Knowledge Core — Handout Blueprint Bridge.

Phase 1D Artifact Blueprint Bridge Integration:
Translates HandoutBlueprint (ExplanatorySections) into Handout RenderArtifact.

Preserves reading hierarchy, context continuity, definitions, examples, and reading depth.
Contains NO CSS, margins, font sizes, or HTML template code.
"""

from __future__ import annotations

import time
from typing import Dict, List, Tuple, Type

from app.intelligence.transformation.blueprints import ArtifactBlueprint, HandoutBlueprint
from app.integration.artifact_bridge.base import ArtifactBlueprintBridge
from app.integration.artifact_bridge.contracts import (
    RenderArtifact,
    RenderMetadata,
    RenderSection,
    RenderTraceabilityRef,
    RenderUnit,
)


class HandoutBlueprintBridge(ArtifactBlueprintBridge):
    """Bridge converting HandoutBlueprint to renderer-neutral handout RenderArtifact."""

    @property
    def supported_blueprint_type(self) -> Type[ArtifactBlueprint]:
        return HandoutBlueprint

    def bridge(self, blueprint: ArtifactBlueprint) -> RenderArtifact:
        self.validate_blueprint(blueprint)
        assert isinstance(blueprint, HandoutBlueprint)

        sections: List[RenderSection] = []
        all_units: List[RenderUnit] = []
        traceability_refs: Dict[str, RenderTraceabilityRef] = {}

        for sec in blueprint.sections:
            ref = RenderTraceabilityRef(
                blueprint_element_id=sec.section_id,
                knowledge_unit_ids=sec.knowledge_unit_ids,
                relationship_ids=(),
                source_section_ids=(),
            )
            traceability_refs[sec.section_id] = ref

            metadata = {
                "heading_level": sec.heading_level,
                "reading_depth": sec.reading_depth,
                "core_unit_ids": list(sec.core_unit_ids),
                "supporting_unit_ids": list(sec.supporting_unit_ids),
                "definitions_count": len(sec.definitions),
                "examples_count": len(sec.examples),
                "layout_intent": "EXPLANATORY_SECTION",
            }

            # Build core content body from definitions and examples
            body_parts = []
            if sec.definitions:
                body_parts.append("Definitions:\n" + "\n".join(f"- {d}" for d in sec.definitions))
            if sec.examples:
                body_parts.append("Examples:\n" + "\n".join(f"- {e}" for e in sec.examples))
            
            content_str = "\n\n".join(body_parts) if body_parts else sec.topic

            unit = RenderUnit(
                unit_id=f"r_sec_{sec.sequence_index:02d}",
                role="EXPLANATORY_SECTION",
                title=sec.topic,
                content=content_str,
                supporting_content=sec.examples,
                sequence_index=sec.sequence_index,
                semantic_metadata=metadata,
                traceability_refs=ref,
            )
            all_units.append(unit)

            render_sec = RenderSection(
                section_id=sec.section_id,
                title=sec.topic,
                sequence_index=sec.sequence_index,
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
                "target_format": "a4_portrait",
                "narrative_mode": blueprint.intent.narrative_mode,
                "compression_strategy": blueprint.intent.compression_strategy,
            },
        )

        artifact_id = f"render_handout_{blueprint.blueprint_id}"
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
