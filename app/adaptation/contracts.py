"""
Adaptive Content Intelligence & Learner Modeling — Core Contracts.

Defines multi-dimensional learner profiles, complexity matrices, time budgets,
shared learning objectives, and explainable adaptation traces.
"""

from __future__ import annotations

from enum import Enum
from typing import Any
from pydantic import BaseModel, Field

from app.blueprints.content import AudienceLevel
from app.director.contracts import CognitiveLevel, KnowledgeState


class ComplexityLevel(str, Enum):
    """5-Tier canonical scale of academic complexity and abstraction."""
    FOUNDATIONAL = "foundational"       # Middle school / introductory intuition
    INTRODUCTORY = "introductory"       # Early high school / basic models
    INTERMEDIATE = "intermediate"       # Upper high school / standard quantitative models
    ADVANCED = "advanced"               # Undergraduate / rigorous formalisms & derivations
    EXPERT = "expert"                   # Graduate / research level / generalized tensors


class ContentComplexityProfile(BaseModel):
    """10-Dimensional explicit complexity profile governing content generation."""
    abstraction_level: ComplexityLevel = ComplexityLevel.INTERMEDIATE
    conceptual_depth: ComplexityLevel = ComplexityLevel.INTERMEDIATE
    vocabulary_complexity: ComplexityLevel = ComplexityLevel.INTERMEDIATE
    mathematical_formalism: ComplexityLevel = ComplexityLevel.INTERMEDIATE
    reasoning_complexity: ComplexityLevel = ComplexityLevel.INTERMEDIATE
    example_complexity: ComplexityLevel = ComplexityLevel.INTERMEDIATE
    evidence_requirement: ComplexityLevel = ComplexityLevel.INTERMEDIATE
    task_open_endedness: ComplexityLevel = ComplexityLevel.INTERMEDIATE
    prerequisite_dependency: ComplexityLevel = ComplexityLevel.INTERMEDIATE
    misconception_depth: ComplexityLevel = ComplexityLevel.INTERMEDIATE


class LearnerProfile(BaseModel):
    """Comprehensive multi-dimensional model of learner readiness and background."""
    educational_level: AudienceLevel = AudienceLevel.HIGH_SCHOOL
    age_band: str = "15-18"
    knowledge_state: KnowledgeState = KnowledgeState.NOVICE
    prerequisite_mastery: dict[str, bool] = Field(default_factory=dict)
    mathematical_readiness: ComplexityLevel = ComplexityLevel.INTERMEDIATE
    scientific_reasoning_level: ComplexityLevel = ComplexityLevel.INTERMEDIATE
    vocabulary_level: ComplexityLevel = ComplexityLevel.INTERMEDIATE
    cognitive_readiness: CognitiveLevel = CognitiveLevel.UNDERSTAND


class InstructionalTimeBudget(BaseModel):
    """Explicit temporal envelope governing pedagogical pacing and journey length."""
    duration_minutes: int = 45
    pacing_mode: str = "standard_lesson"  # rapid_briefing (10-15m), standard_lesson (30-45m), deep_mastery (60-90m+)


class SharedLearningObjective(BaseModel):
    """Atomic, traceable educational outcome shared across all bundle artifacts."""
    objective_id: str
    statement: str
    cognitive_level: CognitiveLevel = CognitiveLevel.UNDERSTAND
    target_concept: str
    mastery_criteria: str = ""


class AdaptationTrace(BaseModel):
    """Machine-readable explainability record detailing every adaptation decision."""
    learner_profile: dict[str, Any] = Field(default_factory=dict)
    complexity_adjustments: list[dict[str, Any]] = Field(default_factory=list)
    prerequisite_actions: list[dict[str, Any]] = Field(default_factory=list)
    vocabulary_transformations: list[dict[str, str]] = Field(default_factory=list)
    formula_transformations: list[dict[str, str]] = Field(default_factory=list)
    duration_adjustments: list[dict[str, Any]] = Field(default_factory=list)
