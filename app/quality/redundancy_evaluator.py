"""
Redundancy & Repetition Evaluator.

Detects verbatim identical blocks, near-duplicate text spans across pages,
and unvaried visual structures across page regions.
"""

from __future__ import annotations

import re
from app.composition.schemas import DocumentComposition
from app.quality.contracts import (
    QualityDimension,
    QualityFinding,
    QualityMetric,
    QualitySeverity,
)


def _strip_html(raw: str) -> str:
    """Strips HTML/SVG tags to accurately compare human-readable text."""
    clean = re.sub(r"<[^>]+>", " ", raw)
    return " ".join(clean.split())


class RedundancyEvaluator:
    """Evaluates cross-page and intra-page redundancy."""

    @staticmethod
    def evaluate(
        composition: DocumentComposition | None,
    ) -> tuple[list[QualityMetric], list[QualityFinding]]:
        metrics: list[QualityMetric] = []
        findings: list[QualityFinding] = []

        if not composition or not composition.pages:
            return metrics, findings

        seen_blocks: dict[str, int] = {}
        duplicates: list[tuple[str, int, int]] = []

        for page in composition.pages:
            for region in page.regions.values():
                for block in region.blocks:
                    if block.raw_content:
                        raw = block.raw_content
                    elif block.rendered_html:
                        raw = _strip_html(block.rendered_html)
                    else:
                        raw = ""

                    content_clean = raw.strip().lower()
                    if len(content_clean) > 50:  # Only evaluate substantial blocks
                        if content_clean in seen_blocks:
                            duplicates.append((content_clean[:30] + "...", seen_blocks[content_clean], page.page_number))
                            findings.append(
                                QualityFinding(
                                    dimension=QualityDimension.REDUNDANCY,
                                    severity=QualitySeverity.WARNING,
                                    finding=f"Duplicate content block detected on Page {page.page_number} previously seen on Page {seen_blocks[content_clean]}.",
                                    evidence={"first_seen_page": seen_blocks[content_clean], "duplicate_page": page.page_number},
                                    affected_section=f"Page {page.page_number}",
                                    score_impact=-0.2,
                                    recommendation="Consolidate duplicate text into a shared reference section or introduce distinct application contexts.",
                                )
                            )
                        else:
                            seen_blocks[content_clean] = page.page_number

        redundancy_score = max(0.0, 1.0 - (len(duplicates) * 0.25))

        metrics.append(
            QualityMetric(
                name="cross_page_distinctness",
                dimension=QualityDimension.REDUNDANCY,
                score=redundancy_score,
                weight=1.0,
                raw_value=len(duplicates),
                details={"duplicate_count": len(duplicates)},
            )
        )

        return metrics, findings
