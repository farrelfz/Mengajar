"""
KIR AI Document Intelligence — Blueprints Subsystem.

Provides the 3-level Semantic Material Blueprint:
- Level A: Content Blueprint (What should be communicated)
- Level B: Pedagogical Blueprint (Sequence & narrative rationale)
- Level C: Production Blueprint (Capabilities and semantic intents)
"""

from app.blueprints.content import (
    AudienceLevel,
    ConceptDefinition,
    ContentBlueprint,
    ContentMetadata,
    DataBlockContent,
    DataSeries,
    DataSeriesPoint,
    FactStatement,
    KnowledgeDomain,
    LearningObjective,
    MisconceptionItem,
    WorkedExampleContent,
    WorkedExampleStep,
)
from app.blueprints.pedagogical import (
    PedagogicalBlueprint,
    PedagogicalPattern,
    PedagogicalStep,
    SemanticStepType,
)
from app.blueprints.production import (
    ProductionBlueprint,
    ProductionRequirement,
    SemanticIntentSpec,
    TargetArtifactType,
)
from app.blueprints.contracts import SemanticMaterialBlueprint

__all__ = [
    "AudienceLevel",
    "ConceptDefinition",
    "ContentBlueprint",
    "ContentMetadata",
    "DataBlockContent",
    "DataSeries",
    "DataSeriesPoint",
    "FactStatement",
    "KnowledgeDomain",
    "LearningObjective",
    "MisconceptionItem",
    "WorkedExampleContent",
    "WorkedExampleStep",
    "PedagogicalBlueprint",
    "PedagogicalPattern",
    "PedagogicalStep",
    "SemanticStepType",
    "ProductionBlueprint",
    "ProductionRequirement",
    "SemanticIntentSpec",
    "TargetArtifactType",
    "SemanticMaterialBlueprint",
]
