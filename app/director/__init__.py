"""
KIR AI Document Intelligence — Intelligent Material Director Subsystem.

Provides autonomous pedagogical direction, narrative journey planning,
cognitive complexity modeling, stage transition grammar, and capability choreography.
"""

from app.director.choreography import PedagogicalChoreographer
from app.director.cognition import CognitiveProgressionPolicy
from app.director.contracts import (
    AudienceProfile,
    CapabilityRequirement,
    CognitiveLevel,
    DensityBudget,
    DirectorDiagnostics,
    DirectorTrace,
    InstructionalIntent,
    KnowledgeState,
    LearningGoal,
    LearningJourney,
    LearningStage,
    LearningStageType,
    MaterialDirection,
    MaterialStrategyType,
)
from app.director.director import IntelligentMaterialDirector
from app.director.journey import LearningJourneyBuilder
from app.director.misconceptions import MisconceptionDetector, MisconceptionOpportunity
from app.director.policies import (
    BaseDomainPolicy,
    DomainPolicyRegistry,
    get_default_policy_registry,
)
from app.director.strategies import STRATEGY_REGISTRY, MaterialStrategyDefinition, get_strategy_definition
from app.director.validators import StageTransitionPolicy

__all__ = [
    "AudienceProfile",
    "BaseDomainPolicy",
    "CapabilityRequirement",
    "CognitiveLevel",
    "CognitiveProgressionPolicy",
    "DensityBudget",
    "DirectorDiagnostics",
    "DirectorTrace",
    "DomainPolicyRegistry",
    "InstructionalIntent",
    "IntelligentMaterialDirector",
    "KnowledgeState",
    "LearningGoal",
    "LearningJourney",
    "LearningJourneyBuilder",
    "LearningStage",
    "LearningStageType",
    "MaterialDirection",
    "MaterialStrategyDefinition",
    "MaterialStrategyType",
    "MisconceptionDetector",
    "MisconceptionOpportunity",
    "PedagogicalChoreographer",
    "StageTransitionPolicy",
    "STRATEGY_REGISTRY",
    "get_default_policy_registry",
    "get_strategy_definition",
]
