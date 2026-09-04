"""
Strongly typed contracts and data models for Learning Personalization and Pedagogical Adaptation.
"""

from __future__ import annotations

from enum import Enum
from typing import Any
from pydantic import BaseModel, Field


# ══════════════════════════════════════════════════════════════════════════════
# MULTI-AXIS LEARNER ENUMERATIONS
# ══════════════════════════════════════════════════════════════════════════════


class KnowledgeLevel(str, Enum):
    """Learner's conceptual depth on the target subject."""
    NOVICE = "novice"
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    PROFICIENT = "proficient"
    ADVANCED = "advanced"


class PriorKnowledgeState(str, Enum):
    """State of foundational prerequisite knowledge."""
    NONE = "none"
    FRAGMENTED = "fragmented"
    BASIC = "basic"
    SOLID = "solid"
    STRONG = "strong"


class CognitiveSupportNeed(str, Enum):
    """Degree of instructional guidance required."""
    HIGH_SUPPORT = "high_support"
    GUIDED = "guided"
    MODERATE = "moderate"
    INDEPENDENT = "independent"
    CHALLENGE_ORIENTED = "challenge_oriented"


class AbstractionPreference(str, Enum):
    """Preferred trajectory from concrete experience to formal models."""
    CONCRETE_FIRST = "concrete_first"
    CONCRETE_TO_ABSTRACT = "concrete_to_abstract"
    BALANCED = "balanced"
    ABSTRACT_READY = "abstract_ready"
    FORMAL_FIRST = "formal_first"


class DensityTolerance(str, Enum):
    """Working memory capacity for textual/mathematical volume per unit area."""
    LOW = "low"
    MEDIUM_LOW = "medium_low"
    MEDIUM = "medium"
    MEDIUM_HIGH = "medium_high"
    HIGH = "high"


class PacingPreference(str, Enum):
    """Pacing speed across conceptual stages."""
    SLOW = "slow"
    MODERATE = "moderate"
    FAST = "fast"
    ACCELERATED = "accelerated"


class AssessmentReadiness(str, Enum):
    """Readiness for practice, application, and mastery evaluation."""
    FOUNDATIONAL = "foundational"
    PRACTICE_READY = "practice_ready"
    APPLICATION_READY = "application_ready"
    TRANSFER_READY = "transfer_ready"
    MASTERY_READY = "mastery_ready"


class PreferredRepresentation(str, Enum):
    """Preferred cognitive modal encoding."""
    TEXTUAL = "textual"
    VISUAL = "visual"
    DIAGRAMMATIC = "diagrammatic"
    SYMBOLIC = "symbolic"
    QUANTITATIVE = "quantitative"
    MIXED = "mixed"


class LearningGoalType(str, Enum):
    """Explicit learner objective."""
    UNDERSTAND = "understand"
    PRACTICE = "practice"
    APPLY = "apply"
    ANALYZE = "analyze"
    CREATE = "create"
    PREPARE_FOR_EXAM = "prepare_for_exam"
    CONDUCT_RESEARCH = "conduct_research"
    TEACH_OTHERS = "teach_others"


class AdaptationPolicyType(str, Enum):
    """Macro policy guiding how aggressively to adapt material."""
    CONSERVATIVE = "conservative"
    BALANCED = "balanced"
    AGGRESSIVE = "aggressive"
    ACCESSIBILITY_FIRST = "accessibility_first"
    MASTERY_FIRST = "mastery_first"
    EXPLORATORY = "exploratory"
    EXAM_PREPARATION = "exam_preparation"


class ScaffoldingStrategy(str, Enum):
    """Scaffolding fading strategy."""
    NONE = "none"
    MINIMAL = "minimal"
    GUIDED = "guided"
    STEPWISE = "stepwise"
    FULL_SUPPORT = "full_support"


# ══════════════════════════════════════════════════════════════════════════════
# CORE MODELS
# ══════════════════════════════════════════════════════════════════════════════


class MisconceptionRiskItem(BaseModel):
    concept: str
    risk_level: str = "medium"  # low, medium, high
    suggested_counterexample: str | None = None


class LearnerProfile(BaseModel):
    """
    Multi-axis orthogonal learner profile representing pedagogical needs.
    Not a psychological or demographic model.
    """
    profile_id: str = "default_learner"
    knowledge_level: KnowledgeLevel = KnowledgeLevel.INTERMEDIATE
    prior_knowledge: PriorKnowledgeState = PriorKnowledgeState.BASIC
    cognitive_support: CognitiveSupportNeed = CognitiveSupportNeed.MODERATE
    abstraction_preference: AbstractionPreference = AbstractionPreference.CONCRETE_TO_ABSTRACT
    density_tolerance: DensityTolerance = DensityTolerance.MEDIUM
    pacing: PacingPreference = PacingPreference.MODERATE
    assessment_readiness: AssessmentReadiness = AssessmentReadiness.PRACTICE_READY
    preferred_representations: list[PreferredRepresentation] = Field(
        default_factory=lambda: [PreferredRepresentation.VISUAL, PreferredRepresentation.TEXTUAL]
    )
    learning_goal: LearningGoalType = LearningGoalType.UNDERSTAND
    misconception_risks: list[MisconceptionRiskItem] = Field(default_factory=list)
    custom_attributes: dict[str, Any] = Field(default_factory=dict)


class AdaptationDecision(BaseModel):
    dimension: str
    decision: str
    rationale: str
    confidence: float = 1.0


class AdaptationPlan(BaseModel):
    """
    First-class inspectable contract defining target complexity, sequence pattern,
    scaffolding strategy, preferred capability families, and density bounds.
    """
    plan_id: str
    target_complexity_level: str
    sequence_strategy: str
    scaffolding_strategy: ScaffoldingStrategy
    density_modifier: float = 1.0  # multiplier: 0.7 (less dense) to 1.3 (more dense)
    preferred_capability_families: list[str] = Field(default_factory=list)
    preferred_representations: list[PreferredRepresentation] = Field(default_factory=list)
    example_strategy: str = "concrete_first"
    assessment_strategy: str = "practice"
    insert_misconception_checkpoints: bool = False
    decisions: list[AdaptationDecision] = Field(default_factory=list)


class PersonalizationTrace(BaseModel):
    """Machine-readable trace detailing every pedagogical adaptation decision."""
    profile_id: str
    policy_applied: AdaptationPolicyType
    decisions: list[AdaptationDecision] = Field(default_factory=list)
    constraints_enforced: list[str] = Field(default_factory=list)


class PersonalizationReport(BaseModel):
    """Full execution report emitted by PersonalizationEngine."""
    learner_profile: LearnerProfile
    adaptation_policy: AdaptationPolicyType
    adaptation_plan: AdaptationPlan
    trace: PersonalizationTrace
