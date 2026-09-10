"""
Universal Document Intelligence System V5 — Raster Image Quality Inspector.

Phase 3A: Deterministic computer vision and image statistics analysis
using PyMuPDF raster pixmaps and Pillow:
- Non-background visual density
- Blank region ratio and completely blank page detection
- Edge density (high-frequency visual contour detail)
- Visual balance (left/right & top/bottom optical equilibrium)
- Spatial quadrant luminance distribution
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, ConfigDict, Field
from PIL import Image, ImageFilter, ImageStat

try:
    import pymupdf as fitz
except ImportError:
    import fitz

from app.quality.rendered.contracts import RasterMetrics
from app.quality.rendered.failure_taxonomy import (
    FutureRepairClass,
    RenderedFailureCode,
    RenderedFailureSeverity,
    RenderedQualityFailure,
)


class PageRasterAnalysis(BaseModel):
    """Deterministic visual raster metrics for a single rendered page."""
    model_config = ConfigDict(frozen=True)

    page_number: int
    visual_density: float
    blank_ratio: float
    edge_density: float
    visual_balance_score: float
    quadrant_densities: Tuple[float, float, float, float]  # TL, TR, BL, BR
    is_blank: bool
    failures: Tuple[RenderedQualityFailure, ...] = Field(default_factory=tuple)


class RasterImageInspector:
    """Inspects rendered page raster images using deterministic pixel statistics."""

    def __init__(self, dpi: int = 72) -> None:
        self.dpi = dpi

    def inspect_pixmap(
        self,
        pix: fitz.Pixmap,
        page_idx: int,
        artifact_type: str = "PRESENTATION",
    ) -> PageRasterAnalysis:
        norm_type = artifact_type.upper()
        failures: List[RenderedQualityFailure] = []

        # Convert pixmap to Pillow grayscale image
        img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples).convert("L")
        w, h = img.size
        total_pixels = max(1, w * h)

        # 1. Determine background luminance from border pixels
        border_pixels: List[int] = []
        # Sample top and bottom borders
        for x in range(0, w, max(1, w // 20)):
            border_pixels.append(img.getpixel((x, 0)))
            border_pixels.append(img.getpixel((x, h - 1)))
        for y in range(0, h, max(1, h // 20)):
            border_pixels.append(img.getpixel((0, y)))
            border_pixels.append(img.getpixel((w - 1, y)))

        median_bg = sorted(border_pixels)[len(border_pixels) // 2] if border_pixels else 255
        is_dark_theme = median_bg < 128

        # 2. Thresholding: non-background foreground pixels
        # If light background: pixel < (median_bg - 20) is foreground
        # If dark background: pixel > (median_bg + 20) is foreground
        diff_threshold = 20
        pixels = list(img.get_flattened_data()) if hasattr(img, "get_flattened_data") else list(img.getdata())

        if is_dark_theme:
            fg_mask = [1 if p > (median_bg + diff_threshold) else 0 for p in pixels]
        else:
            fg_mask = [1 if p < (median_bg - diff_threshold) else 0 for p in pixels]

        fg_count = sum(fg_mask)
        visual_density = round(fg_count / total_pixels, 3)

        # 3. Blank page detection
        is_blank = (fg_count == 0) or (visual_density < 0.0005)
        if is_blank:
            failures.append(
                RenderedQualityFailure(
                    code=RenderedFailureCode.BLANK_PAGE,
                    severity=RenderedFailureSeverity.CRITICAL,
                    artifact_type=norm_type,
                    page_indices=(page_idx,),
                    description=f"Page {page_idx}: Completely blank rendered page (visual density {visual_density:.4f})",
                    evidence={"visual_density": visual_density, "is_dark_theme": is_dark_theme},
                    recommended_future_repair=FutureRepairClass.CLASS_C_PAGINATION_PACING,
                    repair_guidance="Eliminate unnecessary page break or supply missing content blocks.",
                )
            )

        # 4. Quadrant spatial density distribution
        mid_x = w // 2
        mid_y = h // 2
        tl_fg, tr_fg, bl_fg, br_fg = 0, 0, 0, 0
        quad_area = max(1, mid_x * mid_y)

        for y in range(h):
            row_offset = y * w
            is_top = (y < mid_y)
            for x in range(w):
                if fg_mask[row_offset + x]:
                    if x < mid_x and is_top:
                        tl_fg += 1
                    elif x >= mid_x and is_top:
                        tr_fg += 1
                    elif x < mid_x and not is_top:
                        bl_fg += 1
                    else:
                        br_fg += 1

        quad_densities = (
            round(tl_fg / quad_area, 3),
            round(tr_fg / quad_area, 3),
            round(bl_fg / quad_area, 3),
            round(br_fg / quad_area, 3),
        )

        # 5. Visual balance score (Left vs Right, Top vs Bottom)
        left_fg = tl_fg + bl_fg
        right_fg = tr_fg + br_fg
        lr_balance = 1.0 - (abs(left_fg - right_fg) / max(1, left_fg + right_fg)) if (left_fg + right_fg) > 0 else 1.0

        top_fg = tl_fg + tr_fg
        bottom_fg = bl_fg + br_fg
        tb_balance = 1.0 - (abs(top_fg - bottom_fg) / max(1, top_fg + bottom_fg)) if (top_fg + bottom_fg) > 0 else 1.0

        visual_balance = round(0.6 * lr_balance + 0.4 * tb_balance, 3)

        # 6. Edge density using FIND_EDGES filter
        edge_img = img.filter(ImageFilter.FIND_EDGES)
        edge_pixels = list(edge_img.get_flattened_data()) if hasattr(edge_img, "get_flattened_data") else list(edge_img.getdata())
        edge_count = sum(1 for ep in edge_pixels if ep > 40)
        edge_density = round(edge_count / total_pixels, 3)

        # Blank ratio: 1.0 - visual_density
        blank_ratio = round(max(0.0, 1.0 - visual_density), 3)

        return PageRasterAnalysis(
            page_number=page_idx,
            visual_density=visual_density,
            blank_ratio=blank_ratio,
            edge_density=edge_density,
            visual_balance_score=visual_balance,
            quadrant_densities=quad_densities,
            is_blank=is_blank,
            failures=tuple(failures),
        )

    def inspect_document(
        self,
        pdf_path: Path,
        artifact_type: str = "PRESENTATION",
    ) -> Tuple[RasterMetrics, List[PageRasterAnalysis], List[RenderedQualityFailure]]:
        if not pdf_path.exists():
            raise FileNotFoundError(f"Rendered PDF not found: {pdf_path}")

        page_analyses: List[PageRasterAnalysis] = []
        all_failures: List[RenderedQualityFailure] = []

        densities: List[float] = []
        blank_ratios: List[float] = []
        balances: List[float] = []
        edge_densities: List[float] = []
        quad_variances: List[float] = []

        with fitz.open(pdf_path) as doc:
            mat = fitz.Matrix(self.dpi / 72.0, self.dpi / 72.0)
            for idx, page in enumerate(doc, start=1):
                pix = page.get_pixmap(matrix=mat)
                p_analysis = self.inspect_pixmap(pix, idx, artifact_type=artifact_type)
                page_analyses.append(p_analysis)
                all_failures.extend(p_analysis.failures)

                densities.append(p_analysis.visual_density)
                blank_ratios.append(p_analysis.blank_ratio)
                balances.append(p_analysis.visual_balance_score)
                edge_densities.append(p_analysis.edge_density)

                qs = p_analysis.quadrant_densities
                q_mean = sum(qs) / 4.0
                q_var = sum((q - q_mean) ** 2 for q in qs) / 4.0
                quad_variances.append(q_var)

        mean_density = sum(densities) / max(1, len(densities))
        mean_blank = sum(blank_ratios) / max(1, len(blank_ratios))
        mean_balance = sum(balances) / max(1, len(balances))
        mean_edge = sum(edge_densities) / max(1, len(edge_densities))
        mean_quad_var = sum(quad_variances) / max(1, len(quad_variances))

        metrics = RasterMetrics(
            mean_visual_density=round(mean_density, 3),
            blank_region_ratio=round(mean_blank, 3),
            visual_balance_score=round(mean_balance, 3),
            edge_density=round(mean_edge, 3),
            quadrant_balance_variance=round(mean_quad_var, 4),
        )

        return metrics, page_analyses, all_failures
