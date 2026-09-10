"""
Unit tests for Rendered Output Inspection Contracts & Failure Taxonomy.

Phase 3A: Verifies schema invariants, orthogonal dimensions, and decision governance.
"""

from pathlib import Path
import pytest

from app.quality.rendered.contracts import (
    CompositionMetrics,
    DensityMetrics,
    GeometryMetrics,
    PageInspectionDetail,
    RasterMetrics,
    RenderedArtifactInspection,
    RenderedQualityDecision,
    StructuralRenderMetrics,
    TypographyMetrics,
)
from app.quality.rendered.failure_taxonomy import (
    FutureRepairClass,
    RenderedFailureCode,
    RenderedFailureSeverity,
    RenderedQualityFailure,
)


def test_01_failure_taxonomy_serialization():
    failure = RenderedQualityFailure(
        code=RenderedFailureCode.TEXT_CLIPPING,
        severity=RenderedFailureSeverity.CRITICAL,
        artifact_type="PRESENTATION",
        page_indices=(2, 3),
        description="Text clipped outside viewport",
        evidence={"bbox": [-10.0, 50.0, 970.0, 100.0]},
        recommended_future_repair=FutureRepairClass.CLASS_A_GEOMETRY,
        repair_guidance="Rescale viewport margins.",
    )
    d = failure.to_dict()
    assert d["code"] == "TEXT_CLIPPING"
    assert d["severity"] == "CRITICAL"
    assert d["page_indices"] == [2, 3]
    assert d["recommended_future_repair"] == "CLASS_A_GEOMETRY"


def test_02_critical_failure_overrides_high_score():
    """CRITICAL invariant: Critical failures ALWAYS force decision = BLOCKED and can_export = False."""
    inspection = RenderedArtifactInspection.create(
        artifact_type="PRESENTATION",
        rendered_pdf_path="test.pdf",
        page_count=10,
        page_dimensions=(960.0, 540.0),
        structural_metrics=StructuralRenderMetrics(),
        geometry_metrics=GeometryMetrics(text_clipping_instances=2),
        raster_metrics=RasterMetrics(),
        density_metrics=DensityMetrics(),
        hierarchy_metrics=TypographyMetrics(),
        repetition_metrics=CompositionMetrics(),
        artifact_specific_metrics={"artifact_specific_score": 0.95},
        page_details=[],
        failures=[
            RenderedQualityFailure(
                code=RenderedFailureCode.TEXT_CLIPPING,
                severity=RenderedFailureSeverity.CRITICAL,
                artifact_type="PRESENTATION",
                page_indices=(4,),
                description="Catastrophic text clipping",
            )
        ],
    )
    assert inspection.decision == RenderedQualityDecision.BLOCKED
    assert inspection.can_export is False
    assert "Export BLOCKED" in inspection.rationale
    assert inspection.has_critical_failures is True


def test_03_major_warning_forces_needs_repair():
    """MAJOR warnings hold document for repair."""
    inspection = RenderedArtifactInspection.create(
        artifact_type="HANDOUT",
        rendered_pdf_path="test.pdf",
        page_count=4,
        page_dimensions=(595.0, 842.0),
        structural_metrics=StructuralRenderMetrics(),
        geometry_metrics=GeometryMetrics(),
        raster_metrics=RasterMetrics(),
        density_metrics=DensityMetrics(),
        hierarchy_metrics=TypographyMetrics(),
        repetition_metrics=CompositionMetrics(),
        artifact_specific_metrics={"artifact_specific_score": 0.90},
        page_details=[],
        failures=[
            RenderedQualityFailure(
                code=RenderedFailureCode.ORPHAN_HEADING,
                severity=RenderedFailureSeverity.MAJOR,
                artifact_type="HANDOUT",
                page_indices=(2,),
                description="Orphan heading at page break",
            )
        ],
    )
    assert inspection.decision == RenderedQualityDecision.NEEDS_REPAIR
    assert inspection.can_export is False
    assert inspection.has_critical_failures is False


def test_04_minor_warning_allows_pass_with_warnings():
    inspection = RenderedArtifactInspection.create(
        artifact_type="WORKSHEET",
        rendered_pdf_path="test.pdf",
        page_count=3,
        page_dimensions=(595.0, 842.0),
        structural_metrics=StructuralRenderMetrics(),
        geometry_metrics=GeometryMetrics(),
        raster_metrics=RasterMetrics(),
        density_metrics=DensityMetrics(),
        hierarchy_metrics=TypographyMetrics(),
        repetition_metrics=CompositionMetrics(),
        artifact_specific_metrics={"artifact_specific_score": 0.88},
        page_details=[],
        failures=[
            RenderedQualityFailure(
                code=RenderedFailureCode.LAYOUT_MONOTONY,
                severity=RenderedFailureSeverity.MINOR,
                artifact_type="WORKSHEET",
                page_indices=(1, 2),
                description="Mild layout repetition",
            )
        ],
    )
    assert inspection.decision == RenderedQualityDecision.PASS_WITH_WARNINGS
    assert inspection.can_export is True


def test_05_clean_inspection_passes():
    inspection = RenderedArtifactInspection.create(
        artifact_type="SCIENTIFIC_DOCUMENT",
        rendered_pdf_path="test.pdf",
        page_count=6,
        page_dimensions=(595.0, 842.0),
        structural_metrics=StructuralRenderMetrics(),
        geometry_metrics=GeometryMetrics(),
        raster_metrics=RasterMetrics(),
        density_metrics=DensityMetrics(),
        hierarchy_metrics=TypographyMetrics(hierarchy_contrast_score=0.95),
        repetition_metrics=CompositionMetrics(layout_diversity_score=0.92),
        artifact_specific_metrics={"artifact_specific_score": 0.95},
        page_details=[],
        failures=[],
    )
    assert inspection.decision == RenderedQualityDecision.PASS
    assert inspection.can_export is True
    assert inspection.overall_quality_score >= 0.85


def test_06_orthogonal_dimensions_not_hidden():
    """Low score on one dimension remains visible even if overall score is high."""
    inspection = RenderedArtifactInspection.create(
        artifact_type="PRESENTATION",
        rendered_pdf_path="test.pdf",
        page_count=8,
        page_dimensions=(960.0, 540.0),
        structural_metrics=StructuralRenderMetrics(),
        geometry_metrics=GeometryMetrics(),
        raster_metrics=RasterMetrics(),
        density_metrics=DensityMetrics(),
        hierarchy_metrics=TypographyMetrics(hierarchy_contrast_score=0.45),
        repetition_metrics=CompositionMetrics(layout_diversity_score=0.95),
        artifact_specific_metrics={"artifact_specific_score": 0.95},
        page_details=[],
        failures=[],
    )
    assert inspection.dimensional_scores["typographic_hierarchy"] == 0.45
    assert inspection.dimensional_scores["visual_geometry"] == 1.0
