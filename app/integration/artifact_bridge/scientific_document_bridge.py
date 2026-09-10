"""
Universal Knowledge Core — Scientific Document Blueprint Bridge.

Phase 1D Artifact Blueprint Bridge Integration:
Translates ScientificDocumentBlueprint (ScientificArgumentUnits) into Scientific Document RenderArtifact.

Preserves claim/evidence relationships, argument roles, counter-considerations, and confidence.
Evidence traceability survives 100%. Does NOT invent citations or evidence.
"""

from __future__ import annotations

import time
from typing import Dict, List, Tuple, Type

from app.intelligence.transformation.blueprints import ArtifactBlueprint, ScientificDocumentBlueprint
from app.integration.artifact_bridge.base import ArtifactBlueprintBridge
from app.integration.artifact_bridge.contracts import (
    RenderArtifact,
    RenderMetadata,
    RenderSection,
    RenderTraceabilityRef,
    RenderUnit,
)


class ScientificDocumentBlueprintBridge(ArtifactBlueprintBridge):
    """Bridge converting ScientificDocumentBlueprint to renderer-neutral scientific RenderArtifact."""

    @property
    def supported_blueprint_type(self) -> Type[ArtifactBlueprint]:
        return ScientificDocumentBlueprint

    def bridge(self, blueprint: ArtifactBlueprint) -> RenderArtifact:
        self.validate_blueprint(blueprint)
        assert isinstance(blueprint, ScientificDocumentBlueprint)

        sections: List[RenderSection] = []
        all_units: List[RenderUnit] = []
        traceability_refs: Dict[str, RenderTraceabilityRef] = {}

        for arg in blueprint.arguments:
            # Validate evidence integrity: supporting evidence units must be grounded in knowledge_unit_ids
            for ev_id in arg.supporting_evidence_unit_ids:
                if ev_id not in arg.knowledge_unit_ids:
                    raise ValueError(
                        f"Unsupported evidence rejected: argument '{arg.argument_id}' references "
                        f"ungrounded evidence unit '{ev_id}' not in knowledge_unit_ids."
                    )

            ref = RenderTraceabilityRef(
                blueprint_element_id=arg.argument_id,
                knowledge_unit_ids=arg.knowledge_unit_ids,
                relationship_ids=arg.evidence_relationship_ids,
                source_section_ids=arg.source_traceability,
            )
            traceability_refs[arg.argument_id] = ref

            metadata = {
                "argument_role": arg.argument_role.value if hasattr(arg.argument_role, "value") else str(arg.argument_role),
                "claim_unit_id": arg.claim_unit_id,
                "supporting_evidence_unit_ids": list(arg.supporting_evidence_unit_ids),
                "evidence_relationship_ids": list(arg.evidence_relationship_ids),
                "counter_considerations": list(arg.counter_considerations),
                "confidence": arg.confidence,
                "source_traceability": list(arg.source_traceability),
                "layout_intent": "SCIENTIFIC_ARGUMENT_BLOCK",
            }

            unit = RenderUnit(
                unit_id=f"r_arg_{arg.sequence_index:02d}",
                role="SCIENTIFIC_ARGUMENT",
                title=f"Claim [{arg.argument_role.value}]: {arg.claim_statement[:50]}",
                content=arg.claim_statement,
                supporting_content=arg.supporting_evidence_unit_ids,
                sequence_index=arg.sequence_index,
                semantic_metadata=metadata,
                traceability_refs=ref,
            )
            all_units.append(unit)

            render_sec = RenderSection(
                section_id=f"sec_arg_{arg.sequence_index:02d}",
                title=f"Argument Unit {arg.sequence_index}",
                sequence_index=arg.sequence_index,
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
                "target_format": "a4_portrait_scientific",
                "evidence_requirement": blueprint.intent.evidence_requirement,
                "uncertainty_policy": blueprint.intent.uncertainty_policy.value,
            },
        )

        artifact_id = f"render_sci_{blueprint.blueprint_id}"
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
