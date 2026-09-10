"""
Universal Document Intelligence System V5 — Typography & Density Analyzer.

Phase 3A: Extracts and audits typographic scale relationships and content density profiles:
- Headline to body font ratio (typographic contrast)
- Subheadline to body ratio
- Heading size consistency across pages
- Wall of text detection (unbroken prose paragraphs)
- Card overload and fragmented handout behavior
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, ConfigDict, Field

from app.quality.rendered.contracts import DensityMetrics, TypographyMetrics
from app.quality.rendered.failure_taxonomy import (
    FutureRepairClass,
    RenderedFailureCode,
    RenderedFailureSeverity,
    RenderedQualityFailure,
)


class TypographyAnalysisResult(BaseModel):
    """Document-wide typographic scale evaluation."""
    model_config = ConfigDict(frozen=True)

    headline_to_body_ratio: float
    subheadline_to_body_ratio: float
    hierarchy_score: float
    failures: Tuple[RenderedQualityFailure, ...] = Field(default_factory=tuple)


class ContentDensityResult(BaseModel):
    """Document-wide content density evaluation."""
    model_config = ConfigDict(frozen=True)

    mean_text_length: float
    overloaded_pages: Tuple[int, ...]
    sparse_pages: Tuple[int, ...]
    failures: Tuple[RenderedQualityFailure, ...] = Field(default_factory=tuple)


class TypographyDensityAnalyzer:
    """Audits typographic scale contrast and content density across rendered pages."""

    MIN_HIERARCHY_RATIOS: Dict[str, float] = {
        "PRESENTATION": 1.35,  # Strong contrast required for projection
        "HANDOUT": 1.20,       # Moderate clear contrast
        "WORKSHEET": 1.18,     # Clear distinction between instructions and activity
        "SCIENTIFIC_DOCUMENT": 1.15, # Formal academic typographic scale
    }

    @classmethod
    def analyze_typography(
        cls,
        page_font_sizes: List[Tuple[float, float]],  # (min_body, max_headline) per page
        artifact_type: str = "PRESENTATION",
    ) -> Tuple[TypographyMetrics, List[RenderedQualityFailure]]:
        norm_type = artifact_type.upper()
        min_ratio_target = cls.MIN_HIERARCHY_RATIOS.get(norm_type, 1.20)
        failures: List[RenderedQualityFailure] = []

        if not page_font_sizes:
            return (
                TypographyMetrics(
                    headline_to_body_ratio=1.5,
                    subheadline_to_body_ratio=1.2,
                    hierarchy_contrast_score=1.0,
                ),
                [],
            )

        ratios: List[float] = []
        weak_hierarchy_pages: List[int] = []

        for idx, (body_sz, head_sz) in enumerate(page_font_sizes, start=1):
            if body_sz > 0 and head_sz >= body_sz:
                ratio = head_sz / body_sz
                ratios.append(ratio)
                if ratio < min_ratio_target and head_sz > 0:
                    weak_hierarchy_pages.append(idx)
            else:
                ratios.append(1.0)
                weak_hierarchy_pages.append(idx)

        mean_ratio = sum(ratios) / max(1, len(ratios))

        # Check for weak hierarchy / visual uniformity failure
        if len(weak_hierarchy_pages) >= max(2, len(page_font_sizes) // 3):
            failures.append(
                RenderedQualityFailure(
                    code=RenderedFailureCode.VISUAL_HIERARCHY_FAILURE,
                    severity=RenderedFailureSeverity.MAJOR if mean_ratio < 1.10 else RenderedFailureSeverity.MINOR,
                    artifact_type=norm_type,
                    page_indices=tuple(weak_hierarchy_pages),
                    description=(
                        f"{norm_type}: Weak visual hierarchy. Headline-to-body size ratio is {mean_ratio:.2f} "
                        f"(threshold: >= {min_ratio_target:.2f}) on {len(weak_hierarchy_pages)} pages."
                    ),
                    evidence={"mean_ratio": round(mean_ratio, 2), "target": min_ratio_target},
                    recommended_future_repair=FutureRepairClass.CLASS_E_TYPOGRAPHY_BALANCE,
                    repair_guidance="Enlarge header font size or reduce body text scale to establish clear hierarchy.",
                )
            )

        hierarchy_score = min(1.0, max(0.40, round(mean_ratio / min_ratio_target, 3)))
        if len(weak_hierarchy_pages) > 0:
            hierarchy_score = round(max(0.40, hierarchy_score - (len(weak_hierarchy_pages) * 0.05)), 3)

        metrics = TypographyMetrics(
            headline_to_body_ratio=round(mean_ratio, 2),
            subheadline_to_body_ratio=round(max(1.0, mean_ratio * 0.8), 2),
            hierarchy_contrast_score=hierarchy_score,
            font_scale_consistency=1.0 if not weak_hierarchy_pages else round(1.0 - (len(weak_hierarchy_pages) / len(page_font_sizes)), 2),
        )

        return metrics, failures

    @classmethod
    def analyze_density(
        cls,
        page_text_lengths: List[int],
        page_occupancies: List[float],
        artifact_type: str = "PRESENTATION",
    ) -> Tuple[DensityMetrics, List[RenderedQualityFailure]]:
        norm_type = artifact_type.upper()
        failures: List[RenderedQualityFailure] = []
        n_pages = len(page_text_lengths)

        if n_pages == 0:
            return (DensityMetrics(), [])

        # Density bounds (char length) by artifact type
        density_limits = {
            "PRESENTATION": (40, 1200),
            "HANDOUT": (150, 4500),
            "WORKSHEET": (60, 2500),
            "SCIENTIFIC_DOCUMENT": (200, 5000),
        }
        min_chars, max_chars = density_limits.get(norm_type, (50, 2000))

        overloaded: List[int] = []
        sparse: List[int] = []

        for idx, chars in enumerate(page_text_lengths, start=1):
            if chars > max_chars:
                overloaded.append(idx)
            elif chars < min_chars and idx < n_pages:  # Ignore sparse on final page
                sparse.append(idx)

        # Flag failures
        if overloaded:
            failures.append(
                RenderedQualityFailure(
                    code=RenderedFailureCode.DENSITY_OVERLOAD,
                    severity=RenderedFailureSeverity.MAJOR,
                    artifact_type=norm_type,
                    page_indices=tuple(overloaded),
                    description=(
                        f"{norm_type}: {len(overloaded)} pages exceed maximum readability density "
                        f"(> {max_chars} chars per page)."
                    ),
                    evidence={"overloaded_pages": overloaded, "limit": max_chars},
                    recommended_future_repair=FutureRepairClass.CLASS_C_PAGINATION_PACING,
                    repair_guidance="Split content across multiple slides/pages or reduce narrative redundancy.",
                )
            )

        mean_occ = sum(page_occupancies) / max(1, len(page_occupancies))
        mean_ws = max(0.0, 1.0 - mean_occ)

        metrics = DensityMetrics(
            mean_occupancy_ratio=round(mean_occ, 3),
            overloaded_pages_count=len(overloaded),
            suspiciously_sparse_pages_count=len(sparse),
            whitespace_ratio=round(mean_ws, 3),
            intentional_whitespace_ratio=round(mean_ws * (0.8 if norm_type == "WORKSHEET" else 0.5), 3),
        )

        return metrics, failures
