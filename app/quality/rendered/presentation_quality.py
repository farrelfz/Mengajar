"""
Universal Document Intelligence System V5 — Presentation Rendered Quality Evaluator.

Phase 3A: Independent rendered evaluation of 16:9 presentation slide decks:
- Visual hierarchy & typographic scale
- Slide density & whitespace breathing room
- Layout diversity vs monotony streaks
- Card overload & generic container repetition
- Near-duplicate slide sequences & presentation cadence
"""

from __future__ import annotations

import difflib
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


class PresentationRenderedQualityEvaluator:
    """Independent quality evaluator for rendered presentation slide decks."""

    def __init__(self) -> None:
        self.geometry_inspector = PDFGeometryInspector(clip_tolerance_pt=4.0)
        self.raster_inspector = RasterImageInspector(dpi=72)
        self.fingerprint_engine = CompositionFingerprintEngine(
            streak_similarity_threshold=0.88,
            presentation_max_allowed_streak=3,
        )

    def evaluate(
        self,
        pdf_path: Path,
        html_path: Path | None = None,
        source_metadata: Dict[str, Any] | None = None,
    ) -> RenderedArtifactInspection:
        if not pdf_path.exists():
            raise FileNotFoundError(f"Presentation PDF not found: {pdf_path}")

        # 1. Inspect Vector Geometry
        geom_metrics, page_geoms, geom_failures = self.geometry_inspector.inspect_document(
            pdf_path, artifact_type="PRESENTATION"
        )

        # 2. Inspect Raster Pixmaps
        raster_metrics, page_rasters, raster_failures = self.raster_inspector.inspect_document(
            pdf_path, artifact_type="PRESENTATION"
        )

        n_pages = len(page_geoms)
        all_failures: List[RenderedQualityFailure] = list(geom_failures + raster_failures)

        # 3. Generate Composition Fingerprints
        fingerprints: List[PageCompositionFingerprint] = []
        page_font_sizes: List[Tuple[float, float]] = []
        page_texts: List[str] = []
        page_text_lens: List[int] = []
        page_occupancies: List[float] = []

        with fitz.open(pdf_path) as doc:
            for idx, page in enumerate(doc, start=1):
                p_geom = page_geoms[idx - 1]
                p_rast = page_rasters[idx - 1]
                text = page.get_text().strip()
                page_texts.append(text)
                page_text_lens.append(len(text))
                page_occupancies.append(p_geom.occupancy_ratio)
                page_font_sizes.append((p_geom.min_font_size, p_geom.max_font_size))

                fp = PageCompositionFingerprint(
                    page_number=idx,
                    quadrants=p_geom.quadrant_occupancies,
                    text_density=round(p_geom.occupied_area / max(1.0, p_geom.page_area), 3),
                    whitespace_ratio=round(p_rast.blank_ratio, 3),
                    major_blocks_count=len(page.get_text("blocks")),
                    aspect_ratio=round(p_geom.width / max(1.0, p_geom.height), 3),
                )
                fingerprints.append(fp)

        # 4. Composition Repetition & Streaks
        comp_metrics, streaks, comp_failures = self.fingerprint_engine.analyze_fingerprints(
            fingerprints, artifact_type="PRESENTATION"
        )
        all_failures.extend(comp_failures)

        # 5. Typography & Hierarchy Analysis
        typo_metrics, typo_failures = TypographyDensityAnalyzer.analyze_typography(
            page_font_sizes, artifact_type="PRESENTATION"
        )
        all_failures.extend(typo_failures)

        # 6. Density Analysis
        density_metrics, density_failures = TypographyDensityAnalyzer.analyze_density(
            page_text_lens, page_occupancies, artifact_type="PRESENTATION"
        )
        all_failures.extend(density_failures)

        # 7. Presentation-Specific Invariants:
        # A. Detect near-duplicate slide content
        duplicate_pairs: List[Tuple[int, int, float]] = []
        for i in range(n_pages):
            for j in range(i + 1, n_pages):
                t1 = re.sub(r"\s+", " ", page_texts[i].lower())
                t2 = re.sub(r"\s+", " ", page_texts[j].lower())
                if len(t1) > 40 and len(t2) > 40:
                    sim = difflib.SequenceMatcher(None, t1, t2).ratio()
                    if sim >= 0.92:
                        duplicate_pairs.append((i + 1, j + 1, round(sim, 2)))

        if duplicate_pairs:
            is_critical = any(sim >= 0.99 for _, _, sim in duplicate_pairs) or len(duplicate_pairs) >= 3
            all_failures.append(
                RenderedQualityFailure(
                    code=RenderedFailureCode.DUPLICATE_COMPOSITION,
                    severity=RenderedFailureSeverity.CRITICAL if is_critical else RenderedFailureSeverity.MAJOR,
                    artifact_type="PRESENTATION",
                    page_indices=tuple(set([p for pair in duplicate_pairs for p in (pair[0], pair[1])])),
                    description=(
                        f"Presentation: {len(duplicate_pairs)} slide pairs exhibit near-identical duplicate text "
                        f"(e.g. Slides {duplicate_pairs[0][0]} & {duplicate_pairs[0][1]} similarity {duplicate_pairs[0][2]})."
                    ),
                    evidence={"duplicate_pairs": duplicate_pairs},
                    recommended_future_repair=FutureRepairClass.CLASS_C_PAGINATION_PACING,
                    repair_guidance="Consolidate duplicate slides or introduce distinctive sub-themes.",
                )
            )

        # B. Card overload detection: slide with > 6 dense distinct cards/blocks
        card_overloaded_slides: List[int] = []
        with fitz.open(pdf_path) as doc:
            for idx, page in enumerate(doc, start=1):
                # Count distinct rectangular drawing paths or text blocks
                blocks = page.get_text("blocks")
                if len(blocks) > 8:
                    card_overloaded_slides.append(idx)

        if card_overloaded_slides:
            all_failures.append(
                RenderedQualityFailure(
                    code=RenderedFailureCode.CARD_OVERLOAD,
                    severity=RenderedFailureSeverity.MAJOR,
                    artifact_type="PRESENTATION",
                    page_indices=tuple(card_overloaded_slides),
                    description=(
                        f"Presentation: Card overload on slides {card_overloaded_slides}. "
                        f"Excessive visual fragmentation (> 6-8 distinct blocks per slide)."
                    ),
                    evidence={"overloaded_slides": card_overloaded_slides},
                    recommended_future_repair=FutureRepairClass.CLASS_B_LAYOUT_REMAPPING,
                    repair_guidance="Group related cards or switch to comparison matrix layout.",
                )
            )

        # 8. Assemble Per-Page Details
        page_details: List[PageInspectionDetail] = []
        for idx in range(1, n_pages + 1):
            p_geom = page_geoms[idx - 1]
            p_rast = page_rasters[idx - 1]
            p_fails = [f for f in all_failures if idx in f.page_indices]

            role = "TITLE" if idx == 1 else ("CONCLUSION" if idx == n_pages else "BODY")
            ws_eval = WhitespaceIntentModel.evaluate_page(
                page_idx=idx,
                artifact_type="PRESENTATION",
                occupancy_ratio=p_geom.occupancy_ratio,
                text_length=page_text_lens[idx - 1],
                is_last_page=(idx == n_pages),
                page_role=role,
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
                    diagnostics={
                        "visual_balance": p_rast.visual_balance_score,
                        "edge_density": p_rast.edge_density,
                    },
                )
            )

        # 9. Calculate presentation-specific scores
        dup_deduction = min(0.40, len(duplicate_pairs) * 0.15)
        card_deduction = min(0.30, len(card_overloaded_slides) * 0.10)
        streak_deduction = min(0.30, max(0, comp_metrics.max_repetition_streak - 3) * 0.10)

        rhythm_score = max(0.20, round(1.0 - dup_deduction - streak_deduction, 3))
        presentation_visual_score = max(
            0.20,
            round(
                (raster_metrics.visual_balance_score * 0.40)
                + (typo_metrics.hierarchy_contrast_score * 0.35)
                + ((1.0 - card_deduction) * 0.25),
                3,
            ),
        )

        artifact_specific_metrics = {
            "artifact_specific_score": presentation_visual_score,
            "presentation_visual_score": presentation_visual_score,
            "layout_diversity_score": comp_metrics.layout_diversity_score,
            "rhythm_score": rhythm_score,
            "hierarchy_score": typo_metrics.hierarchy_contrast_score,
            "density_score": round(max(0.20, 1.0 - (density_metrics.overloaded_pages_count * 0.20)), 3),
            "repetition_score": round(max(0.20, 1.0 - dup_deduction), 3),
            "duplicate_slide_pairs_count": len(duplicate_pairs),
            "card_overloaded_slides_count": len(card_overloaded_slides),
        }

        # Structural Metrics
        p0 = page_geoms[0] if page_geoms else None
        p_dims = (p0.width, p0.height) if p0 else (960.0, 540.0)
        structural_metrics = StructuralRenderMetrics(
            page_count=n_pages,
            expected_format_id="presentation_16_9",
            format_dimensions_match=(abs((p_dims[0] / max(1.0, p_dims[1])) - 1.777) < 0.1),
            blank_pages_count=sum(1 for r in page_rasters if r.is_blank),
            total_text_blocks=sum(len(page.get_text("blocks")) for page in fitz.open(pdf_path)),
            total_images_count=sum(len(page.get_images()) for page in fitz.open(pdf_path)),
        )

        return RenderedArtifactInspection.create(
            artifact_type="PRESENTATION",
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
