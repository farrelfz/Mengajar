"""
KIR AI Document Intelligence — Adaptive Content Intelligence Subsystem.
"""

from app.adaptation.adaptation import AdaptiveContentTransformer
from app.adaptation.contracts import (
    AdaptationTrace,
    ComplexityLevel,
    ContentComplexityProfile,
    InstructionalTimeBudget,
    LearnerProfile,
    SharedLearningObjective,
)
from app.adaptation.pacing import PacingPolicy
from app.adaptation.prerequisites import ConceptPrerequisiteGraph
from app.adaptation.profiles import ComplexityPolicy, get_default_learner_profile
from app.adaptation.vocabulary import VocabularyTransformer

__all__ = [
    "AdaptationTrace",
    "AdaptiveContentTransformer",
    "ComplexityLevel",
    "ComplexityPolicy",
    "ConceptPrerequisiteGraph",
    "ContentComplexityProfile",
    "InstructionalTimeBudget",
    "LearnerProfile",
    "PacingPolicy",
    "SharedLearningObjective",
    "VocabularyTransformer",
    "get_default_learner_profile",
]
