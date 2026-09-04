"""
Information Density Evaluator.

Analyzes text volume, character counts per slide, paragraph lengths,
and visual-to-text density balance across page regions.
"""

from __future__ import annotations

import re
from typing import Any
from app.composition.schemas import DocumentComposition, PageComposition
from app.quality.contracts import (
    QualityDimension,
    QualityFinding,
    QualityMetric,
    QualitySeverity,
)


def _strip_html(raw: str) -> str:
    """Strips HTML/SVG tags to accurately measure human-readable text density."""
    clean = re.sub(r"<[^>]+>", " ", raw)
    return " ".join(clean.split())


class DensityEvaluator:
    """Evaluates whether content density is appropriate for the target format."""

    @staticmethod
    def evaluate(
        composition: DocumentComposition | None,
        target_format: str = "a4_portrait",
    ) -> tuple[list[QualityMetric], list[QualityFinding]]:
        metrics: list[QualityMetric] = []
        findings: list[QualityFinding] = []

        if not composition or not composition.pages:
            return metrics, findings

        is_presentation = "16_9" in target_format or "presentation" in target_format
        max_slide_chars = 1200 if is_presentation else 3500

        total_chars = 0
        overdense_pages = []

        for page in composition.pages:
            page_chars = 0
            for region in page.regions.values():
                for block in region.blocks:
                    if block.raw_content:
                        content_str = block.raw_content
                    elif block.rendered_html:
                        content_str = _strip_html(block.rendered_html)
                    else:
                        content_str = ""
                    page_chars += len(content_str)

            total_chars += page_chars

            if is_presentation and page_chars > max_slide_chars:
                overdense_pages.append((page.page_number, page_chars))
                findings.append(
                    QualityFinding(
                        dimension=QualityDimension.INFORMATION_DENSITY,
                        severity=QualitySeverity.WARNING if page_chars < 1800 else QualitySeverity.ERROR,
                        finding=f"Slide {page.page_number} contains excessive textual density ({page_chars} chars, max recommended {max_slide_chars}).",
                        evidence={"page_number": page.page_number, "char_count": page_chars, "limit": max_slide_chars},
                        affected_section=f"Page {page.page_number}",
                        score_impact=-0.25,
                        recommendation="Split the explanation across multiple slides or replace dense text with visual progression cards.",
                    )
                )

        avg_page_chars = total_chars / max(1, len(composition.pages))
        density_score = 1.0 - min(1.0, len(overdense_pages) * 0.3)

        metrics.append(
            QualityMetric(
                name="textual_density_balance",
                dimension=QualityDimension.INFORMATION_DENSITY,
                score=max(0.0, density_score),
                weight=1.2,
                raw_value=avg_page_chars,
                details={"overdense_pages": overdense_pages, "avg_chars_per_page": avg_page_chars},
            )
        )

        return metrics, findings
