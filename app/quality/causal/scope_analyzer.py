"""
Universal Document Intelligence System V5 — Failure Scope Analyzer.

Phase 3A.1: Classifies the operational breadth of defects across an artifact:
LOCAL, CLUSTER, SYSTEMIC, or ARTIFACT_WIDE.
"""

from __future__ import annotations

from typing import Tuple
from app.quality.causal.taxonomy import CanonicalFailureCode, FailureScope


class ScopeAnalyzer:
    """Analyzes the page distribution of failures to determine structural scope."""

    ARTIFACT_WIDE_CODES = {
        CanonicalFailureCode.SCIENTIFIC_CITATION_INVISIBLE,
        CanonicalFailureCode.SCIENTIFIC_HIERARCHY_FAILURE,
        CanonicalFailureCode.WORKSHEET_QUIZ_COLLAPSE,
        CanonicalFailureCode.PRESENTATION_HANDOUT_COLLAPSE,
        CanonicalFailureCode.TRACEABILITY_BREAK,
        CanonicalFailureCode.EVIDENCE_DISCIPLINE_FAILURE,
    }

    @classmethod
    def analyze_scope(
        cls,
        affected_pages: Tuple[int, ...],
        total_pages: int,
        failure_code: CanonicalFailureCode | None = None,
    ) -> FailureScope:
        # 1. Structural artifact-wide codes
        if failure_code in cls.ARTIFACT_WIDE_CODES:
            return FailureScope.ARTIFACT_WIDE

        count = len(affected_pages)
        if count == 0:
            return FailureScope.LOCAL

        ratio = count / max(1, total_pages)

        # 2. Majority of pages -> SYSTEMIC
        if ratio > 0.50 or (total_pages > 2 and count >= (total_pages - 1)):
            return FailureScope.SYSTEMIC

        # 3. Check for consecutive sequence -> CLUSTER
        if count >= 3:
            sorted_p = sorted(affected_pages)
            is_consecutive = all(sorted_p[i + 1] == sorted_p[i] + 1 for i in range(len(sorted_p) - 1))
            if is_consecutive:
                return FailureScope.CLUSTER

        # 4. Isolated pages (1-2 pages or <= 15% of pages)
        if count <= 2 or ratio <= 0.15:
            return FailureScope.LOCAL

        # Fallback for moderate non-consecutive
        return FailureScope.CLUSTER if count >= 3 else FailureScope.LOCAL
