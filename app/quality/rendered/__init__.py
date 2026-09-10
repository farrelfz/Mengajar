"""
Universal Document Intelligence System V5 — Rendered Output Quality Intelligence.

Phase 3A: Independent, adversarial post-render inspection layer across:
- Presentation
- Handout
- Worksheet
- Scientific Document
"""

from app.quality.rendered.composition_fingerprint import (
    CompositionFingerprintEngine,
    PageCompositionFingerprint,
    RepetitionStreak,
)
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
from app.quality.rendered.handout_quality import HandoutRenderedQualityEvaluator
from app.quality.rendered.pdf_inspector import (
    PageGeometryAnalysis,
    PDFGeometryInspector,
)
from app.quality.rendered.presentation_quality import (
    PresentationRenderedQualityEvaluator,
)
from app.quality.rendered.quality_engine import MasterRenderedQualityEngine
from app.quality.rendered.quality_reporter import RenderedQualityReporter
from app.quality.rendered.raster_inspector import (
    PageRasterAnalysis,
    RasterImageInspector,
)
from app.quality.rendered.scientific_quality import (
    ScientificRenderedQualityEvaluator,
)
from app.quality.rendered.typography_density import (
    ContentDensityResult,
    TypographyAnalysisResult,
    TypographyDensityAnalyzer,
)
from app.quality.rendered.whitespace_model import (
    WhitespaceEvaluation,
    WhitespaceIntentModel,
)
from app.quality.rendered.worksheet_quality import (
    WorksheetRenderedQualityEvaluator,
)

__all__ = [
    "FutureRepairClass",
    "RenderedFailureCode",
    "RenderedFailureSeverity",
    "RenderedQualityFailure",
    "CompositionMetrics",
    "DensityMetrics",
    "GeometryMetrics",
    "PageInspectionDetail",
    "RasterMetrics",
    "RenderedArtifactInspection",
    "RenderedQualityDecision",
    "StructuralRenderMetrics",
    "TypographyMetrics",
    "PageCompositionFingerprint",
    "RepetitionStreak",
    "CompositionFingerprintEngine",
    "PageGeometryAnalysis",
    "PDFGeometryInspector",
    "PageRasterAnalysis",
    "RasterImageInspector",
    "TypographyAnalysisResult",
    "ContentDensityResult",
    "TypographyDensityAnalyzer",
    "WhitespaceEvaluation",
    "WhitespaceIntentModel",
    "PresentationRenderedQualityEvaluator",
    "HandoutRenderedQualityEvaluator",
    "WorksheetRenderedQualityEvaluator",
    "ScientificRenderedQualityEvaluator",
    "MasterRenderedQualityEngine",
    "RenderedQualityReporter",
]
