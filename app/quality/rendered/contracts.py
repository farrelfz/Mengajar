"""
Universal Document Intelligence System V5 — Rendered Output Inspection Contracts.

Phase 3A: Authoritative, immutable contracts for post-render physical PDF
and raster image inspection across all four artifact formats.
"""

from __future__ import annotations

import time
import uuid
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, ConfigDict, Field

from app.quality.rendered.failure_taxonomy import (
    FutureRepairClass,
    RenderedFailureCode,
    RenderedFailureSeverity,
    RenderedQualityFailure,
)


class RenderedQualityDecision(str, Enum):
    """Authoritative decision status for rendered artifact export."""
    PASS = "PASS"
    PASS_WITH_WARNINGS = "PASS_WITH_WARNINGS"
    NEEDS_REPAIR = "NEEDS_REPAIR"
    BLOCKED = "BLOCKED"


class StructuralRenderMetrics(BaseModel):
    """Basic physical structural metrics of rendered PDF."""
    model_config = ConfigDict(frozen=True)

    page_count: int = 0
    expected_format_id: str = "auto"
    format_dimensions_match: bool = True
    blank_pages_count: int = 0
    total_text_blocks: int = 0
    total_images_count: int = 0


class GeometryMetrics(BaseModel):
    """Vector geometry metrics extracted from PDF page display lists."""
    model_config = ConfigDict(frozen=True)

    text_clipping_instances: int = 0
    page_overflow_instances: int = 0
    tiny_text_spans_count: int = 0
    element_collision_count: int = 0
    mean_margin_pt: float = 0.0
    margin_variance: float = 0.0
    min_observed_font_size: float = 12.0
    max_observed_font_size: float = 12.0


class RasterMetrics(BaseModel):
    """Computer vision raster analysis metrics from rendered page screenshots."""
    model_config = ConfigDict(frozen=True)

    mean_visual_density: float = 0.0
    blank_region_ratio: float = 0.0
    visual_balance_score: float = 1.0
    edge_density: float = 0.0
    quadrant_balance_variance: float = 0.0


class TypographyMetrics(BaseModel):
    """Typographic hierarchy ratios and consistency across the document."""
    model_config = ConfigDict(frozen=True)

    headline_to_body_ratio: float = 1.50
    subheadline_to_body_ratio: float = 1.20
    hierarchy_contrast_score: float = 1.0
    font_scale_consistency: float = 1.0


class DensityMetrics(BaseModel):
    """Content and spatial density distribution across pages."""
    model_config = ConfigDict(frozen=True)

    mean_occupancy_ratio: float = 0.50
    overloaded_pages_count: int = 0
    suspiciously_sparse_pages_count: int = 0
    whitespace_ratio: float = 0.50
    intentional_whitespace_ratio: float = 0.50


class CompositionMetrics(BaseModel):
    """Layout diversity, layout monotony, and composition repetition streaks."""
    model_config = ConfigDict(frozen=True)

    layout_diversity_score: float = 1.0
    max_repetition_streak: int = 1
    near_duplicate_pages_count: int = 0
    mean_spatial_similarity: float = 0.0


class PageInspectionDetail(BaseModel):
    """Per-page diagnostic summary for rendered inspection."""
    model_config = ConfigDict(frozen=True)

    page_number: int
    dimensions: Tuple[float, float]
    text_length: int
    occupancy_ratio: float
    quadrant_occupancy: Tuple[float, float, float, float]  # TL, TR, BL, BR
    min_font_size: float
    max_font_size: float
    has_clipping: bool = False
    has_collision: bool = False
    density_status: str = "BALANCED"
    failures: Tuple[RenderedQualityFailure, ...] = Field(default_factory=tuple)
    diagnostics: Dict[str, Any] = Field(default_factory=dict)


class RenderedArtifactInspection(BaseModel):
    """Authoritative, immutable post-render inspection outcome.
    
    CRITICAL ARCHITECTURAL INVARIANT:
    overall_quality_score must NEVER hide dimensional failures.
    Any CRITICAL failure forces decision = BLOCKED and can_export = False.
    """
    model_config = ConfigDict(frozen=True)

    inspection_id: str = Field(default_factory=lambda: f"insp_{uuid.uuid4().hex[:8]}")
    artifact_type: str
    source_path: Optional[str] = None
    rendered_pdf_path: str
    rendered_html_path: Optional[str] = None
    page_count: int
    page_dimensions: Tuple[float, float]
    inspection_timestamp: float = Field(default_factory=time.time)

    # Core Subsystem Metrics
    structural_metrics: StructuralRenderMetrics = Field(default_factory=StructuralRenderMetrics)
    geometry_metrics: GeometryMetrics = Field(default_factory=GeometryMetrics)
    raster_metrics: RasterMetrics = Field(default_factory=RasterMetrics)
    density_metrics: DensityMetrics = Field(default_factory=DensityMetrics)
    hierarchy_metrics: TypographyMetrics = Field(default_factory=TypographyMetrics)
    repetition_metrics: CompositionMetrics = Field(default_factory=CompositionMetrics)
    artifact_specific_metrics: Dict[str, Any] = Field(default_factory=dict)

    # Granular Page Diagnostics
    page_details: Tuple[PageInspectionDetail, ...] = Field(default_factory=tuple)

    # Defects & Severities
    critical_failures: Tuple[RenderedQualityFailure, ...] = Field(default_factory=tuple)
    major_warnings: Tuple[RenderedQualityFailure, ...] = Field(default_factory=tuple)
    minor_warnings: Tuple[RenderedQualityFailure, ...] = Field(default_factory=tuple)

    # Explicit Orthogonal Dimensional Scores (0.0 to 1.0)
    dimensional_scores: Dict[str, float] = Field(default_factory=dict)

    # Composite Score & Governed Decision
    overall_quality_score: float = Field(ge=0.0, le=1.0)
    decision: RenderedQualityDecision
    can_export: bool
    rationale: str

    @property
    def has_critical_failures(self) -> bool:
        return len(self.critical_failures) > 0

    @classmethod
    def create(
        cls,
        artifact_type: str,
        rendered_pdf_path: Path | str,
        page_count: int,
        page_dimensions: Tuple[float, float],
        structural_metrics: StructuralRenderMetrics,
        geometry_metrics: GeometryMetrics,
        raster_metrics: RasterMetrics,
        density_metrics: DensityMetrics,
        hierarchy_metrics: TypographyMetrics,
        repetition_metrics: CompositionMetrics,
        artifact_specific_metrics: Dict[str, Any],
        page_details: List[PageInspectionDetail],
        failures: List[RenderedQualityFailure],
        rendered_html_path: Path | str | None = None,
        source_path: Path | str | None = None,
    ) -> RenderedArtifactInspection:
        crit = tuple(f for f in failures if f.severity == RenderedFailureSeverity.CRITICAL)
        maj = tuple(f for f in failures if f.severity == RenderedFailureSeverity.MAJOR)
        minr = tuple(f for f in failures if f.severity == RenderedFailureSeverity.MINOR)

        # 1. Compute Dimensional Scores
        # A. Render Integrity (clipping, blanks, boundary violation)
        render_integ = max(0.0, 1.0 - (len(crit) * 0.40) - (structural_metrics.blank_pages_count * 0.50))

        # B. Visual Geometry (overflow, collision, margins)
        geom_score = max(0.0, 1.0 - (geometry_metrics.text_clipping_instances * 0.35) - (geometry_metrics.element_collision_count * 0.20))

        # C. Readability (tiny text, font scales)
        readability = max(0.0, 1.0 - (geometry_metrics.tiny_text_spans_count * 0.15))

        # D. Typographic Hierarchy
        hierarchy = hierarchy_metrics.hierarchy_contrast_score

        # E. Density Balance
        density = max(0.0, 1.0 - (density_metrics.overloaded_pages_count * 0.25) - (density_metrics.suspiciously_sparse_pages_count * 0.15))

        # F. Composition Rhythm & Diversity
        comp_rhythm = repetition_metrics.layout_diversity_score

        # G. Artifact Specific Score
        art_spec = float(artifact_specific_metrics.get("artifact_specific_score", 1.0))

        dim_scores = {
            "render_integrity": round(render_integ, 3),
            "visual_geometry": round(geom_score, 3),
            "readability": round(readability, 3),
            "typographic_hierarchy": round(hierarchy, 3),
            "density_balance": round(density, 3),
            "composition_rhythm": round(comp_rhythm, 3),
            "artifact_specific_quality": round(art_spec, 3),
        }

        # Weighted composite overall score
        overall = round(
            (
                render_integ * 0.20
                + geom_score * 0.15
                + readability * 0.15
                + hierarchy * 0.10
                + density * 0.15
                + comp_rhythm * 0.10
                + art_spec * 0.15
            ),
            3,
        )
        overall = max(0.0, min(1.0, overall))

        # Decision Governance (CRITICAL failure ALWAYS blocks export)
        if len(crit) > 0:
            decision = RenderedQualityDecision.BLOCKED
            can_export = False
            top_crit = crit[0].description
            rationale = f"Export BLOCKED due to {len(crit)} critical rendered failures. Top: {top_crit}"
        elif len(maj) > 0:
            decision = RenderedQualityDecision.NEEDS_REPAIR
            can_export = False
            top_maj = maj[0].description
            rationale = f"Export held for repair due to {len(maj)} major warnings. Top: {top_maj}"
        elif len(minr) > 0 or overall < 0.85:
            decision = RenderedQualityDecision.PASS_WITH_WARNINGS
            can_export = True
            rationale = f"Approved with {len(minr)} minor warnings. Score: {overall:.3f}"
        else:
            decision = RenderedQualityDecision.PASS
            can_export = True
            rationale = f"Approved. Rendered quality score: {overall:.3f}"

        return cls(
            artifact_type=artifact_type,
            source_path=str(source_path) if source_path else None,
            rendered_pdf_path=str(rendered_pdf_path),
            rendered_html_path=str(rendered_html_path) if rendered_html_path else None,
            page_count=page_count,
            page_dimensions=page_dimensions,
            structural_metrics=structural_metrics,
            geometry_metrics=geometry_metrics,
            raster_metrics=raster_metrics,
            density_metrics=density_metrics,
            hierarchy_metrics=hierarchy_metrics,
            repetition_metrics=repetition_metrics,
            artifact_specific_metrics=artifact_specific_metrics,
            page_details=tuple(page_details),
            critical_failures=crit,
            major_warnings=maj,
            minor_warnings=minr,
            dimensional_scores=dim_scores,
            overall_quality_score=overall,
            decision=decision,
            can_export=can_export,
            rationale=rationale,
        )
