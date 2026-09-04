"""
KIR AI Document Intelligence — Pedagogical & Narrative Blueprint (Level B).

Answers: IN WHAT SEQUENCE and WHY should information be communicated?
Encapsulates pedagogical arcs, cognitive scaffolding, and narrative flow.
"""

from __future__ import annotations

import uuid
from enum import Enum
from typing import Any
from pydantic import BaseModel, Field


class PedagogicalPattern(str, Enum):
    QUESTION_TO_ANSWER = "question_to_answer"
    CONCRETE_TO_ABSTRACT = "concrete_to_abstract"
    MISCONCEPTION_CORRECTION = "misconception_correction"
    WORKED_EXAMPLE = "worked_example"
    SCIENTIFIC_REASONING = "scientific_reasoning"
    PROBLEM_TO_SOLUTION = "problem_to_solution"
    CLAIM_EVIDENCE_REASONING = "claim_evidence_reasoning"
    LINEAR_EXPLANATION = "linear_explanation"


class SemanticStepType(str, Enum):
    HOOK = "hook"
    QUESTION = "question"
    PHENOMENON = "phenomenon"
    OBSERVATION = "observation"
    CONCEPT = "concept"
    VISUALIZATION = "visualization"
    MATHEMATICAL_MODEL = "mathematical_model"
    DERIVATION = "derivation"
    WORKED_EXAMPLE = "worked_example"
    MISCONCEPTION = "misconception"
    PRACTICE = "practice"
    COMPARISON = "comparison"
    CASE_STUDY = "case_study"
    SUMMARY = "summary"
    REFLECTION = "reflection"
    CLOSING = "closing"


class PedagogicalStep(BaseModel):
    """An individual step in the pedagogical sequence."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    semantic_type: SemanticStepType
    purpose: str
    target_concept_id: str | None = None
    content_ref_ids: list[str] = Field(default_factory=list)
    visual_intent: str | None = None
    duration_estimate_minutes: int | None = None
    notes: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class PedagogicalBlueprint(BaseModel):
    """Level B Pedagogical Blueprint: Structured narrative sequence."""
    blueprint_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    primary_pattern: PedagogicalPattern = PedagogicalPattern.CONCRETE_TO_ABSTRACT
    narrative_rationale: str
    target_cognitive_load: str = "balanced"  # low, balanced, high
    sequence: list[PedagogicalStep] = Field(default_factory=list)
