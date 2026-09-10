"""
Universal Document Intelligence System V5 — Worksheet Pedagogical Diversity Analyzer.

Phase 4: Forensics engine evaluating the pedagogical variety and inquiry distribution
of worksheets, distinguishing legitimate table continuations from pathological monotony.
"""

from __future__ import annotations

from collections import Counter
from typing import Any, Dict, List, Optional, Sequence, Tuple
from pydantic import BaseModel, ConfigDict, Field


class PedagogicalDiversityReport(BaseModel):
    """Authoritative audit report on worksheet pedagogical variety."""
    model_config = ConfigDict(frozen=True)

    total_activities: int
    activity_type_counts: Dict[str, int]
    inquiry_stages_present: Tuple[str, ...]
    shannon_entropy: float
    max_consecutive_identical: int
    is_pathological_monotony: bool
    is_legitimate_continuation: bool
    recommendations: Tuple[str, ...] = Field(default_factory=tuple)


class WorksheetPedagogicalDiversityAnalyzer:
    """Analyzes worksheet blueprints to assess pedagogical variety and monotony risk."""

    @classmethod
    def analyze(
        cls,
        blueprint: Any,
        max_allowed_consecutive: int = 3,
    ) -> PedagogicalDiversityReport:
        activities = getattr(blueprint, "activities", ())
        if not activities:
            return PedagogicalDiversityReport(
                total_activities=0,
                activity_type_counts={},
                inquiry_stages_present=(),
                shannon_entropy=0.0,
                max_consecutive_identical=0,
                is_pathological_monotony=False,
                is_legitimate_continuation=False,
                recommendations=("No activities found in blueprint.",),
            )

        types = [
            getattr(a.activity_type, "value", str(a.activity_type))
            for a in activities
        ]
        counts = dict(Counter(types))
        total = len(types)

        # Calculate Shannon entropy: H = -sum(p * log2(p))
        import math
        entropy = 0.0
        for cnt in counts.values():
            p = cnt / total
            if p > 0:
                entropy -= p * math.log2(p)

        # Detect consecutive streaks
        max_streak = 1
        cur_streak = 1
        for i in range(1, total):
            if types[i] == types[i - 1]:
                cur_streak += 1
                max_streak = max(max_streak, cur_streak)
            else:
                cur_streak = 1

        is_pathological = max_streak > max_allowed_consecutive and len(counts) <= 2
        # Legitimate continuation: repeated OBSERVATION tables or INVESTIGATION steps
        is_legitimate = max_streak > max_allowed_consecutive and all(
            t in ("OBSERVATION", "INVESTIGATION", "DATA_ANALYSIS")
            for t in types[:max_streak]
        )

        recs: List[str] = []
        if is_pathological:
            recs.append(
                f"Pathological streak of {max_streak} identical '{types[0]}' activities detected. "
                "Recompose into structured inquiry arc."
            )
        if len(counts) < 4 and total >= 6:
            recs.append("Inquiry distribution is narrow. Introduce prediction, observation, and reflection stages.")

        return PedagogicalDiversityReport(
            total_activities=total,
            activity_type_counts=counts,
            inquiry_stages_present=tuple(sorted(counts.keys())),
            shannon_entropy=round(entropy, 3),
            max_consecutive_identical=max_streak,
            is_pathological_monotony=is_pathological and not is_legitimate,
            is_legitimate_continuation=is_legitimate,
            recommendations=tuple(recs),
        )
