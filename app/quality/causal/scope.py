"""
Universal Document Intelligence System V5 — Failure Scope and Policy Contract.

Phase 3A.2 Hardening & Phase 3B: Artifact-aware failure scope resolution supporting
Presentation, Handout, Worksheet, and Scientific Document layouts, with explicit
global invariant semantic overrides.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Optional, Sequence, Set


class FailureScope(str, Enum):
    """Spatial and structural breadth of a failure across an artifact."""
    LOCAL = "LOCAL"                 # Isolated to 1-2 non-consecutive pages/elements (<= 15%)
    CLUSTER = "CLUSTER"             # Consecutive streak of pages (e.g. 3-5 slides/sections)
    SYSTEMIC = "SYSTEMIC"           # Distributed recurring defect across multiple pages (>= 20% and < 50%)
    ARTIFACT_WIDE = "ARTIFACT_WIDE" # Document-global or majority-level failure (>= 50% or global invariant)


class ScopePolicy:
    """Artifact-aware scope evaluator with configurable, calibrated thresholds and semantic overrides."""

    GLOBAL_INVARIANT_CODES: Set[str] = {
        "SCIENTIFIC_CITATION_INVISIBLE",
        "SCIENTIFIC_HIERARCHY_FAILURE",
        "WORKSHEET_QUIZ_COLLAPSE",
        "WORKSHEET_SPOILING_FAILURE",
        "PRESENTATION_HANDOUT_COLLAPSE",
        "TRACEABILITY_BREAK",
        "EVIDENCE_DISCIPLINE_FAILURE",
        "METADATA_CORRUPTION",
        "PDF_CONFORMANCE_VIOLATION",
        "GLOBAL_CONFIGURATION_FAILURE",
        "STYLE_SYSTEM_FAILURE",
        "DOCUMENT_STRUCTURE_FAILURE",
    }

    def __init__(
        self,
        local_threshold: float = 0.15,
        cluster_consecutive_min: int = 3,
        systemic_threshold: float = 0.50,
        artifact_wide_threshold: float = 0.50,
        artifact_type: Optional[str] = None,
    ):
        self.local_threshold = local_threshold
        self.cluster_consecutive_min = cluster_consecutive_min
        self.systemic_threshold = systemic_threshold
        self.artifact_wide_threshold = artifact_wide_threshold
        self.artifact_type = artifact_type

        # Calibrated defaults per artifact format if explicitly set
        if artifact_type == "PRESENTATION":
            self.cluster_consecutive_min = cluster_consecutive_min or 3
        elif artifact_type in ("HANDOUT", "WORKSHEET", "SCIENTIFIC_DOCUMENT"):
            self.cluster_consecutive_min = cluster_consecutive_min or 2

    @classmethod
    def is_global_invariant_code(cls, code: Any) -> bool:
        """Returns True if code represents an inherent document-level global defect."""
        if not code:
            return False
        code_str = code.value if hasattr(code, "value") else str(code)
        return code_str in cls.GLOBAL_INVARIANT_CODES or any(
            inv in code_str for inv in ("CITATION_INVISIBLE", "SPOILING", "GLOBAL", "METADATA_CORRUPTION")
        )

    @classmethod
    def for_artifact(cls, artifact_type: str) -> ScopePolicy:
        """Factory for an artifact-calibrated ScopePolicy."""
        type_norm = artifact_type.upper()
        if type_norm == "PRESENTATION":
            return cls(local_threshold=0.15, cluster_consecutive_min=3, systemic_threshold=0.50, artifact_type=type_norm)
        elif type_norm in ("HANDOUT", "SCIENTIFIC_DOCUMENT"):
            return cls(local_threshold=0.15, cluster_consecutive_min=2, systemic_threshold=0.50, artifact_type=type_norm)
        elif type_norm == "WORKSHEET":
            return cls(local_threshold=0.20, cluster_consecutive_min=2, systemic_threshold=0.50, artifact_type=type_norm)
        return cls(local_threshold=0.15, cluster_consecutive_min=3, systemic_threshold=0.50, artifact_type=type_norm)

    def determine_scope(
        self,
        affected_pages: Sequence[int],
        total_pages: int,
        is_document_level: bool = False,
        is_global_invariant: bool = False,
        failure_code: Optional[Any] = None,
        artifact_type: Optional[str] = None,
    ) -> FailureScope:
        """Calculates canonical failure scope based on affected pages, span, and document traits."""
        # Semantic overrides: document-global failures unconditionally evaluate to ARTIFACT_WIDE
        if is_document_level or is_global_invariant or self.is_global_invariant_code(failure_code):
            return FailureScope.ARTIFACT_WIDE

        if not affected_pages or total_pages <= 0:
            return FailureScope.LOCAL

        unique_pages = sorted(set(affected_pages))
        ratio = len(unique_pages) / total_pages

        # Check for consecutive streak
        max_streak = self._find_max_consecutive_streak(unique_pages)
        cluster_threshold = self.cluster_consecutive_min

        # 1. Systemic defect check (> 50% pages affected or >= systemic_threshold)
        if ratio > self.systemic_threshold:
            return FailureScope.SYSTEMIC

        # 2. Cluster defect check (streak of consecutive pages)
        if max_streak >= cluster_threshold:
            return FailureScope.CLUSTER

        # 3. Local defect check (isolated within local threshold and no long streak)
        if ratio <= self.local_threshold:
            return FailureScope.LOCAL

        # 4. Intermediate non-consecutive pages
        if len(unique_pages) > 2:
            return FailureScope.CLUSTER

        return FailureScope.LOCAL

    @staticmethod
    def _find_max_consecutive_streak(pages: Sequence[int]) -> int:
        """Finds length of longest contiguous sequence of page indices."""
        if not pages:
            return 0
        max_streak = 1
        current_streak = 1
        for i in range(1, len(pages)):
            if pages[i] == pages[i - 1] + 1:
                current_streak += 1
                if current_streak > max_streak:
                    max_streak = current_streak
            else:
                current_streak = 1
        return max_streak
