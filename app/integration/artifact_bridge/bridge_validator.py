"""
Universal Knowledge Core — Artifact Bridge Traceability Validator.

Phase 1D Artifact Blueprint Bridge Integration:
Validates forward and reverse traceability, orphan detection, lost element detection,
sequence preservation, and evidence survival across the bridge boundary.
"""

from __future__ import annotations

from typing import Dict, List, Set, Tuple, Any
from pydantic import BaseModel, Field

from app.intelligence.transformation.blueprints import (
    ArtifactBlueprint,
    HandoutBlueprint,
    PresentationBlueprint,
    ScientificDocumentBlueprint,
    WorksheetBlueprint,
)
from app.integration.artifact_bridge.contracts import RenderArtifact


class BridgeValidationReport(BaseModel):
    """Validation outcome emitted by ArtifactBridgeValidator."""
    artifact_id: str
    artifact_type: str
    is_valid: bool
    total_blueprint_elements: int
    total_render_units: int
    orphan_render_unit_count: int
    lost_blueprint_element_ids: List[str] = Field(default_factory=list)
    sequence_violations: List[str] = Field(default_factory=list)
    evidence_loss_violations: List[str] = Field(default_factory=list)
    missing_knowledge_violations: List[str] = Field(default_factory=list)
    duplicated_unit_violations: List[str] = Field(default_factory=list)
    violations: List[str] = Field(default_factory=list)


class ArtifactBridgeValidator:
    """Validator enforcing complete traceability and structural survival across blueprint bridges."""

    def validate(
        self,
        blueprint: ArtifactBlueprint,
        render_artifact: RenderArtifact,
    ) -> BridgeValidationReport:
        violations: List[str] = []
        lost_elements: List[str] = []
        sequence_violations: List[str] = []
        evidence_violations: List[str] = []
        missing_knowledge_violations: List[str] = []
        duplicated_unit_violations: List[str] = []

        # 1. Extract Blueprint Elements and their Knowledge Unit IDs
        bp_element_map: Dict[str, Any] = {}
        if isinstance(blueprint, PresentationBlueprint):
            bp_element_map = {b.beat_id: b for b in blueprint.beats}
        elif isinstance(blueprint, HandoutBlueprint):
            bp_element_map = {s.section_id: s for s in blueprint.sections}
        elif isinstance(blueprint, WorksheetBlueprint):
            bp_element_map = {a.activity_id: a for a in blueprint.activities}
        elif isinstance(blueprint, ScientificDocumentBlueprint):
            bp_element_map = {a.argument_id: a for a in blueprint.arguments}

        blueprint_element_ids: Set[str] = set(bp_element_map.keys())

        # 2. Check Render Unit Traceability, Orphan Detection, and Duplication
        seen_blueprint_elements: Set[str] = set()
        seen_render_unit_ids: Set[str] = set()
        orphan_count = 0

        for unit in render_artifact.units:
            # Check duplicate unit_id
            if unit.unit_id in seen_render_unit_ids:
                dup_err = f"Duplicate RenderUnit id detected: {unit.unit_id}"
                duplicated_unit_violations.append(dup_err)
                violations.append(dup_err)
            seen_render_unit_ids.add(unit.unit_id)

            ref = unit.traceability_refs
            if not ref or not ref.blueprint_element_id:
                orphan_count += 1
                violations.append(f"RenderUnit {unit.unit_id} is an orphan without traceability ref.")
            elif ref.blueprint_element_id not in blueprint_element_ids:
                orphan_count += 1
                violations.append(
                    f"RenderUnit {unit.unit_id} references unknown blueprint element {ref.blueprint_element_id}."
                )
            else:
                # Check duplicate bridging of the same semantic blueprint element
                if ref.blueprint_element_id in seen_blueprint_elements:
                    dup_err = f"Duplicated semantic unit caused by bridging: {ref.blueprint_element_id}"
                    duplicated_unit_violations.append(dup_err)
                    violations.append(dup_err)
                seen_blueprint_elements.add(ref.blueprint_element_id)

                # 5. Check Missing Knowledge References
                bp_elem = bp_element_map[ref.blueprint_element_id]
                expected_ku = set(getattr(bp_elem, "knowledge_unit_ids", ()))
                actual_ku = set(ref.knowledge_unit_ids)
                missing_ku = expected_ku - actual_ku
                if missing_ku:
                    m_err = f"Missing knowledge unit references for {ref.blueprint_element_id}: {missing_ku}"
                    missing_knowledge_violations.append(m_err)
                    violations.append(m_err)

        # 3. Detect Lost Blueprint Elements
        for elem_id in blueprint_element_ids:
            if elem_id not in seen_blueprint_elements:
                lost_elements.append(elem_id)
                violations.append(f"Blueprint element {elem_id} was lost during bridging.")

        # 4. Check Sequence Index Preservation
        indices = [unit.sequence_index for unit in render_artifact.units]
        if indices != sorted(indices):
            seq_err = f"Sequence index order violated: {indices}"
            sequence_violations.append(seq_err)
            violations.append(seq_err)

        # 5. Scientific Evidence Survival Check
        if isinstance(blueprint, ScientificDocumentBlueprint):
            for unit in render_artifact.units:
                ref = unit.traceability_refs
                if ref and ref.blueprint_element_id in bp_element_map:
                    orig_arg = bp_element_map[ref.blueprint_element_id]
                    orig_rel = set(orig_arg.evidence_relationship_ids)
                    ref_rel = set(ref.relationship_ids)
                    if orig_rel != ref_rel:
                        ev_err = f"Evidence relationship mismatch for argument {orig_arg.argument_id}: {orig_rel} vs {ref_rel}"
                        evidence_violations.append(ev_err)
                        violations.append(ev_err)

        is_valid = (
            orphan_count == 0
            and len(lost_elements) == 0
            and len(sequence_violations) == 0
            and len(evidence_violations) == 0
            and len(missing_knowledge_violations) == 0
            and len(duplicated_unit_violations) == 0
            and len(violations) == 0
        )

        return BridgeValidationReport(
            artifact_id=render_artifact.artifact_id,
            artifact_type=render_artifact.artifact_type,
            is_valid=is_valid,
            total_blueprint_elements=len(blueprint_element_ids),
            total_render_units=len(render_artifact.units),
            orphan_render_unit_count=orphan_count,
            lost_blueprint_element_ids=lost_elements,
            sequence_violations=sequence_violations,
            evidence_loss_violations=evidence_violations,
            missing_knowledge_violations=missing_knowledge_violations,
            duplicated_unit_violations=duplicated_unit_violations,
            violations=violations,
        )
