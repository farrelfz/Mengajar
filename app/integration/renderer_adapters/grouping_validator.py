"""
Universal Knowledge Core — Semantic Grouping Quality Validator.

Phase 2B Controlled Renderer Execution & Artifact Fidelity:
Validates that Many-to-One grouping across all four artifacts is structurally and
semantically justified rather than mechanical fixed-size chunking.

Zero AI calls. Zero keyword matching. Zero semantic inference.
Enforces explicit metadata compatibility, inquiry semantics, and academic integrity.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Set, Tuple
from pydantic import BaseModel, ConfigDict, Field

from app.integration.artifact_bridge.contracts import RenderArtifact, RenderUnit
from app.integration.renderer_adapters.contracts import (
    DocumentContent,
    GroupingDecisionTrace,
    LegacyPresentationDeck,
    LegacyScientificDocument,
    LegacyWorksheetDocument,
)

# Valid inquiry stage transitions in worksheets
INQUIRY_FORWARD_ORDER = {
    "PHENOMENON": 1,
    "PREDICTION": 2,
    "QUESTION": 2,
    "OBSERVATION": 3,
    "INVESTIGATION": 4,
    "DATA_ANALYSIS": 5,
    "REFLECTION": 6,
}


class GroupingQualityReport(BaseModel):
    """Validation outcome emitted by SemanticGroupingQualityValidator."""
    model_config = ConfigDict(frozen=True)

    artifact_type: str
    is_valid: bool
    total_groups: int
    total_sources: int
    arbitrary_grouping_detected: bool
    compatibility_violations: Tuple[str, ...] = Field(default_factory=tuple)
    continuity_violations: Tuple[str, ...] = Field(default_factory=tuple)
    capacity_violations: Tuple[str, ...] = Field(default_factory=tuple)
    decision_traces: Tuple[GroupingDecisionTrace, ...] = Field(default_factory=tuple)
    violations: Tuple[str, ...] = Field(default_factory=tuple)


class SemanticGroupingQualityValidator:
    """Validates structural coherence, pedagogical progression, and audit traces of groupings."""

    def validate_presentation_grouping(
        self,
        legacy_deck: LegacyPresentationDeck,
        render_artifact: RenderArtifact,
    ) -> GroupingQualityReport:
        """Validates that presentation slides group beats by narrative segment, not raw count."""
        violations: List[str] = []
        compat_violations: List[str] = []
        continuity_violations: List[str] = []
        capacity_violations: List[str] = []
        arbitrary_detected = False

        unit_map = {u.traceability_refs.blueprint_element_id: u for u in render_artifact.units}

        for slide in legacy_deck.slides:
            sources = [unit_map[sid] for sid in slide.source_element_ids if sid in unit_map]
            if len(sources) <= 1:
                continue

            # 1. Check narrative function compatibility
            first_fn = sources[0].semantic_metadata.get("narrative_function")
            for s in sources[1:]:
                fn = s.semantic_metadata.get("narrative_function")
                if fn != first_fn:
                    err = (
                        f"Incompatible narrative grouping on slide {slide.slide_id}: "
                        f"{first_fn} grouped with {fn} without structural justification."
                    )
                    compat_violations.append(err)
                    violations.append(err)

            # 2. Check progressive sequence continuity
            for i in range(len(sources) - 1):
                curr_idx = sources[i].sequence_index
                next_idx = sources[i + 1].sequence_index
                if next_idx != curr_idx + 1:
                    err = (
                        f"Sequence break in slide {slide.slide_id}: beat sequence jumped "
                        f"from {curr_idx} to {next_idx}."
                    )
                    continuity_violations.append(err)
                    violations.append(err)

            # 3. Check cognitive load capacity
            total_load = sum(
                float(s.semantic_metadata.get("cognitive_load_target", 0.5)) for s in sources
            )
            if total_load > 1.8:
                err = f"Cognitive overload on slide {slide.slide_id}: total load {total_load:.2f} > 1.8."
                capacity_violations.append(err)
                violations.append(err)

        # 4. Check for arbitrary count-based chunking signature
        # If all grouped slides have identical group sizes without decision traces
        group_sizes = [len(s.source_element_ids) for s in legacy_deck.slides if len(s.source_element_ids) > 1]
        if group_sizes and len(set(group_sizes)) == 1 and not legacy_deck.grouping_decision_traces:
            arbitrary_detected = True
            violations.append("Arbitrary count-based presentation grouping detected without decision traces.")

        is_valid = len(violations) == 0

        return GroupingQualityReport(
            artifact_type="PRESENTATION",
            is_valid=is_valid,
            total_groups=len(legacy_deck.slides),
            total_sources=sum(len(s.source_element_ids) for s in legacy_deck.slides),
            arbitrary_grouping_detected=arbitrary_detected,
            compatibility_violations=tuple(compat_violations),
            continuity_violations=tuple(continuity_violations),
            capacity_violations=tuple(capacity_violations),
            decision_traces=legacy_deck.grouping_decision_traces,
            violations=tuple(violations),
        )

    def validate_worksheet_grouping(
        self,
        legacy_doc: LegacyWorksheetDocument,
        render_artifact: RenderArtifact,
    ) -> GroupingQualityReport:
        """Validates inquiry phase continuity and anti-spoiling in worksheet sections."""
        violations: List[str] = []
        compat_violations: List[str] = []
        continuity_violations: List[str] = []
        capacity_violations: List[str] = []
        arbitrary_detected = False

        for sec in legacy_doc.sections:
            activities = sec.activities
            if len(activities) <= 1:
                continue

            # 1. Validate inquiry order (e.g. PREDICTION must not follow REFLECTION)
            for i in range(len(activities) - 1):
                t1 = activities[i].activity_type
                t2 = activities[i + 1].activity_type
                o1 = INQUIRY_FORWARD_ORDER.get(t1, 0)
                o2 = INQUIRY_FORWARD_ORDER.get(t2, 0)

                if o1 > 0 and o2 > 0 and o2 < o1:
                    err = (
                        f"Inquiry order regression in worksheet section {sec.section_id}: "
                        f"{t2} (stage {o2}) grouped after {t1} (stage {o1})."
                    )
                    continuity_violations.append(err)
                    violations.append(err)

            # 2. Validate withholding policy in all grouped activities
            for a in activities:
                if not a.withhold_explanation:
                    err = f"Withhold explanation violated in activity {a.activity_id} in {sec.section_id}."
                    compat_violations.append(err)
                    violations.append(err)

            # 3. Check section capacity
            if len(activities) > 4:
                err = f"Excessive activity density in section {sec.section_id}: {len(activities)} activities > 4."
                capacity_violations.append(err)
                violations.append(err)

        # 4. Check for arbitrary fixed-size chunking signature
        sec_sizes = [len(s.activities) for s in legacy_doc.sections]
        if sec_sizes and len(set(sec_sizes)) == 1 and not legacy_doc.grouping_decision_traces:
            arbitrary_detected = True
            violations.append("Arbitrary fixed-size worksheet chunking detected without decision traces.")

        is_valid = len(violations) == 0

        return GroupingQualityReport(
            artifact_type="WORKSHEET",
            is_valid=is_valid,
            total_groups=len(legacy_doc.sections),
            total_sources=sum(len(s.activities) for s in legacy_doc.sections),
            arbitrary_grouping_detected=arbitrary_detected,
            compatibility_violations=tuple(compat_violations),
            continuity_violations=tuple(continuity_violations),
            capacity_violations=tuple(capacity_violations),
            decision_traces=legacy_doc.grouping_decision_traces,
            violations=tuple(violations),
        )

    def validate_scientific_grouping(
        self,
        legacy_doc: LegacyScientificDocument,
        render_artifact: RenderArtifact,
    ) -> GroupingQualityReport:
        """Validates academic consistency, chapter integrity, and evidence preservation in KTI subsections."""
        violations: List[str] = []
        compat_violations: List[str] = []
        continuity_violations: List[str] = []
        capacity_violations: List[str] = []
        arbitrary_detected = False

        for bab in legacy_doc.babs:
            for sub in bab.subsections:
                if len(sub.argument_ids) <= 1:
                    continue

                # 1. Validate that unsupported empirical claims are not mixed with supported findings without marker
                if sub.unsupported_claims and sub.evidence_ids:
                    # Mixed unsupported and supported in same subsection without isolation
                    if not sub.limitations:
                        err = (
                            f"Integrity violation in subsection {sub.subsection_id}: unsupported claims "
                            f"mixed with empirical evidence without limitation demarcation."
                        )
                        compat_violations.append(err)
                        violations.append(err)

                # 2. Check subsection argument capacity
                if len(sub.argument_ids) > 5:
                    err = f"Subsection {sub.subsection_id} exceeds capacity: {len(sub.argument_ids)} arguments > 5."
                    capacity_violations.append(err)
                    violations.append(err)

        # 3. Check for arbitrary argument chunking signature
        sub_sizes = [
            len(s.argument_ids)
            for b in legacy_doc.babs
            for s in b.subsections
            if len(s.argument_ids) > 1
        ]
        if sub_sizes and len(set(sub_sizes)) == 1 and not legacy_doc.grouping_decision_traces:
            arbitrary_detected = True
            violations.append("Arbitrary argument chunking detected in scientific document without decision traces.")

        is_valid = len(violations) == 0

        return GroupingQualityReport(
            artifact_type="SCIENTIFIC_DOCUMENT",
            is_valid=is_valid,
            total_groups=sum(len(b.subsections) for b in legacy_doc.babs),
            total_sources=legacy_doc.total_arguments,
            arbitrary_grouping_detected=arbitrary_detected,
            compatibility_violations=tuple(compat_violations),
            continuity_violations=tuple(continuity_violations),
            capacity_violations=tuple(capacity_violations),
            decision_traces=legacy_doc.grouping_decision_traces,
            violations=tuple(violations),
        )

    def validate_handout_grouping(
        self,
        legacy_doc: DocumentContent,
        render_artifact: RenderArtifact,
    ) -> GroupingQualityReport:
        """Validates heading hierarchy, reading flow, and definition attachment in handouts."""
        violations: List[str] = []
        compat_violations: List[str] = []
        continuity_violations: List[str] = []
        capacity_violations: List[str] = []

        last_level = 1
        for sec in legacy_doc.sections:
            # 1. Hierarchy inversion check (level cannot jump from 1 to 3 or 4 directly)
            if sec.level > last_level + 1 and last_level > 0:
                err = f"Heading hierarchy inversion in section {sec.section_id}: level jumped from {last_level} to {sec.level}."
                continuity_violations.append(err)
                violations.append(err)
            last_level = sec.level

            # 2. Reading flow: empty section check
            if not sec.content and not sec.definitions and not sec.examples:
                err = f"Empty reading section detected: {sec.section_id} has no body text or callouts."
                compat_violations.append(err)
                violations.append(err)

        is_valid = len(violations) == 0

        return GroupingQualityReport(
            artifact_type="HANDOUT",
            is_valid=is_valid,
            total_groups=len(legacy_doc.sections),
            total_sources=sum(len(s.source_element_ids) for s in legacy_doc.sections),
            arbitrary_grouping_detected=False,
            compatibility_violations=tuple(compat_violations),
            continuity_violations=tuple(continuity_violations),
            capacity_violations=tuple(capacity_violations),
            decision_traces=legacy_doc.grouping_decision_traces,
            violations=tuple(violations),
        )
