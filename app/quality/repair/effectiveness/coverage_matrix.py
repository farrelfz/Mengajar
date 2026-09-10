"""
Universal Document Intelligence System V5 — Root Cause Coverage Matrix.

Phase 3D.1: Canonical coverage matrix mapping finding codes to defect domains,
root causes, owning layers, and eligible repair strategies.
Guarantees: No silent gaps, zero generic fallback for unmapped findings,
and explicit forensic decomposition for complex defects like SCIENTIFIC_CITATION_INVISIBLE.
"""

from __future__ import annotations

from enum import Enum
from typing import Dict, List, Optional, Sequence, Tuple
from pydantic import BaseModel, ConfigDict

from app.quality.contracts.signals import QualityDomain
from app.quality.repair.contracts import RepairMutationClass
from app.quality.repair.root_cause import RootCauseType


class CitationInvisibleSubtype(str, Enum):
    """Forensic sub-types for invisible or defective scientific citations."""
    CITATION_CLIPPED = "CITATION_CLIPPED"                     # Bounding box truncates citation text
    CITATION_ZERO_SIZE = "CITATION_ZERO_SIZE"                 # Font size or container rendered at 0px/0pt
    CITATION_LOW_CONTRAST = "CITATION_LOW_CONTRAST"           # Font color fails contrast ratio against background
    CITATION_OUTSIDE_VIEWPORT = "CITATION_OUTSIDE_VIEWPORT"   # Citation element coordinates outside page bounds
    CITATION_NOT_RENDERED = "CITATION_NOT_RENDERED"           # Citation in blueprint was dropped by renderer bridge
    CITATION_ANCHOR_MISSING = "CITATION_ANCHOR_MISSING"       # Claim text has no citation anchor in semantic source


class DefectCoverageEntry(BaseModel):
    """Canonical ledger entry in the root cause coverage matrix."""
    model_config = ConfigDict(frozen=True)

    finding_code: str
    artifact_type: str
    domain: QualityDomain
    root_cause: RootCauseType
    owning_layer: str  # R0, R1, R2, R3, R4
    eligible_strategy_ids: Tuple[str, ...]
    is_automatable: bool
    mutation_class: RepairMutationClass
    rationale: str


class RootCauseCoverageMatrix:
    """Master Deterministic Root Cause Coverage Matrix."""

    # Explicit canonical matrix entries
    _ENTRIES: Dict[Tuple[str, str], DefectCoverageEntry] = {
        # ── PRESENTATION DEFECTS ──
        ("ELEMENT_COLLISION", "PRESENTATION"): DefectCoverageEntry(
            finding_code="ELEMENT_COLLISION",
            artifact_type="PRESENTATION",
            domain=QualityDomain.RENDERED,
            root_cause=RootCauseType.GRID_GEOMETRY,
            owning_layer="R1",
            eligible_strategy_ids=("presentation_component_reflow", "presentation_layout_remap"),
            is_automatable=True,
            mutation_class=RepairMutationClass.CLASS_A_GEOMETRY,
            rationale="Conflicting bounding boxes on slide grid; reflow or remap to 2-column canonical layout.",
        ),
        ("OVERLAPPING_CONTENT", "PRESENTATION"): DefectCoverageEntry(
            finding_code="OVERLAPPING_CONTENT",
            artifact_type="PRESENTATION",
            domain=QualityDomain.RENDERED,
            root_cause=RootCauseType.GRID_GEOMETRY,
            owning_layer="R1",
            eligible_strategy_ids=("presentation_component_reflow", "presentation_layout_remap"),
            is_automatable=True,
            mutation_class=RepairMutationClass.CLASS_A_GEOMETRY,
            rationale="Slide visual elements overlap; separate into isolated grid cards.",
        ),
        ("TEXT_CLIPPING", "PRESENTATION"): DefectCoverageEntry(
            finding_code="TEXT_CLIPPING",
            artifact_type="PRESENTATION",
            domain=QualityDomain.RENDERED,
            root_cause=RootCauseType.PADDING_SPACING,
            owning_layer="R0",
            eligible_strategy_ids=("presentation_padding_adjust", "presentation_density_split"),
            is_automatable=True,
            mutation_class=RepairMutationClass.CLASS_A_GEOMETRY,
            rationale="Slide text overflows boundary container; adjust padding or split slide.",
        ),
        ("TEXT_OVERFLOW", "PRESENTATION"): DefectCoverageEntry(
            finding_code="TEXT_OVERFLOW",
            artifact_type="PRESENTATION",
            domain=QualityDomain.RENDERED,
            root_cause=RootCauseType.CONTENT_DENSITY,
            owning_layer="R2",
            eligible_strategy_ids=("presentation_density_split", "presentation_padding_adjust"),
            is_automatable=True,
            mutation_class=RepairMutationClass.CLASS_B_COMPOSITION,
            rationale="Excessive content density causes slide overflow; split into coherent beats.",
        ),
        ("TEXT_TOO_SMALL", "PRESENTATION"): DefectCoverageEntry(
            finding_code="TEXT_TOO_SMALL",
            artifact_type="PRESENTATION",
            domain=QualityDomain.RENDERED,
            root_cause=RootCauseType.TYPOGRAPHY,
            owning_layer="R0",
            eligible_strategy_ids=("presentation_layout_remap", "presentation_density_split"),
            is_automatable=True,
            mutation_class=RepairMutationClass.CLASS_C_LAYOUT_REMAPPING,
            rationale="Font shrunk below 14pt threshold due to density pressure; remap or split.",
        ),
        ("LAYOUT_MONOTONY", "PRESENTATION"): DefectCoverageEntry(
            finding_code="LAYOUT_MONOTONY",
            artifact_type="PRESENTATION",
            domain=QualityDomain.ARTIFACT,
            root_cause=RootCauseType.SEMANTIC_LAYOUT_MAPPING,
            owning_layer="R1",
            eligible_strategy_ids=("presentation_layout_remap",),
            is_automatable=True,
            mutation_class=RepairMutationClass.CLASS_C_LAYOUT_REMAPPING,
            rationale="Identical consecutive slide layouts; rotate to canonical alternating layout.",
        ),

        # ── WORKSHEET DEFECTS ──
        ("REPETITION_STREAK", "WORKSHEET"): DefectCoverageEntry(
            finding_code="REPETITION_STREAK",
            artifact_type="WORKSHEET",
            domain=QualityDomain.ARTIFACT,
            root_cause=RootCauseType.SEMANTIC_LAYOUT_MAPPING,
            owning_layer="R2",
            eligible_strategy_ids=("worksheet_layout_alternation", "worksheet_inquiry_sequence"),
            is_automatable=True,
            mutation_class=RepairMutationClass.CLASS_C_LAYOUT_REMAPPING,
            rationale="Repetitive single-column worksheet tasks; alternate layout or inquiry sequence.",
        ),
        ("ANTI_SPOILING_BREACH", "WORKSHEET"): DefectCoverageEntry(
            finding_code="ANTI_SPOILING_BREACH",
            artifact_type="WORKSHEET",
            domain=QualityDomain.ARTIFACT,
            root_cause=RootCauseType.INQUIRY_STRUCTURE,
            owning_layer="R3",
            eligible_strategy_ids=("worksheet_anti_spoiling",),
            is_automatable=True,
            mutation_class=RepairMutationClass.CLASS_D_PEDAGOGICAL_STRUCTURE,
            rationale="Explanatory answers leaked in prompt text; redact and withhold explanation.",
        ),
        ("TEXT_TOO_SMALL", "WORKSHEET"): DefectCoverageEntry(
            finding_code="TEXT_TOO_SMALL",
            artifact_type="WORKSHEET",
            domain=QualityDomain.RENDERED,
            root_cause=RootCauseType.TYPOGRAPHY,
            owning_layer="R0",
            eligible_strategy_ids=("worksheet_typography_scale",),
            is_automatable=True,
            mutation_class=RepairMutationClass.CLASS_A_GEOMETRY,
            rationale="Font below 11pt educational minimum; scale body font within safe bounds.",
        ),
        ("INSUFFICIENT_WORKSPACE", "WORKSHEET"): DefectCoverageEntry(
            finding_code="INSUFFICIENT_WORKSPACE",
            artifact_type="WORKSHEET",
            domain=QualityDomain.ARTIFACT,
            root_cause=RootCauseType.GRID_GEOMETRY,
            owning_layer="R1",
            eligible_strategy_ids=("worksheet_workspace_expansion",),
            is_automatable=True,
            mutation_class=RepairMutationClass.CLASS_A_GEOMETRY,
            rationale="Student write-in area too small; expand line count or response box height.",
        ),

        # ── SCIENTIFIC DOCUMENT DEFECTS ──
        ("UNSUPPORTED_SCIENTIFIC_CLAIM", "SCIENTIFIC_DOCUMENT"): DefectCoverageEntry(
            finding_code="UNSUPPORTED_SCIENTIFIC_CLAIM",
            artifact_type="SCIENTIFIC_DOCUMENT",
            domain=QualityDomain.SEMANTIC,
            root_cause=RootCauseType.EVIDENCE_MAPPING,
            owning_layer="R3",
            eligible_strategy_ids=("scientific_evidence_mapping", "scientific_claim_downgrade"),
            is_automatable=True,
            mutation_class=RepairMutationClass.CLASS_E_SEMANTIC_INTEGRITY,
            rationale="Claim lacks supporting evidence in knowledge manifest; hedge claim statement.",
        ),
        ("SCIENTIFIC_CITATION_INVISIBLE", "SCIENTIFIC_DOCUMENT"): DefectCoverageEntry(
            finding_code="SCIENTIFIC_CITATION_INVISIBLE",
            artifact_type="SCIENTIFIC_DOCUMENT",
            domain=QualityDomain.RENDERED,
            root_cause=RootCauseType.EVIDENCE_MAPPING,
            owning_layer="R3",
            eligible_strategy_ids=("scientific_citation_linking",),
            is_automatable=True,
            mutation_class=RepairMutationClass.CLASS_E_SEMANTIC_INTEGRITY,
            rationale="Bibliographic citation anchor missing or unlinked; generate reference and anchor.",
        ),
        ("SOURCE_CONTRADICTION", "SCIENTIFIC_DOCUMENT"): DefectCoverageEntry(
            finding_code="SOURCE_CONTRADICTION",
            artifact_type="SCIENTIFIC_DOCUMENT",
            domain=QualityDomain.SEMANTIC,
            root_cause=RootCauseType.SOURCE_INSUFFICIENCY,
            owning_layer="R4",
            eligible_strategy_ids=(),
            is_automatable=False,  # Explicitly non-automatable
            mutation_class=RepairMutationClass.CLASS_F_NON_REPAIRABLE,
            rationale="Contradictory factual source material cannot be autonomously resolved.",
        ),
        ("EXTRACTION_AMBIGUITY", "SCIENTIFIC_DOCUMENT"): DefectCoverageEntry(
            finding_code="EXTRACTION_AMBIGUITY",
            artifact_type="SCIENTIFIC_DOCUMENT",
            domain=QualityDomain.SEMANTIC,
            root_cause=RootCauseType.SOURCE_INSUFFICIENCY,
            owning_layer="R4",
            eligible_strategy_ids=(),
            is_automatable=False,
            mutation_class=RepairMutationClass.CLASS_F_NON_REPAIRABLE,
            rationale="Ambiguous semantic extraction requires human editorial review.",
        ),

        # ── HANDOUT DEFECTS ──
        ("ACCIDENTAL_PAGE", "HANDOUT"): DefectCoverageEntry(
            finding_code="ACCIDENTAL_PAGE",
            artifact_type="HANDOUT",
            domain=QualityDomain.ARTIFACT,
            root_cause=RootCauseType.PAGE_BREAK,
            owning_layer="R2",
            eligible_strategy_ids=("handout_pagination", "handout_density_balance"),
            is_automatable=True,
            mutation_class=RepairMutationClass.CLASS_B_COMPOSITION,
            rationale="Trailing accidental blank/short page; adjust paragraph leading or section breaks.",
        ),
        ("TEXT_OVERFLOW", "HANDOUT"): DefectCoverageEntry(
            finding_code="TEXT_OVERFLOW",
            artifact_type="HANDOUT",
            domain=QualityDomain.RENDERED,
            root_cause=RootCauseType.CONTENT_DENSITY,
            owning_layer="R2",
            eligible_strategy_ids=("handout_density_balance", "handout_pagination"),
            is_automatable=True,
            mutation_class=RepairMutationClass.CLASS_B_COMPOSITION,
            rationale="A4 reading text overflows page budget; balance section density.",
        ),
    }

    @classmethod
    def lookup(cls, finding_code: str, artifact_type: str) -> Optional[DefectCoverageEntry]:
        """Looks up a finding code for a specific artifact type."""
        norm_code = finding_code.strip()
        norm_art = artifact_type.strip().upper()
        return cls._ENTRIES.get((norm_code, norm_art))

    @classmethod
    def classify_citation_invisible_subtype(
        cls,
        evidence: Dict[str, Any],
    ) -> CitationInvisibleSubtype:
        """
        Forensically decomposes SCIENTIFIC_CITATION_INVISIBLE based on physical inspection evidence.
        """
        font_size = evidence.get("font_size", evidence.get("font_size_pt", 10.0))
        contrast_ratio = evidence.get("contrast_ratio", 4.5)
        bbox = evidence.get("bbox", (0, 0, 100, 100))
        page_width = evidence.get("page_width", 595.28)
        page_height = evidence.get("page_height", 841.89)
        anchor_exists = evidence.get("anchor_exists", False)
        is_clipped = evidence.get("is_clipped", False)

        if font_size <= 0.5:
            return CitationInvisibleSubtype.CITATION_ZERO_SIZE
        if contrast_ratio < 2.0:
            return CitationInvisibleSubtype.CITATION_LOW_CONTRAST
        if is_clipped:
            return CitationInvisibleSubtype.CITATION_CLIPPED
        if len(bbox) == 4:
            x0, y0, x1, y1 = bbox
            if x1 > page_width or y1 > page_height or x0 < 0 or y0 < 0:
                return CitationInvisibleSubtype.CITATION_OUTSIDE_VIEWPORT
        if not anchor_exists:
            return CitationInvisibleSubtype.CITATION_ANCHOR_MISSING

        return CitationInvisibleSubtype.CITATION_NOT_RENDERED

    @classmethod
    def resolve_citation_subtype_strategy(
        cls,
        subtype: CitationInvisibleSubtype,
    ) -> Tuple[RootCauseType, str, Tuple[str, ...]]:
        """
        Maps citation invisible subtype to root cause, owning layer, and eligible strategy.
        """
        if subtype == CitationInvisibleSubtype.CITATION_ZERO_SIZE:
            return RootCauseType.TYPOGRAPHY, "R0", ("scientific_citation_linking",)
        elif subtype == CitationInvisibleSubtype.CITATION_LOW_CONTRAST:
            return RootCauseType.PADDING_SPACING, "R0", ("scientific_citation_linking",)
        elif subtype == CitationInvisibleSubtype.CITATION_CLIPPED:
            return RootCauseType.GRID_GEOMETRY, "R1", ("scientific_citation_linking",)
        elif subtype == CitationInvisibleSubtype.CITATION_OUTSIDE_VIEWPORT:
            return RootCauseType.CONTENT_DENSITY, "R2", ("scientific_citation_linking",)
        elif subtype == CitationInvisibleSubtype.CITATION_ANCHOR_MISSING:
            return RootCauseType.EVIDENCE_MAPPING, "R3", ("scientific_citation_linking",)
        else:  # CITATION_NOT_RENDERED
            return RootCauseType.EVIDENCE_MAPPING, "R1", ("scientific_citation_linking",)
