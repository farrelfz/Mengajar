"""
Universal Document Intelligence System V5 — Scientific Document Rendered Quality Evaluator.

Phase 3A: Independent rendered evaluation of academic scientific papers & KTI:
- Formal BAB 1–5 / IMRAD chapter hierarchy consistency
- Claim-to-evidence proximity and table/chart context
- In-text citation visibility and bibliographic integrity
- Argument density vs academic rigor
- Section balance & formal academic typography
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


class ScientificRenderedQualityEvaluator:
    """Independent quality evaluator for rendered academic scientific documents."""

    REQUIRED_BABS = ["BAB I", "BAB II", "BAB III", "BAB IV", "BAB V"]

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
            raise FileNotFoundError(f"Scientific document PDF not found: {pdf_path}")

        # 1. Geometry & Raster Inspection
        geom_metrics, page_geoms, geom_failures = self.geometry_inspector.inspect_document(
            pdf_path, artifact_type="SCIENTIFIC_DOCUMENT"
        )
        raster_metrics, page_rasters, raster_failures = self.raster_inspector.inspect_document(
            pdf_path, artifact_type="SCIENTIFIC_DOCUMENT"
        )

        n_pages = len(page_geoms)
        all_failures: List[RenderedQualityFailure] = list(geom_failures + raster_failures)

        fingerprints: List[PageCompositionFingerprint] = []
        page_font_sizes: List[Tuple[float, float]] = []
        page_texts: List[str] = []
        page_text_lens: List[int] = []
        page_occupancies: List[float] = []

        bab_order_seen: List[str] = []
        citations_found: List[str] = []
        tables_count = 0
        figures_count = 0

        with fitz.open(pdf_path) as doc:
            for idx, page in enumerate(doc, start=1):
                p_geom = page_geoms[idx - 1]
                p_rast = page_rasters[idx - 1]
                text = page.get_text().strip()
                page_texts.append(text)
                page_text_lens.append(len(text))
                page_occupancies.append(p_geom.occupancy_ratio)
                page_font_sizes.append((p_geom.min_font_size, p_geom.max_font_size))

                # A. Scan for BAB headings in order
                for bab in self.REQUIRED_BABS:
                    if re.search(rf"\b{bab}\b", text, re.IGNORECASE):
                        if bab not in bab_order_seen:
                            bab_order_seen.append(bab)

                # B. Scan for in-text citations: [1], [2], (Author, Year), etc.
                cit_matches = re.findall(r"\[\d+\]|\([A-Za-z\s]+,\s*\d{4}\)", text)
                citations_found.extend(cit_matches)

                # C. Check table / figure markers
                if re.search(r"tabel\s+\d+|table\s+\d+", text, re.IGNORECASE):
                    tables_count += 1
                if re.search(r"gambar\s+\d+|figure\s+\d+", text, re.IGNORECASE):
                    figures_count += 1

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
            fingerprints, artifact_type="SCIENTIFIC_DOCUMENT"
        )
        all_failures.extend(comp_failures)

        # 3. Typography & Density
        typo_metrics, typo_failures = TypographyDensityAnalyzer.analyze_typography(
            page_font_sizes, artifact_type="SCIENTIFIC_DOCUMENT"
        )
        all_failures.extend(typo_failures)

        density_metrics, density_failures = TypographyDensityAnalyzer.analyze_density(
            page_text_lens, page_occupancies, artifact_type="SCIENTIFIC_DOCUMENT"
        )
        all_failures.extend(density_failures)

        # 4. Academic Rigor & Failure Detection:
        # A. BAB Hierarchy Inversion Check
        # Ensure bab_order_seen maintains sorted order
        expected_indices = [self.REQUIRED_BABS.index(b) for b in bab_order_seen if b in self.REQUIRED_BABS]
        is_inverted = any(expected_indices[i] > expected_indices[i + 1] for i in range(len(expected_indices) - 1))
        if is_inverted:
            all_failures.append(
                RenderedQualityFailure(
                    code=RenderedFailureCode.SCIENTIFIC_HIERARCHY_FAILURE,
                    severity=RenderedFailureSeverity.CRITICAL,
                    artifact_type="SCIENTIFIC_DOCUMENT",
                    page_indices=tuple(range(1, n_pages + 1)),
                    description=f"Scientific Document: Inverted BAB hierarchy detected: {bab_order_seen}.",
                    evidence={"observed_order": bab_order_seen},
                    recommended_future_repair=FutureRepairClass.CLASS_D_SEMANTIC_REFINEMENT,
                    repair_guidance="Restore canonical IMRAD / BAB sequence (BAB 1 -> BAB 2 -> BAB 3 -> BAB 4 -> BAB 5).",
                )
            )

        # B. Citation Visibility Check:
        # If document is multi-page (>= 3 pages) but has 0 citations
        if n_pages >= 3 and len(citations_found) == 0:
            all_failures.append(
                RenderedQualityFailure(
                    code=RenderedFailureCode.SCIENTIFIC_CITATION_INVISIBLE,
                    severity=RenderedFailureSeverity.MAJOR,
                    artifact_type="SCIENTIFIC_DOCUMENT",
                    page_indices=tuple(range(1, n_pages + 1)),
                    description="Scientific Document: Zero visible citations detected in multi-page academic document.",
                    evidence={"citations_count": 0, "page_count": n_pages},
                    recommended_future_repair=FutureRepairClass.CLASS_D_SEMANTIC_REFINEMENT,
                    repair_guidance="Ensure source bibliographic references and in-text markers are rendered.",
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
                artifact_type="SCIENTIFIC_DOCUMENT",
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

        # 6. Scientific Rigor Score
        hierarchy_score = 0.40 if is_inverted else 1.0
        citation_score = 0.60 if (n_pages >= 3 and len(citations_found) == 0) else 1.0
        academic_rigor_score = round(hierarchy_score * 0.60 + citation_score * 0.40, 3)

        artifact_specific_metrics = {
            "artifact_specific_score": academic_rigor_score,
            "academic_rigor_score": academic_rigor_score,
            "babs_detected": bab_order_seen,
            "citations_found_count": len(citations_found),
            "tables_found_count": tables_count,
            "figures_found_count": figures_count,
            "hierarchy_intact": not is_inverted,
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
            artifact_type="SCIENTIFIC_DOCUMENT",
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
