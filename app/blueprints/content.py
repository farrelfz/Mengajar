"""
KIR AI Document Intelligence — Content Blueprint (Level A).

Answers: WHAT should be communicated?
Contains topics, concepts, definitions, facts, arguments, examples, questions, data, and conclusions.
"""

from __future__ import annotations

import uuid
from enum import Enum
from typing import Any
from pydantic import BaseModel, Field


class AudienceLevel(str, Enum):
    BEGINNER = "beginner"
    MIDDLE_SCHOOL = "middle_school"
    HIGH_SCHOOL = "high_school"
    UNDERGRADUATE = "undergraduate"
    RESEARCHER = "researcher"
    GENERAL_PUBLIC = "general_public"


class KnowledgeDomain(str, Enum):
    PHYSICS = "physics"
    MATHEMATICS = "mathematics"
    RESEARCH_METHODOLOGY = "research_methodology"
    EXPERIMENT_KIR = "experiment_kir"
    COMPUTER_SCIENCE = "computer_science"
    BIOLOGY = "biology"
    CHEMISTRY = "chemistry"
    GENERAL_SCIENCE = "general_science"
    EDUCATION = "education"


class ContentMetadata(BaseModel):
    title: str
    domain: KnowledgeDomain = KnowledgeDomain.GENERAL_SCIENCE
    audience: AudienceLevel = AudienceLevel.HIGH_SCHOOL
    purpose: str = "teaching"
    duration_minutes: int | None = None
    tags: list[str] = Field(default_factory=list)
    custom_metadata: dict[str, Any] = Field(default_factory=dict)


class LearningObjective(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    objective: str
    level: str = "conceptual"  # conceptual, procedural, analytical, evaluative
    target_concept: str | None = None


class ConceptDefinition(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    formal_definition: str
    intuitive_explanation: str | None = None
    symbol: str | None = None
    si_unit: str | None = None
    formula: str | None = None


class FactStatement(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    statement: str
    context: str | None = None
    supporting_evidence: str | None = None


class MisconceptionItem(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    common_belief: str
    why_it_seems_true: str
    counterexample: str
    correct_explanation: str


class WorkedExampleStep(BaseModel):
    step_number: int
    description: str
    math_or_code: str | None = None
    rationale: str | None = None


class WorkedExampleContent(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    problem_statement: str
    knowns: dict[str, str] = Field(default_factory=dict)
    unknowns: list[str] = Field(default_factory=list)
    principles_used: list[str] = Field(default_factory=list)
    steps: list[WorkedExampleStep] = Field(default_factory=list)
    final_answer: str
    interpretation: str | None = None


class DataSeriesPoint(BaseModel):
    label: str
    value: float
    uncertainty: float | None = None


class DataSeries(BaseModel):
    name: str
    points: list[DataSeriesPoint] = Field(default_factory=list)


class DataBlockContent(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    x_label: str
    y_label: str
    series: list[DataSeries] = Field(default_factory=list)
    key_takeaway: str | None = None


class ContentBlueprint(BaseModel):
    """Level A Content Blueprint: Declarative representation of knowledge assets."""
    blueprint_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    metadata: ContentMetadata
    objectives: list[LearningObjective] = Field(default_factory=list)
    concepts: list[ConceptDefinition] = Field(default_factory=list)
    facts: list[FactStatement] = Field(default_factory=list)
    misconceptions: list[MisconceptionItem] = Field(default_factory=list)
    worked_examples: list[WorkedExampleContent] = Field(default_factory=list)
    datasets: list[DataBlockContent] = Field(default_factory=list)
    summary_points: list[str] = Field(default_factory=list)
