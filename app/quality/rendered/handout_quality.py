"""
Universal Document Intelligence System V5 — Handout Rendered Quality Evaluator.

Phase 3A: Independent rendered evaluation of A4 continuous reading handouts:
- Reading flow & paragraph chunking
- Orphan headings at page breaks
- Textbook wall of text detection
- Presentation-like fragmentation detection
- Margin consistency & print readability
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, ConfigDict, Field

try:
    import pymupdf as fitz
except ImportError:
    import fitz

from app.quality.rendered.composition_fingerprint import (
    CompositionFingerprintEngine,
    PageCompositionFingerprint,
)
from app.quality.rendered.contracts import (
    CompositionMetrics,
    DensityMetrics,
    GeometryMetrics,
    PageInspectionDetail,
    RasterMetrics,
    RenderedArtifactInspection,
    StructuralRenderMetrics,
    TypographyMetrics,
)
from app.quality.rendered.failure_taxonomy import (
    FutureRepairClass,
    RenderedFailureCode,
    RenderedFailureSeverity,
    RenderedQualityFailure,
)
from app.quality.rendered.pdf_inspector import PDFGeometryInspector
from app.quality.rendered.raster_inspector import RasterImageInspector
from app.quality.rendered.typography_density import TypographyDensityAnalyzer
from app.quality.rendered.whitespace_model import WhitespaceIntentModel


class HandoutRenderedQualityEvaluator:
    """Independent quality evaluator for rendered continuous reading handouts."""

    def __init__(self) -> None:
        self.geometry_inspector = PDFGeometryInspector(clip_tolerance_pt=4.0)
        self.raster_inspector = RasterImageInspector(dpi=72)
        self.fingerprint_engine = CompositionFingerprintEngine(
            streak_similarity_threshold=0.92,
            document_max_allowed_streak=5,
        )

    def evaluate(
        self,
        pdf_path: Path,
        html_path: Path | None = None,
        source_metadata: Dict[str, Any] | None = None,
    ) -> RenderedArtifactInspection:
        if not pdf_path.exists():
            raise FileNotFoundError(f"Handout PDF not found: {pdf_path}")

        # 1. Geometry & Raster Inspection
        geom_metrics, page_geoms, geom_failures = self.geometry_inspector.inspect_document(
            pdf_path, artifact_type="HANDOUT"
        )
        raster_metrics, page_rasters, raster_failures = self.raster_inspector.inspect_document(
            pdf_path, artifact_type="HANDOUT"
        )

        n_pages = len(page_geoms)
        all_failures: List[RenderedQualityFailure] = list(geom_failures + raster_failures)

        fingerprints: List[PageCompositionFingerprint] = []
        page_font_sizes: List[Tuple[float, float]] = []
        page_texts: List[str] = []
        page_text_lens: List[int] = []
        page_occupancies: List[float] = []

        orphan_headings: List[int] = []
        walls_of_text: List[int] = []
        fragmented_pages: List[int] = []

        with fitz.open(pdf_path) as doc:
            for idx, page in enumerate(doc, start=1):
                p_geom = page_geoms[idx - 1]
                p_rast = page_rasters[idx - 1]
                text = page.get_text().strip()
                page_texts.append(text)
                page_text_lens.append(len(text))
                page_occupancies.append(p_geom.occupancy_ratio)
                page_font_sizes.append((p_geom.min_font_size, p_geom.max_font_size))

                # Handout-Specific Invariant Checks:
                # A. Orphan Heading Detection: Heading block positioned at the bottom 10% of page
                blocks = page.get_text("dict").get("blocks", [])
                page_h = p_geom.height
                if len(blocks) > 0 and idx < n_pages:
                    last_block = blocks[-1]
                    b_bbox = last_block.get("bbox", (0, 0, 0, 0))
                    # Check if last block is near page bottom and has large/heading font size
                    if b_bbox[3] > (page_h - 70.0):
                        spans = [s for l in last_block.get("lines", []) for s in l.get("spans", [])]
                        if spans:
                            max_sz = max(s.get("size", 10.0) for s in spans)
                            block_text = "".join(s.get("text", "") for s in spans).strip()
                            if max_sz >= (p_geom.min_font_size * 1.25) and len(block_text) < 80:
                                orphan_headings.append(idx)

                # B. Wall of text: Single unbroken block > 2000 chars
                for b in blocks:
                    b_text = "".join(s.get("text", "") for l in b.get("lines", []) for s in l.get("spans", []))
                    if len(b_text) > 2200:
                        walls_of_text.append(idx)

                # C. Presentation-like fragmentation: page with very few chars (<100 words) but >4 discrete cards
                if len(text) < 300 and len(blocks) >= 4 and idx < n_pages:
                    fragmented_pages.append(idx)

                fp = PageCompositionFingerprint(
                    page_number=idx,
                    quadrants=p_geom.quadrant_occupancies,
                    text_density=round(p_geom.occupied_area / max(1.0, p_geom.page_area), 3),
                    whitespace_ratio=round(p_rast.blank_ratio, 3),
                    major_blocks_count=len(blocks),
                    aspect_ratio=round(p_geom.width / max(1.0, p_geom.height), 3),
                )
                fingerprints.append(fp)

        # 2. Composition Metrics & Monotony
        comp_metrics, streaks, comp_failures = self.fingerprint_engine.analyze_fingerprints(
            fingerprints, artifact_type="HANDOUT"
        )
        all_failures.extend(comp_failures)

        # 3. Typographic & Density Metrics
        typo_metrics, typo_failures = TypographyDensityAnalyzer.analyze_typography(
            page_font_sizes, artifact_type="HANDOUT"
        )
        all_failures.extend(typo_failures)

        density_metrics, density_failures = TypographyDensityAnalyzer.analyze_density(
            page_text_lens, page_occupancies, artifact_type="HANDOUT"
        )
        all_failures.extend(density_failures)

        # 4. Record Handout Failures
        if orphan_headings:
            all_failures.append(
                RenderedQualityFailure(
                    code=RenderedFailureCode.ORPHAN_HEADING,
                    severity=RenderedFailureSeverity.MAJOR,
                    artifact_type="HANDOUT",
                    page_indices=tuple(orphan_headings),
                    description=f"Handout: Orphan heading detected at bottom of page {orphan_headings} without body continuation.",
                    evidence={"orphan_pages": orphan_headings},
                    recommended_future_repair=FutureRepairClass.CLASS_C_PAGINATION_PACING,
                    repair_guidance="Insert page break before heading to keep heading with its section.",
                )
            )

        if walls_of_text:
            all_failures.append(
                RenderedQualityFailure(
                    code=RenderedFailureCode.HANDOUT_WALL_OF_TEXT,
                    severity=RenderedFailureSeverity.MAJOR,
                    artifact_type="HANDOUT",
                    page_indices=tuple(walls_of_text),
                    description=f"Handout: Monolithic unbroken wall of text on page {walls_of_text} (> 2200 characters).",
                    evidence={"pages": walls_of_text},
                    recommended_future_repair=FutureRepairClass.CLASS_D_SEMANTIC_REFINEMENT,
                    repair_guidance="Break text into multi-paragraph sections or introduce definition callouts.",
                )
            )

        if fragmented_pages:
            all_failures.append(
                RenderedQualityFailure(
                    code=RenderedFailureCode.HANDOUT_FRAGMENTATION,
                    severity=RenderedFailureSeverity.MINOR,
                    artifact_type="HANDOUT",
                    page_indices=tuple(fragmented_pages),
                    description=f"Handout: Presentation-like fragmentation on page {fragmented_pages} (sparse text split into cards).",
                    evidence={"pages": fragmented_pages},
                    recommended_future_repair=FutureRepairClass.CLASS_B_LAYOUT_REMAPPING,
                    repair_guidance="Consolidate fragmented cards into continuous narrative paragraphs.",
                )
            )

        # 5. Assemble Page Details
        page_details: List[PageInspectionDetail] = []
        for idx in range(1, n_pages + 1):
            p_geom = page_geoms[idx - 1]
            p_rast = page_rasters[idx - 1]
            p_fails = [f for f in all_failures if idx in f.page_indices]

            ws_eval = WhitespaceIntentModel.evaluate_page(
                page_idx=idx,
                artifact_type="HANDOUT",
                occupancy_ratio=p_geom.occupancy_ratio,
                text_length=page_text_lens[idx - 1],
                is_last_page=(idx == n_pages),
            )
            if ws_eval.failure:
                all_failures.append(ws_eval.failure)
                p_fails.append(ws_eval.failure)

            page_details.append(
                PageInspectionDetail(
                    page_number=idx,
                    dimensions=(p_geom.width, p_geom.height),
                    text_length=page_text_lens[idx - 1],
                    occupancy_ratio=p_geom.occupancy_ratio,
                    quadrant_occupancy=p_geom.quadrant_occupancies,
                    min_font_size=p_geom.min_font_size,
                    max_font_size=p_geom.max_font_size,
                    has_clipping=(p_geom.clipping_boxes_count > 0),
                    has_collision=(p_geom.collision_boxes_count > 0),
                    density_status=ws_eval.status,
                    failures=tuple(p_fails),
                    diagnostics={"visual_balance": p_rast.visual_balance_score},
                )
            )

        # 6. Handout Reading Flow Score
        flow_deduction = (len(orphan_headings) * 0.20) + (len(walls_of_text) * 0.15) + (len(fragmented_pages) * 0.10)
        reading_flow_score = max(0.20, round(1.0 - min(0.70, flow_deduction), 3))

        artifact_specific_metrics = {
            "artifact_specific_score": reading_flow_score,
            "reading_flow_score": reading_flow_score,
            "orphan_headings_count": len(orphan_headings),
            "walls_of_text_count": len(walls_of_text),
            "fragmented_pages_count": len(fragmented_pages),
            "margin_consistency": geom_metrics.margin_variance,
        }

        # Structural Metrics
        p0 = page_geoms[0] if page_geoms else None
        p_dims = (p0.width, p0.height) if p0 else (595.0, 842.0)
        structural_metrics = StructuralRenderMetrics(
            page_count=n_pages,
            expected_format_id="a4_portrait",
            format_dimensions_match=(p_dims[1] > p_dims[0]),
            blank_pages_count=sum(1 for r in page_rasters if r.is_blank),
            total_text_blocks=sum(len(page.get_text("blocks")) for page in fitz.open(pdf_path)),
            total_images_count=sum(len(page.get_images()) for page in fitz.open(pdf_path)),
        )

        return RenderedArtifactInspection.create(
            artifact_type="HANDOUT",
            rendered_pdf_path=pdf_path,
            rendered_html_path=html_path,
            page_count=n_pages,
            page_dimensions=p_dims,
            structural_metrics=structural_metrics,
            geometry_metrics=geom_metrics,
            raster_metrics=raster_metrics,
            density_metrics=density_metrics,
            hierarchy_metrics=typo_metrics,
            repetition_metrics=comp_metrics,
            artifact_specific_metrics=artifact_specific_metrics,
            page_details=page_details,
            failures=all_failures,
        )
