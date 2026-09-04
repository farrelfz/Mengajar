"""
Physical Format & Geometry Integrity Evaluator.

Inspects rendered physical PDF page counts, point dimensions, aspect ratios,
and margin safety invariants.
"""

from __future__ import annotations

from pathlib import Path
import pymupdf

from app.formats import get_format
from app.quality.contracts import (
    QualityDimension,
    QualityFinding,
    QualityMetric,
    QualitySeverity,
)


class FormatEvaluator:
    """Evaluates physical rendered artifact geometry against format contracts."""

    @staticmethod
    def evaluate(
        pdf_path: str | Path | None,
        target_format: str = "a4_portrait",
        expected_page_count: int | None = None,
    ) -> tuple[list[QualityMetric], list[QualityFinding]]:
        metrics: list[QualityMetric] = []
        findings: list[QualityFinding] = []

        # If pdf_path is None, evaluation is progressive (Blueprint or Composition stage)
        if pdf_path is None:
            return metrics, findings

        path_obj = Path(pdf_path)
        if not path_obj.exists():
            findings.append(
                QualityFinding(
                    dimension=QualityDimension.FORMAT_INTEGRITY,
                    severity=QualitySeverity.CRITICAL,
                    finding="Physical PDF artifact was not generated or path does not exist.",
                    evidence={"pdf_path": str(pdf_path)},
                    score_impact=-1.0,
                    recommendation="Ensure MasterRenderEngine and headless browser complete successfully.",
                )
            )
            metrics.append(
                QualityMetric(
                    name="physical_pdf_existence",
                    dimension=QualityDimension.FORMAT_INTEGRITY,
                    score=0.0,
                    weight=2.0,
                    raw_value=False,
                )
            )
            return metrics, findings

        doc = pymupdf.open(str(pdf_path))
        page_count = len(doc)

        if page_count == 0:
            doc.close()
            findings.append(
                QualityFinding(
                    dimension=QualityDimension.FORMAT_INTEGRITY,
                    severity=QualitySeverity.CRITICAL,
                    finding="Rendered PDF is empty (0 pages).",
                    evidence={"page_count": 0},
                    score_impact=-1.0,
                    recommendation="Inspect HTML assembler output for rendering blockers.",
                )
            )
            metrics.append(
                QualityMetric(
                    name="physical_page_count_validity",
                    dimension=QualityDimension.FORMAT_INTEGRITY,
                    score=0.0,
                    weight=2.0,
                    raw_value=0,
                )
            )
            return metrics, findings

        # Check geometry on first page
        page1 = doc[0]
        rect = page1.rect
        width_pt, height_pt = rect.width, rect.height
        doc.close()

        fmt = get_format(target_format)
        expected_w, expected_h = fmt.width_pt, fmt.height_pt

        # Allow 2pt tolerance due to rounding
        w_diff = abs(width_pt - expected_w)
        h_diff = abs(height_pt - expected_h)

        is_geometry_valid = w_diff <= 2.0 and h_diff <= 2.0
        score = 1.0

        if not is_geometry_valid:
            # If deviation is major (e.g. orientation inverted), flag CRITICAL
            is_major_mismatch = w_diff > 50.0 or h_diff > 50.0
            sev = QualitySeverity.CRITICAL if is_major_mismatch else QualitySeverity.ERROR
            score = 0.0 if is_major_mismatch else 0.5
            findings.append(
                QualityFinding(
                    dimension=QualityDimension.FORMAT_INTEGRITY,
                    severity=sev,
                    finding=f"PDF physical dimensions ({width_pt:.1f}x{height_pt:.1f} pt) deviate from contract ({expected_w:.1f}x{expected_h:.1f} pt).",
                    evidence={"actual": [width_pt, height_pt], "expected": [expected_w, expected_h]},
                    score_impact=-1.0 if is_major_mismatch else -0.5,
                    recommendation="Ensure MasterRenderEngine uses matching format CSS geometry tokens.",
                )
            )

        # Check page count against expected composition
        if expected_page_count is not None and expected_page_count > 0:
            if page_count != expected_page_count:
                score = min(score, 0.6)
                findings.append(
                    QualityFinding(
                        dimension=QualityDimension.FORMAT_INTEGRITY,
                        severity=QualitySeverity.WARNING,
                        finding=f"Rendered PDF page count ({page_count}) diverges from composition page allocation ({expected_page_count}).",
                        evidence={"actual_pages": page_count, "expected_pages": expected_page_count},
                        score_impact=-0.2,
                        recommendation="Check for CSS overflow or premature page breaks causing unintended pagination.",
                    )
                )

        metrics.append(
            QualityMetric(
                name="physical_geometry_conformance",
                dimension=QualityDimension.FORMAT_INTEGRITY,
                score=score,
                weight=1.5,
                raw_value=[width_pt, height_pt],
                details={"expected": [expected_w, expected_h], "page_count": page_count},
            )
        )

        return metrics, findings
