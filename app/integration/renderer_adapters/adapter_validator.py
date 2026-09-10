"""
Universal Knowledge Core — Adapter Traceability Validator & Fragmentation Risk Analyzer.

Phase 2A Controlled Renderer Adapter Integration:
- Part 8: AdapterTraceabilityValidator validates the full traceability graph between
  RenderArtifact contracts and legacy intermediate representations.
- Part 9: FragmentationRiskAnalyzer detects pathological 1:1 mechanical mappings
  and micro-fragmentation without performing automatic or semantic merging.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Set, Tuple
from pydantic import BaseModel, ConfigDict, Field

from app.integration.artifact_bridge.contracts import RenderArtifact, RenderUnit
from app.integration.renderer_adapters.contracts import (
    DocumentContent,
    LegacyPresentationDeck,
    LegacyScientificDocument,
    LegacyWorksheetDocument,
    SlideBlueprint,
)


class AdapterValidationReport(BaseModel):
    """Validation outcome emitted by AdapterTraceabilityValidator."""
    model_config = ConfigDict(frozen=True)

    artifact_id: str
    artifact_type: str
    is_valid: bool
    total_render_units: int
    total_legacy_objects: int
    mapped_source_count: int
    dropped_source_count: int
    orphan_legacy_objects: Tuple[str, ...] = Field(default_factory=tuple)
    dropped_source_ids: Tuple[str, ...] = Field(default_factory=tuple)
    evidence_loss_violations: Tuple[str, ...] = Field(default_factory=tuple)
    activity_type_violations: Tuple[str, ...] = Field(default_factory=tuple)
    sequence_violations: Tuple[str, ...] = Field(default_factory=tuple)
    duplicated_content_violations: Tuple[str, ...] = Field(default_factory=tuple)
    violations: Tuple[str, ...] = Field(default_factory=tuple)


class FragmentationRiskReport(BaseModel):
    """Fragmentation risk analysis outcome emitted by FragmentationRiskAnalyzer."""
    model_config = ConfigDict(frozen=True)

    artifact_type: str
    is_pathological: bool
    risk_score: float = Field(ge=0.0, le=1.0)
    input_unit_count: int
    output_object_count: int
    ratio: float
    warnings: Tuple[str, ...] = Field(default_factory=tuple)
    metrics: Dict[str, Any] = Field(default_factory=dict)


class AdapterTraceabilityValidator:
    """Enforces bidirectional traceability and structural survival across adapter boundaries."""

    def validate(
        self,
        render_artifact: RenderArtifact,
        legacy_model: Any,
    ) -> AdapterValidationReport:
        """Validates that legacy model fully traces back to input RenderArtifact."""
        violations: List[str] = []
        orphan_objects: List[str] = []
        dropped_sources: List[str] = []
        evidence_violations: List[str] = []
        activity_type_violations: List[str] = []
        sequence_violations: List[str] = []
        duplicated_violations: List[str] = []

        # 1. Collect all expected source element IDs and knowledge units from RenderArtifact
        expected_bp_ids: Set[str] = {
            u.traceability_refs.blueprint_element_id for u in render_artifact.units
        }
        expected_unit_ids: Set[str] = {u.unit_id for u in render_artifact.units}

        mapped_bp_ids: Set[str] = set()
        total_legacy_objects = 0

        # 2. Extract legacy objects and their source mappings based on model type
        if isinstance(legacy_model, LegacyPresentationDeck):
            total_legacy_objects = len(legacy_model.slides)
            last_slide_num = 0

            for slide in legacy_model.slides:
                # Sequence validation: strictly ascending slide numbers
                if slide.slide_number <= last_slide_num:
                    seq_err = (
                        f"Presentation sequence broken: slide {slide.slide_id} "
                        f"has number {slide.slide_number} <= previous {last_slide_num}."
                    )
                    sequence_violations.append(seq_err)
                    violations.append(seq_err)
                last_slide_num = slide.slide_number

                # Orphan detection: slide with no source element IDs
                if not slide.source_element_ids:
                    orphan_err = f"Orphan slide detected: {slide.slide_id} has no source_element_ids."
                    orphan_objects.append(slide.slide_id)
                    violations.append(orphan_err)

                # Traceability check: each source element ID must exist in RenderArtifact
                for bp_id in slide.source_element_ids:
                    if bp_id not in expected_bp_ids:
                        orphan_err = (
                            f"Slide {slide.slide_id} references unknown source blueprint element '{bp_id}'."
                        )
                        orphan_objects.append(slide.slide_id)
                        violations.append(orphan_err)
                    mapped_bp_ids.add(bp_id)

        elif isinstance(legacy_model, DocumentContent):
            total_legacy_objects = len(legacy_model.sections)
            last_seq = 0

            for sec in legacy_model.sections:
                if sec.sequence_index <= last_seq:
                    seq_err = (
                        f"Handout sequence broken: section {sec.section_id} "
                        f"has index {sec.sequence_index} <= previous {last_seq}."
                    )
                    sequence_violations.append(seq_err)
                    violations.append(seq_err)
                last_seq = sec.sequence_index

                if not sec.source_element_ids:
                    orphan_err = f"Orphan handout section: {sec.section_id} has no source_element_ids."
                    orphan_objects.append(sec.section_id)
                    violations.append(orphan_err)

                for bp_id in sec.source_element_ids:
                    if bp_id not in expected_bp_ids:
                        orphan_err = (
                            f"Section {sec.section_id} references unknown blueprint element '{bp_id}'."
                        )
                        orphan_objects.append(sec.section_id)
                        violations.append(orphan_err)
                    mapped_bp_ids.add(bp_id)

        elif isinstance(legacy_model, LegacyWorksheetDocument):
            total_legacy_objects = len(legacy_model.sections)
            seen_activities: Set[str] = set()

            for sec in legacy_model.sections:
                if not sec.source_element_ids:
                    orphan_err = f"Orphan worksheet section: {sec.section_id} has no source_element_ids."
                    orphan_objects.append(sec.section_id)
                    violations.append(orphan_err)

                for act in sec.activities:
                    # Activity type survival check: must remain typed and NOT generic paragraph
                    if not act.activity_type or act.activity_type in ("paragraph", "generic_text", "PROSE"):
                        act_err = f"Worksheet activity '{act.activity_id}' flattened to generic text!"
                        activity_type_violations.append(act_err)
                        violations.append(act_err)

                    # Duplication check
                    if act.activity_id in seen_activities:
                        dup_err = f"Duplicate activity detected in worksheet: {act.activity_id}"
                        duplicated_violations.append(dup_err)
                        violations.append(dup_err)
                    seen_activities.add(act.activity_id)

                    for bp_id in act.source_element_ids:
                        if bp_id not in expected_bp_ids:
                            orphan_err = f"Activity {act.activity_id} references unknown blueprint element '{bp_id}'."
                            orphan_objects.append(act.activity_id)
                            violations.append(orphan_err)
                        mapped_bp_ids.add(bp_id)

        elif isinstance(legacy_model, LegacyScientificDocument):
            # Collect all relationship IDs in render artifact
            expected_rel_ids: Set[str] = set()
            for u in render_artifact.units:
                rels = u.semantic_metadata.get("evidence_relationship_ids", ())
                expected_rel_ids.update(rels)

            survived_rel_ids: Set[str] = set()
            for bab in legacy_model.babs:
                total_legacy_objects += len(bab.subsections)
                for subsec in bab.subsections:
                    if not subsec.source_element_ids:
                        orphan_err = f"Orphan scientific subsection: {subsec.subsection_id} has no sources."
                        orphan_objects.append(subsec.subsection_id)
                        violations.append(orphan_err)

                    for bp_id in subsec.source_element_ids:
                        if bp_id not in expected_bp_ids:
                            orphan_err = f"Subsection {subsec.subsection_id} references unknown source '{bp_id}'."
                            orphan_objects.append(subsec.subsection_id)
                            violations.append(orphan_err)
                        mapped_bp_ids.add(bp_id)

                    survived_rel_ids.update(subsec.relationship_ids)

            # Evidence relationship survival check
            missing_rels = expected_rel_ids - survived_rel_ids
            if missing_rels:
                ev_err = f"Scientific evidence relationship loss detected: {missing_rels}"
                evidence_violations.append(ev_err)
                violations.append(ev_err)

        else:
            violations.append(f"Unrecognized legacy model type '{type(legacy_model).__name__}'.")

        # 3. Check for silently dropped RenderUnits (source completeness)
        dropped = expected_bp_ids - mapped_bp_ids
        if dropped:
            for d in dropped:
                dropped_sources.append(d)
                violations.append(f"Silently dropped RenderUnit source element detected: {d}")

        is_valid = len(violations) == 0

        return AdapterValidationReport(
            artifact_id=render_artifact.artifact_id,
            artifact_type=render_artifact.artifact_type,
            is_valid=is_valid,
            total_render_units=len(render_artifact.units),
            total_legacy_objects=total_legacy_objects,
            mapped_source_count=len(mapped_bp_ids),
            dropped_source_count=len(dropped),
            orphan_legacy_objects=tuple(orphan_objects),
            dropped_source_ids=tuple(dropped_sources),
            evidence_loss_violations=tuple(evidence_violations),
            activity_type_violations=tuple(activity_type_violations),
            sequence_violations=tuple(sequence_violations),
            duplicated_content_violations=tuple(duplicated_violations),
            violations=tuple(violations),
        )


class FragmentationRiskAnalyzer:
    """Detects pathological mappings, micro-fragmentation, and mechanical 1:1 allocations."""

    def analyze_presentation(
        self,
        legacy_deck: LegacyPresentationDeck,
        render_artifact: RenderArtifact,
    ) -> FragmentationRiskReport:
        """Analyzes presentation deck for mechanical 1:1 mapping and low cognitive density."""
        beat_count = len(render_artifact.units)
        slide_count = len(legacy_deck.slides)
        ratio = round(slide_count / beat_count, 3) if beat_count else 0.0

        warnings: List[str] = []
        is_pathological = False
        risk_score = 0.0

        # Mechanical 1:1 mapping detection:
        # If > 15 beats and exactly 100% 1:1 mapped without any grouping
        if beat_count > 15 and ratio == 1.0:
            risk_score = 0.85
            is_pathological = True
            warnings.append(
                f"High risk of mechanical presentation mapping: {beat_count} beats mapped 1-to-1 "
                f"to {slide_count} slides without grouping opportunities considered."
            )
        elif ratio > 0.8 and beat_count > 20:
            risk_score = 0.60
            warnings.append(
                f"Moderate slide bloat risk: {slide_count} slides for {beat_count} conceptual beats."
            )

        return FragmentationRiskReport(
            artifact_type="PRESENTATION",
            is_pathological=is_pathological,
            risk_score=risk_score,
            input_unit_count=beat_count,
            output_object_count=slide_count,
            ratio=ratio,
            warnings=tuple(warnings),
            metrics={
                "beat_count": beat_count,
                "slide_count": slide_count,
                "ratio": ratio,
                "layout_distribution": legacy_deck.layout_distribution,
            },
        )

    def analyze_worksheet(
        self,
        legacy_doc: LegacyWorksheetDocument,
        render_artifact: RenderArtifact,
    ) -> FragmentationRiskReport:
        """Analyzes worksheet document for micro-activity fragmentation."""
        act_count = len(render_artifact.units)
        sec_count = len(legacy_doc.sections)
        ratio = round(sec_count / act_count, 3) if act_count else 0.0

        warnings: List[str] = []
        is_pathological = False
        risk_score = 0.0

        # Micro-activity fragmentation: > 30 activities with 1:1 section mapping
        if act_count > 30 and ratio >= 0.9:
            risk_score = 0.90
            is_pathological = True
            warnings.append(
                f"High risk of micro-activity fragmentation: {act_count} activities isolated in "
                f"{sec_count} sections without pedagogical grouping."
            )
        elif act_count > 25 and ratio > 0.6:
            risk_score = 0.50
            warnings.append(
                f"Moderate activity fragmentation: {act_count} activities across {sec_count} sections."
            )

        return FragmentationRiskReport(
            artifact_type="WORKSHEET",
            is_pathological=is_pathological,
            risk_score=risk_score,
            input_unit_count=act_count,
            output_object_count=sec_count,
            ratio=ratio,
            warnings=tuple(warnings),
            metrics={
                "activity_count": act_count,
                "section_count": sec_count,
                "activities_per_section_avg": round(act_count / sec_count, 2) if sec_count else 0,
            },
        )

    def analyze_scientific(
        self,
        legacy_doc: LegacyScientificDocument,
        render_artifact: RenderArtifact,
    ) -> FragmentationRiskReport:
        """Analyzes scientific document for micro-argument fragmentation."""
        arg_count = len(render_artifact.units)
        subsec_count = sum(len(b.subsections) for b in legacy_doc.babs)
        ratio = round(subsec_count / arg_count, 3) if arg_count else 0.0

        warnings: List[str] = []
        is_pathological = False
        risk_score = 0.0

        # Micro-argument fragmentation: > 30 argument units with 1:1 subsection mapping
        if arg_count > 30 and ratio >= 0.9:
            risk_score = 0.90
            is_pathological = True
            warnings.append(
                f"High risk of micro-argument fragmentation: {arg_count} argument units isolated in "
                f"{subsec_count} subsections without analytical synthesis."
            )
        elif arg_count > 25 and ratio > 0.6:
            risk_score = 0.50
            warnings.append(
                f"Moderate argument fragmentation: {arg_count} arguments across {subsec_count} subsections."
            )

        return FragmentationRiskReport(
            artifact_type="SCIENTIFIC_DOCUMENT",
            is_pathological=is_pathological,
            risk_score=risk_score,
            input_unit_count=arg_count,
            output_object_count=subsec_count,
            ratio=ratio,
            warnings=tuple(warnings),
            metrics={
                "argument_count": arg_count,
                "subsection_count": subsec_count,
                "arguments_per_subsection_avg": round(arg_count / subsec_count, 2) if subsec_count else 0,
                "unsupported_claims_count": len(legacy_doc.unsupported_claims_flagged),
            },
        )
