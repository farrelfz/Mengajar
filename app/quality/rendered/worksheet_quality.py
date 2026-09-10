"""
Universal Document Intelligence System V5 — Worksheet Rendered Quality Evaluator.

Phase 3A: Independent rendered evaluation of educational worksheets / LKS:
- Guided scientific inquiry progression (Phenomenon -> Prediction -> Observation -> Analysis)
- Student workspace box adequacy & writing canvas dimensions (via PyMuPDF vector drawings)
- Anti-spoiling verification (ensures answers/explanations are strictly withheld)
- Quiz collapse detection (prevents conversion into monolithic question banks)
- Whitespace validation (preserves student response area as positive utility)
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


class WorksheetRenderedQualityEvaluator:
    """Independent quality evaluator for rendered educational worksheets."""

    INQUIRY_KEYWORDS = [
        "prediksi", "hipotesis", "pengamatan", "observasi",
        "investigasi", "eksperimen", "tabel data", "analisis",
        "kesimpulan", "refleksi", "pertanyaan pemantik"
    ]

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
            raise FileNotFoundError(f"Worksheet PDF not found: {pdf_path}")

        # 1. Geometry & Raster Inspection
        geom_metrics, page_geoms, geom_failures = self.geometry_inspector.inspect_document(
            pdf_path, artifact_type="WORKSHEET"
        )
        raster_metrics, page_rasters, raster_failures = self.raster_inspector.inspect_document(
            pdf_path, artifact_type="WORKSHEET"
        )

        n_pages = len(page_geoms)
        all_failures: List[RenderedQualityFailure] = list(geom_failures + raster_failures)

        fingerprints: List[PageCompositionFingerprint] = []
        page_font_sizes: List[Tuple[float, float]] = []
        page_texts: List[str] = []
        page_text_lens: List[int] = []
        page_occupancies: List[float] = []

        total_workspace_boxes = 0
        total_workspace_area = 0.0
        pages_with_inquiry_phases: set[int] = set()
        cramped_workspace_pages: List[int] = []
        spoiling_leak_pages: List[int] = []
        quiz_item_count = 0

        with fitz.open(pdf_path) as doc:
            for idx, page in enumerate(doc, start=1):
                p_geom = page_geoms[idx - 1]
                p_rast = page_rasters[idx - 1]
                text = page.get_text().strip()
                page_texts.append(text)
                page_text_lens.append(len(text))
                page_occupancies.append(p_geom.occupancy_ratio)
                page_font_sizes.append((p_geom.min_font_size, p_geom.max_font_size))

                # A. Inspect vector drawings for student workspace boxes (rectangles with height >= 35pt)
                drawings = page.get_drawings()
                page_ws_area = 0.0
                page_ws_boxes = 0
                for d in drawings:
                    r = d.get("rect")
                    if r:
                        rw = r.width
                        rh = r.height
                        # Response boxes typically have height between 35 and 500pt and width >= 150pt
                        if 35.0 <= rh <= 600.0 and rw >= 150.0:
                            page_ws_boxes += 1
                            box_area = rw * rh
                            page_ws_area += box_area

                total_workspace_boxes += page_ws_boxes
                total_workspace_area += page_ws_area

                # B. Detect Inquiry Progression
                text_lower = text.lower()
                for kw in self.INQUIRY_KEYWORDS:
                    if kw in text_lower:
                        pages_with_inquiry_phases.add(idx)

                # Count numbered question patterns (e.g. "1.", "2.", "pertanyaan 1")
                q_matches = re.findall(r"(?:^|\n)\s*(?:\d+[\.\)]|soal\s+\d+|pertanyaan\s+\d+)", text_lower)
                quiz_item_count += len(q_matches)

                # C. Anti-Spoiling Audit in Rendered Text:
                # If "jawaban:", "penjelasan lengkap:", or "kunci jawaban" is directly rendered in activity space
                if any(leak in text_lower for leak in ["kunci jawaban:", "jawaban yang benar:", "pembahasan lengkap:"]):
                    spoiling_leak_pages.append(idx)

                # Check if page has multiple questions but zero workspace boxes
                if len(q_matches) >= 2 and page_ws_boxes == 0 and idx < n_pages:
                    cramped_workspace_pages.append(idx)

                fp = PageCompositionFingerprint(
                    page_number=idx,
                    quadrants=p_geom.quadrant_occupancies,
                    text_density=round(p_geom.occupied_area / max(1.0, p_geom.page_area), 3),
                    whitespace_ratio=round(p_rast.blank_ratio, 3),
                    major_blocks_count=len(page.get_text("blocks")),
                    aspect_ratio=round(p_geom.width / max(1.0, p_geom.height), 3),
                )
                fingerprints.append(fp)

        # 2. Composition Metrics & Streaks
        comp_metrics, streaks, comp_failures = self.fingerprint_engine.analyze_fingerprints(
            fingerprints, artifact_type="WORKSHEET"
        )
        all_failures.extend(comp_failures)

        # 3. Typography & Density
        typo_metrics, typo_failures = TypographyDensityAnalyzer.analyze_typography(
            page_font_sizes, artifact_type="WORKSHEET"
        )
        all_failures.extend(typo_failures)

        density_metrics, density_failures = TypographyDensityAnalyzer.analyze_density(
            page_text_lens, page_occupancies, artifact_type="WORKSHEET"
        )
        all_failures.extend(density_failures)

        # 4. Worksheet Failure Classification:
        # A. Anti-Spoiling Leak (CRITICAL)
        if spoiling_leak_pages:
            all_failures.append(
                RenderedQualityFailure(
                    code=RenderedFailureCode.WORKSHEET_SPOILING_FAILURE,
                    severity=RenderedFailureSeverity.CRITICAL,
                    artifact_type="WORKSHEET",
                    page_indices=tuple(spoiling_leak_pages),
                    description=f"Worksheet: Anti-spoiling violation! Answers/explanations exposed on pages {spoiling_leak_pages}.",
                    evidence={"leaked_pages": spoiling_leak_pages},
                    recommended_future_repair=FutureRepairClass.CLASS_D_SEMANTIC_REFINEMENT,
                    repair_guidance="Withhold answers and full explanations from student worksheet.",
                )
            )

        # B. Quiz Collapse: High question count (> 8) but very low inquiry phase coverage (< 30%)
        inquiry_coverage = len(pages_with_inquiry_phases) / max(1, n_pages)
        if quiz_item_count >= 8 and inquiry_coverage < 0.35:
            all_failures.append(
                RenderedQualityFailure(
                    code=RenderedFailureCode.WORKSHEET_QUIZ_COLLAPSE,
                    severity=RenderedFailureSeverity.MAJOR,
                    artifact_type="WORKSHEET",
                    page_indices=tuple(range(1, n_pages + 1)),
                    description=(
                        f"Worksheet: Quiz collapse detected ({quiz_item_count} questions without scaffolded inquiry phases). "
                        f"Inquiry coverage is {inquiry_coverage * 100:.1f}%."
                    ),
                    evidence={"quiz_items": quiz_item_count, "inquiry_coverage": inquiry_coverage},
                    recommended_future_repair=FutureRepairClass.CLASS_D_SEMANTIC_REFINEMENT,
                    repair_guidance="Introduce inquiry progression (Phenomenon -> Prediction -> Experiment -> Reflection).",
                )
            )

        # C. Insufficient Student Workspace
        if cramped_workspace_pages:
            all_failures.append(
                RenderedQualityFailure(
                    code=RenderedFailureCode.WORKSHEET_WORKSPACE_INSUFFICIENT,
                    severity=RenderedFailureSeverity.MAJOR,
                    artifact_type="WORKSHEET",
                    page_indices=tuple(cramped_workspace_pages),
                    description=f"Worksheet: Insufficient student workspace boxes on pages {cramped_workspace_pages}.",
                    evidence={"cramped_pages": cramped_workspace_pages, "total_boxes": total_workspace_boxes},
                    recommended_future_repair=FutureRepairClass.CLASS_A_GEOMETRY,
                    repair_guidance="Render designated response boxes with minimum height >= 60pt for student answers.",
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
                artifact_type="WORKSHEET",
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
                    diagnostics={"workspace_boxes": total_workspace_boxes},
                )
            )

        # 6. Calculate Worksheet Pedagogical Score
        inquiry_score = min(1.0, max(0.30, round(inquiry_coverage * 1.25, 3)))
        spoiling_deduction = 0.50 if spoiling_leak_pages else 0.0
        workspace_score = max(0.30, 1.0 - (len(cramped_workspace_pages) * 0.15))
        worksheet_pedagogical_score = max(0.10, round((inquiry_score * 0.60 + workspace_score * 0.40) - spoiling_deduction, 3))

        artifact_specific_metrics = {
            "artifact_specific_score": worksheet_pedagogical_score,
            "worksheet_pedagogical_score": worksheet_pedagogical_score,
            "inquiry_coverage_ratio": round(inquiry_coverage, 3),
            "total_workspace_boxes": total_workspace_boxes,
            "total_workspace_area_pt": round(total_workspace_area, 1),
            "anti_spoiling_intact": len(spoiling_leak_pages) == 0,
            "quiz_items_count": quiz_item_count,
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
            artifact_type="WORKSHEET",
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
