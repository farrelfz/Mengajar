"""
Universal Document Intelligence System V5 — Composition Fingerprint Engine.

Phase 3A: Generates spatial layout fingerprints per page and detects layout monotony,
near-identical page sequences, and composition repetition streaks with contextual justification.
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, ConfigDict, Field

from app.quality.rendered.contracts import CompositionMetrics
from app.quality.rendered.failure_taxonomy import (
    FutureRepairClass,
    RenderedFailureCode,
    RenderedFailureSeverity,
    RenderedQualityFailure,
)


class PageCompositionFingerprint(BaseModel):
    """Spatial layout and element distribution fingerprint for one rendered page."""
    model_config = ConfigDict(frozen=True)

    page_number: int
    quadrants: Tuple[float, float, float, float]  # Q1 (TL), Q2 (TR), Q3 (BL), Q4 (BR)
    text_density: float
    whitespace_ratio: float
    major_blocks_count: int
    aspect_ratio: float = 1.777

    def similarity(self, other: PageCompositionFingerprint) -> float:
        """Calculates cosine similarity of spatial feature vectors (0.0 to 1.0)."""
        v1 = list(self.quadrants) + [self.text_density, self.whitespace_ratio]
        v2 = list(other.quadrants) + [other.text_density, other.whitespace_ratio]

        dot = sum(a * b for a, b in zip(v1, v2))
        norm1 = math.sqrt(sum(a * a for a in v1))
        norm2 = math.sqrt(sum(b * b for b in v2))

        if norm1 <= 1e-6 or norm2 <= 1e-6:
            spatial_sim = 1.0 if norm1 == norm2 else 0.5
        else:
            spatial_sim = max(0.0, min(1.0, dot / (norm1 * norm2)))

        # Block count delta factor
        max_b = max(1, self.major_blocks_count, other.major_blocks_count)
        block_sim = 1.0 - (abs(self.major_blocks_count - other.major_blocks_count) / max_b)

        return round(0.75 * spatial_sim + 0.25 * block_sim, 3)


class RepetitionStreak(BaseModel):
    """Sequence of consecutive pages with high composition similarity."""
    model_config = ConfigDict(frozen=True)

    start_page: int
    end_page: int
    length: int
    mean_similarity: float
    is_justified: bool
    justification_reason: str = ""


class CompositionFingerprintEngine:
    """Analyzes layout diversity and detects monotonous visual repetition streaks."""

    def __init__(
        self,
        streak_similarity_threshold: float = 0.90,
        presentation_max_allowed_streak: int = 3,
        document_max_allowed_streak: int = 5,
    ) -> None:
        self.streak_sim_threshold = streak_similarity_threshold
        self.pres_max_streak = presentation_max_allowed_streak
        self.doc_max_streak = document_max_allowed_streak

    def analyze_fingerprints(
        self,
        fingerprints: List[PageCompositionFingerprint],
        artifact_type: str = "PRESENTATION",
    ) -> Tuple[CompositionMetrics, List[RepetitionStreak], List[RenderedQualityFailure]]:
        n_pages = len(fingerprints)
        if n_pages <= 1:
            return (
                CompositionMetrics(layout_diversity_score=1.0, max_repetition_streak=1),
                [],
                [],
            )

        norm_type = artifact_type.upper()
        max_allowed_streak = (
            self.pres_max_streak if norm_type == "PRESENTATION" else self.doc_max_streak
        )

        streaks: List[RepetitionStreak] = []
        failures: List[RenderedQualityFailure] = []
        pairwise_sims: List[float] = []

        curr_start = 1
        curr_len = 1
        curr_sims: List[float] = []
        near_duplicate_count = 0

        for i in range(n_pages - 1):
            fp1 = fingerprints[i]
            fp2 = fingerprints[i + 1]
            sim = fp1.similarity(fp2)
            pairwise_sims.append(sim)

            if sim >= 0.98:
                near_duplicate_count += 1

            if sim >= self.streak_sim_threshold:
                curr_len += 1
                curr_sims.append(sim)
            else:
                if curr_len > 1:
                    m_sim = sum(curr_sims) / len(curr_sims)
                    # Check contextual justification
                    is_justified = (norm_type in ("HANDOUT", "SCIENTIFIC_DOCUMENT") and curr_len <= max_allowed_streak)
                    just_reason = (
                        "Multi-page document continuous text flow"
                        if is_justified
                        else ("Monotonous slide composition streak" if norm_type == "PRESENTATION" else "")
                    )
                    streaks.append(
                        RepetitionStreak(
                            start_page=curr_start,
                            end_page=curr_start + curr_len - 1,
                            length=curr_len,
                            mean_similarity=round(m_sim, 3),
                            is_justified=is_justified,
                            justification_reason=just_reason,
                        )
                    )
                curr_start = i + 2
                curr_len = 1
                curr_sims = []

        if curr_len > 1:
            m_sim = sum(curr_sims) / len(curr_sims)
            is_justified = (norm_type in ("HANDOUT", "SCIENTIFIC_DOCUMENT") and curr_len <= max_allowed_streak)
            just_reason = (
                "Multi-page document continuous text flow"
                if is_justified
                else ("Monotonous slide composition streak" if norm_type == "PRESENTATION" else "")
            )
            streaks.append(
                RepetitionStreak(
                    start_page=curr_start,
                    end_page=curr_start + curr_len - 1,
                    length=curr_len,
                    mean_similarity=round(m_sim, 3),
                    is_justified=is_justified,
                    justification_reason=just_reason,
                )
            )

        max_streak_len = max((s.length for s in streaks), default=1)
        mean_pairwise_sim = sum(pairwise_sims) / max(1, len(pairwise_sims))
        diversity_score = max(0.10, min(1.0, 1.0 - (mean_pairwise_sim * 0.45)))

        # Evaluate streak failures
        for streak in streaks:
            if not streak.is_justified and streak.length > max_allowed_streak:
                severity = (
                    RenderedFailureSeverity.MAJOR
                    if streak.length >= (max_allowed_streak + 2)
                    else RenderedFailureSeverity.MINOR
                )
                failures.append(
                    RenderedQualityFailure(
                        code=RenderedFailureCode.REPETITION_STREAK,
                        severity=severity,
                        artifact_type=norm_type,
                        page_indices=tuple(range(streak.start_page, streak.end_page + 1)),
                        description=(
                            f"{norm_type}: Layout monotony streak of {streak.length} consecutive pages "
                            f"(pages {streak.start_page}-{streak.end_page}, similarity {streak.mean_similarity:.2f})"
                        ),
                        evidence={
                            "start_page": streak.start_page,
                            "end_page": streak.end_page,
                            "streak_length": streak.length,
                            "mean_similarity": streak.mean_similarity,
                        },
                        recommended_future_repair=FutureRepairClass.CLASS_B_LAYOUT_REMAPPING,
                        repair_guidance="Introduce visual break, two-column variant, or alternating composition.",
                    )
                )

        metrics = CompositionMetrics(
            layout_diversity_score=round(diversity_score, 3),
            max_repetition_streak=max_streak_len,
            near_duplicate_pages_count=near_duplicate_count,
            mean_spatial_similarity=round(mean_pairwise_sim, 3),
        )

        return metrics, streaks, failures
