"""
Universal Document Intelligence System V5 — Rendered Output Failure Taxonomy.

Phase 3A: Rigorous taxonomy for physical rendered output failures, severities,
and future repair recommendations (Phase 3B/3C repair classes).
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Tuple
from pydantic import BaseModel, ConfigDict, Field


class RenderedFailureSeverity(str, Enum):
    """Severity classification for rendered artifact inspection issues."""
    CRITICAL = "CRITICAL"   # Catastrophic failure: text clipping, answer leakage, missing pages
    MAJOR = "MAJOR"         # Severe design flaw: quiz collapse, unreadable font, massive repetition
    MINOR = "MINOR"         # Mild suboptimal issue: slight imbalance, minor spacing variance
    INFO = "INFO"           # Informational diagnostic


class FutureRepairClass(str, Enum):
    """Repair recommendation categories for Phase 3B/3C automated repair engine."""
    CLASS_A_GEOMETRY = "CLASS_A_GEOMETRY"                     # Viewport scaling, margins, box bounds
    CLASS_B_LAYOUT_REMAPPING = "CLASS_B_LAYOUT_REMAPPING"     # Remap layout family (e.g. cards -> timeline)
    CLASS_C_PAGINATION_PACING = "CLASS_C_PAGINATION_PACING"   # Split slides, insert page break, re-chunk
    CLASS_D_SEMANTIC_REFINEMENT = "CLASS_D_SEMANTIC_REFINEMENT"# Withhold answers, re-link citations, scaffold inquiry
    CLASS_E_TYPOGRAPHY_BALANCE = "CLASS_E_TYPOGRAPHY_BALANCE" # Adjust type scale, leading, font sizes
    NONE = "NONE"


class RenderedFailureCode(str, Enum):
    """Machine-readable failure codes for rendered output inspection."""
    # Geometry & Viewport
    RENDER_GEOMETRY_FAILURE = "RENDER_GEOMETRY_FAILURE"
    TEXT_CLIPPING = "TEXT_CLIPPING"
    TEXT_TOO_SMALL = "TEXT_TOO_SMALL"
    ELEMENT_COLLISION = "ELEMENT_COLLISION"
    PAGE_BOUNDARY_VIOLATION = "PAGE_BOUNDARY_VIOLATION"
    MARGIN_INCONSISTENCY = "MARGIN_INCONSISTENCY"
    BLANK_PAGE = "BLANK_PAGE"

    # Hierarchy & Typography
    VISUAL_HIERARCHY_FAILURE = "VISUAL_HIERARCHY_FAILURE"
    HEADLINE_BODY_COLLAPSE = "HEADLINE_BODY_COLLAPSE"
    INCONSISTENT_HEADING_SCALE = "INCONSISTENT_HEADING_SCALE"

    # Density & Whitespace
    DENSITY_OVERLOAD = "DENSITY_OVERLOAD"
    SUSPICIOUS_VOID = "SUSPICIOUS_VOID"
    DENSITY_IMBALANCE = "DENSITY_IMBALANCE"

    # Composition & Repetition
    LAYOUT_MONOTONY = "LAYOUT_MONOTONY"
    DUPLICATE_COMPOSITION = "DUPLICATE_COMPOSITION"
    REPETITION_STREAK = "REPETITION_STREAK"
    CARD_OVERLOAD = "CARD_OVERLOAD"

    # Handout-Specific
    HANDOUT_READING_FLOW_FAILURE = "HANDOUT_READING_FLOW_FAILURE"
    HANDOUT_FRAGMENTATION = "HANDOUT_FRAGMENTATION"
    HANDOUT_WALL_OF_TEXT = "HANDOUT_WALL_OF_TEXT"
    ORPHAN_HEADING = "ORPHAN_HEADING"
    TABLE_SPLIT_WITHOUT_HEADER = "TABLE_SPLIT_WITHOUT_HEADER"

    # Worksheet-Specific
    WORKSHEET_QUIZ_COLLAPSE = "WORKSHEET_QUIZ_COLLAPSE"
    WORKSHEET_WORKSPACE_INSUFFICIENT = "WORKSHEET_WORKSPACE_INSUFFICIENT"
    WORKSHEET_WORKSPACE_MISSING = "WORKSHEET_WORKSPACE_MISSING"
    WORKSHEET_SPOILING_FAILURE = "WORKSHEET_SPOILING_FAILURE"
    WORKSHEET_INQUIRY_DEGRADED = "WORKSHEET_INQUIRY_DEGRADED"

    # Scientific Document-Specific
    SCIENTIFIC_HIERARCHY_FAILURE = "SCIENTIFIC_HIERARCHY_FAILURE"
    SCIENTIFIC_EVIDENCE_DETACHED = "SCIENTIFIC_EVIDENCE_DETACHED"
    SCIENTIFIC_CITATION_INVISIBLE = "SCIENTIFIC_CITATION_INVISIBLE"
    SCIENTIFIC_ARGUMENT_SPARSITY = "SCIENTIFIC_ARGUMENT_SPARSITY"
    SCIENTIFIC_CHAPTER_IMBALANCE = "SCIENTIFIC_CHAPTER_IMBALANCE"


class RenderedQualityFailure(BaseModel):
    """Structured, machine-readable diagnostic defect detected in rendered output."""
    model_config = ConfigDict(frozen=True)

    code: RenderedFailureCode
    severity: RenderedFailureSeverity
    artifact_type: str
    page_indices: Tuple[int, ...] = Field(default_factory=tuple)
    description: str
    evidence: Dict[str, Any] = Field(default_factory=dict)
    recommended_future_repair: FutureRepairClass = FutureRepairClass.NONE
    repair_guidance: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "code": self.code.value,
            "severity": self.severity.value,
            "artifact_type": self.artifact_type,
            "page_indices": list(self.page_indices),
            "description": self.description,
            "evidence": self.evidence,
            "recommended_future_repair": self.recommended_future_repair.value,
            "repair_guidance": self.repair_guidance,
        }
