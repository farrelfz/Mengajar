"""
Universal Document Intelligence System V5 — PDF Geometry Inspector.

Phase 3A: PyMuPDF-based physical display list and bounding box inspector:
- Text clipping outside physical page boundaries
- Tiny text detection with artifact-specific thresholds
- Bounding box element collision
- Page occupancy and quadrant distribution
- Margin consistency and viewport edge proximity
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, ConfigDict, Field

try:
    import pymupdf as fitz
except ImportError:
    import fitz

from app.quality.rendered.contracts import GeometryMetrics
from app.quality.rendered.failure_taxonomy import (
    FutureRepairClass,
    RenderedFailureCode,
    RenderedFailureSeverity,
    RenderedQualityFailure,
)


class PageGeometryAnalysis(BaseModel):
    """Raw vector and bounding box analysis for a single PDF page."""
    model_config = ConfigDict(frozen=True)

    page_number: int
    width: float
    height: float
    page_area: float
    occupied_area: float
    occupancy_ratio: float
    quadrant_occupancies: Tuple[float, float, float, float]  # TL, TR, BL, BR
    margins: Tuple[float, float, float, float]  # Top, Right, Bottom, Left
    text_length: int
    min_font_size: float
    max_font_size: float
    clipping_boxes_count: int
    collision_boxes_count: int
    tiny_text_spans_count: int
    failures: Tuple[RenderedQualityFailure, ...] = Field(default_factory=tuple)


class PDFGeometryInspector:
    """Inspects physical vector geometries of rendered PDF pages."""

    # Artifact-specific minimum body font size thresholds (points)
    MIN_BODY_FONT_THRESHOLDS: Dict[str, float] = {
        "PRESENTATION": 11.0,
        "HANDOUT": 8.5,
        "WORKSHEET": 9.0,
        "SCIENTIFIC_DOCUMENT": 8.0,
    }

    def __init__(self, clip_tolerance_pt: float = 4.0) -> None:
        self.clip_tolerance_pt = clip_tolerance_pt

    def inspect_page(
        self,
        page: fitz.Page,
        page_idx: int,
        artifact_type: str = "PRESENTATION",
    ) -> PageGeometryAnalysis:
        rect = page.rect
        width = rect.width
        height = rect.height
        page_area = max(1.0, width * height)

        norm_type = artifact_type.upper()
        min_font_thresh = self.MIN_BODY_FONT_THRESHOLDS.get(norm_type, 8.5)

        p_dict = page.get_text("dict")
        blocks = p_dict.get("blocks", [])

        occupied_area = 0.0
        tl_area, tr_area, bl_area, br_area = 0.0, 0.0, 0.0, 0.0
        mid_x = width / 2.0
        mid_y = height / 2.0

        min_font = 999.0
        max_font = 0.0
        total_text_len = 0
        tiny_spans = 0
        clipping_count = 0
        collision_count = 0
        failures: List[RenderedQualityFailure] = []

        valid_block_rects: List[fitz.Rect] = []

        # Margin bounding trackers
        min_x0 = width
        min_y0 = height
        max_x1 = 0.0
        max_y1 = 0.0

        for b in blocks:
            bbox = b.get("bbox", (0, 0, 0, 0))
            bx0, by0, bx1, by1 = bbox
            bw = max(0.0, bx1 - bx0)
            bh = max(0.0, by1 - by0)
            b_area = bw * bh

            if b_area <= 0:
                continue

            occupied_area += b_area
            min_x0 = min(min_x0, bx0)
            min_y0 = min(min_y0, by0)
            max_x1 = max(max_x1, bx1)
            max_y1 = max(max_y1, by1)

            # Quadrant distribution
            if bx0 < mid_x and by0 < mid_y:
                tl_area += b_area
            elif bx0 >= mid_x and by0 < mid_y:
                tr_area += b_area
            elif bx0 < mid_x and by0 >= mid_y:
                bl_area += b_area
            else:
                br_area += b_area

            # A. Check text clipping outside viewport
            is_clipped = (
                bx0 < -self.clip_tolerance_pt
                or by0 < -self.clip_tolerance_pt
                or bx1 > (width + self.clip_tolerance_pt)
                or by1 > (height + self.clip_tolerance_pt)
            )
            if is_clipped:
                clipping_count += 1
                failures.append(
                    RenderedQualityFailure(
                        code=RenderedFailureCode.TEXT_CLIPPING,
                        severity=RenderedFailureSeverity.CRITICAL,
                        artifact_type=norm_type,
                        page_indices=(page_idx,),
                        description=(
                            f"Page {page_idx}: Content clipped outside page boundaries "
                            f"[{bx0:.1f}, {by0:.1f}, {bx1:.1f}, {by1:.1f}] vs page [{width:.1f}, {height:.1f}]"
                        ),
                        evidence={"bbox": list(bbox), "page_dims": [width, height]},
                        recommended_future_repair=FutureRepairClass.CLASS_A_GEOMETRY,
                        repair_guidance="Scale viewport content or add auto-flow page breaking.",
                    )
                )

            # B. Extract spans, typography, and text lengths
            if "lines" in b:
                valid_block_rects.append(fitz.Rect(bx0, by0, bx1, by1))
                for line in b["lines"]:
                    for span in line.get("spans", []):
                        s_text = span.get("text", "").strip()
                        s_size = float(span.get("size", 12.0))
                        if not s_text:
                            continue

                        total_text_len += len(s_text)
                        min_font = min(min_font, s_size)
                        max_font = max(max_font, s_size)

                        # C. Detect tiny unreadable text
                        # Exclude header/footer chrome (page number, slide title header, tiny copyright at page edge)
                        is_edge_chrome = (by1 < 48.0 or by0 > (height - 48.0))
                        if s_size < (min_font_thresh - 0.1) and not is_edge_chrome:
                            tiny_spans += 1
                            failures.append(
                                RenderedQualityFailure(
                                    code=RenderedFailureCode.TEXT_TOO_SMALL,
                                    severity=RenderedFailureSeverity.CRITICAL if s_size < (min_font_thresh - 2.5) else RenderedFailureSeverity.MAJOR,
                                    artifact_type=norm_type,
                                    page_indices=(page_idx,),
                                    description=(
                                        f"Page {page_idx}: Text span '{s_text[:25]}' font size {s_size:.1f}pt "
                                        f"below readable threshold {min_font_thresh:.1f}pt"
                                    ),
                                    evidence={"font_size": s_size, "threshold": min_font_thresh, "sample": s_text[:30]},
                                    recommended_future_repair=FutureRepairClass.CLASS_E_TYPOGRAPHY_BALANCE,
                                    repair_guidance=f"Increase minimum font size to >= {min_font_thresh}pt.",
                                )
                            )

        # D. Detect element collision across non-identical text blocks
        n_blocks = len(valid_block_rects)
        for i in range(n_blocks):
            for j in range(i + 1, n_blocks):
                r1 = valid_block_rects[i]
                r2 = valid_block_rects[j]
                # Calculate intersection rectangle
                intersect = r1 & r2
                if not intersect.is_empty:
                    inter_area = intersect.width * intersect.height
                    # Require non-trivial overlap (> 20 sq pt)
                    if inter_area > 20.0:
                        collision_count += 1
                        failures.append(
                            RenderedQualityFailure(
                                code=RenderedFailureCode.ELEMENT_COLLISION,
                                severity=RenderedFailureSeverity.CRITICAL if inter_area > 150.0 else RenderedFailureSeverity.MAJOR,
                                artifact_type=norm_type,
                                page_indices=(page_idx,),
                                description=f"Page {page_idx}: Overlapping element collision ({inter_area:.1f} sq pt overlap)",
                                evidence={"overlap_area": inter_area, "b1": list(r1), "b2": list(r2)},
                                recommended_future_repair=FutureRepairClass.CLASS_A_GEOMETRY,
                                repair_guidance="Separate conflicting elements or adjust container flex margins.",
                            )
                        )

        # Margin calculations
        top_m = max(0.0, min_y0) if min_y0 < height else 0.0
        bottom_m = max(0.0, height - max_y1) if max_y1 > 0 else 0.0
        left_m = max(0.0, min_x0) if min_x0 < width else 0.0
        right_m = max(0.0, width - max_x1) if max_x1 > 0 else 0.0
        margins = (round(top_m, 1), round(right_m, 1), round(bottom_m, 1), round(left_m, 1))

        occ_ratio = min(1.0, occupied_area / page_area)
        q_occ = (
            round(tl_area / page_area, 3),
            round(tr_area / page_area, 3),
            round(bl_area / page_area, 3),
            round(br_area / page_area, 3),
        )

        return PageGeometryAnalysis(
            page_number=page_idx,
            width=round(width, 1),
            height=round(height, 1),
            page_area=round(page_area, 1),
            occupied_area=round(occupied_area, 1),
            occupancy_ratio=round(occ_ratio, 3),
            quadrant_occupancies=q_occ,
            margins=margins,
            text_length=total_text_len,
            min_font_size=round(min_font if min_font < 990 else 12.0, 1),
            max_font_size=round(max_font if max_font > 0 else 12.0, 1),
            clipping_boxes_count=clipping_count,
            collision_boxes_count=collision_count,
            tiny_text_spans_count=tiny_spans,
            failures=tuple(failures),
        )

    def inspect_document(
        self,
        pdf_path: Path,
        artifact_type: str = "PRESENTATION",
    ) -> Tuple[GeometryMetrics, List[PageGeometryAnalysis], List[RenderedQualityFailure]]:
        """Inspects all pages in a rendered PDF and aggregates geometry metrics."""
        if not pdf_path.exists():
            raise FileNotFoundError(f"Rendered PDF does not exist: {pdf_path}")

        page_analyses: List[PageGeometryAnalysis] = []
        all_failures: List[RenderedQualityFailure] = []

        total_clipping = 0
        total_overflow = 0
        total_tiny = 0
        total_collisions = 0
        all_margins: List[float] = []
        all_min_fonts: List[float] = []
        all_max_fonts: List[float] = []

        with fitz.open(pdf_path) as doc:
            for idx, page in enumerate(doc, start=1):
                p_analysis = self.inspect_page(page, idx, artifact_type=artifact_type)
                page_analyses.append(p_analysis)
                all_failures.extend(p_analysis.failures)

                total_clipping += p_analysis.clipping_boxes_count
                total_tiny += p_analysis.tiny_text_spans_count
                total_collisions += p_analysis.collision_boxes_count
                all_margins.extend(p_analysis.margins)
                all_min_fonts.append(p_analysis.min_font_size)
                all_max_fonts.append(p_analysis.max_font_size)

        mean_margin = sum(all_margins) / max(1, len(all_margins))
        margin_var = (
            sum((m - mean_margin) ** 2 for m in all_margins) / max(1, len(all_margins))
            if all_margins
            else 0.0
        )

        metrics = GeometryMetrics(
            text_clipping_instances=total_clipping,
            page_overflow_instances=total_overflow,
            tiny_text_spans_count=total_tiny,
            element_collision_count=total_collisions,
            mean_margin_pt=round(mean_margin, 2),
            margin_variance=round(margin_var, 2),
            min_observed_font_size=min(all_min_fonts) if all_min_fonts else 12.0,
            max_observed_font_size=max(all_max_fonts) if all_max_fonts else 12.0,
        )

        return metrics, page_analyses, all_failures
