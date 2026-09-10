"""
Universal Knowledge Core — Transformation Contract Package.

Phase 1C:
Semantic transformation layer mapping UniversalKnowledgeManifest to
artifact-specific semantic blueprints (Presentation, Handout, Worksheet, Scientific Document).
"""

from app.intelligence.transformation.intent import (
    ArtifactType,
    AudienceLevel,
    ResolvedArtifactIntent,
    UncertaintyHandlingPolicy,
    get_default_intent,
)
from app.intelligence.transformation.blueprints import (
    ArtifactBlueprint,
    ConceptualBeat,
    ExplanatorySection,
    HandoutBlueprint,
    LearningActivity,
    LearningActivityType,
    PresentationBlueprint,
    ScientificArgumentRole,
    ScientificArgumentUnit,
    ScientificDocumentBlueprint,
    WorksheetBlueprint,
)
from app.intelligence.transformation.selection import (
    KnowledgeSelectionEngine,
    SelectedKnowledgeSet,
)
from app.intelligence.transformation.transformers import (
    HandoutTransformer,
    PresentationTransformer,
    ScientificDocumentTransformer,
    WorksheetTransformer,
)
from app.intelligence.transformation.differentiation_validator import (
    ArtifactDifferentiationValidator,
    DifferentiationValidationResult,
)
from app.intelligence.transformation.traceability import (
    BlueprintTraceabilityReport,
    ElementTraceabilityRecord,
    TransformationTraceabilityEngine,
)

__all__ = [
    "ArtifactType",
    "AudienceLevel",
    "ResolvedArtifactIntent",
    "UncertaintyHandlingPolicy",
    "get_default_intent",
    "ArtifactBlueprint",
    "ConceptualBeat",
    "ExplanatorySection",
    "HandoutBlueprint",
    "LearningActivity",
    "LearningActivityType",
    "PresentationBlueprint",
    "ScientificArgumentRole",
    "ScientificArgumentUnit",
    "ScientificDocumentBlueprint",
    "WorksheetBlueprint",
    "KnowledgeSelectionEngine",
    "SelectedKnowledgeSet",
    "PresentationTransformer",
    "HandoutTransformer",
    "WorksheetTransformer",
    "ScientificDocumentTransformer",
    "ArtifactDifferentiationValidator",
    "DifferentiationValidationResult",
    "ElementTraceabilityRecord",
    "BlueprintTraceabilityReport",
    "TransformationTraceabilityEngine",
]
