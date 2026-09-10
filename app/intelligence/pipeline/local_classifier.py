"""
Stage 3 — LocalClassifier.

Applies deterministic syntax rules, math patterns, table structures, and lexical signals
to classify CandidateUnits into ContentTypes without calling AI models.
"""

from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, Field

from app.intelligence.pipeline.unit_normalizer import CandidateUnit
from app.intelligence.rule_classifier import RuleClassifier
from app.intelligence.schemas import ContentType, ContentUnit
from app.intelligence.schemas.knowledge_unit import KnowledgeCategory


class RuleClassifiedUnit(BaseModel):
    candidate: CandidateUnit
    content_type: ContentType
    category: KnowledgeCategory
    confidence: float
    is_ambiguous: bool
    classification_reasons: List[str] = Field(default_factory=list)

    @property
    def local_confidence(self) -> float:
        return self.confidence

    @local_confidence.setter
    def local_confidence(self, val: float) -> None:
        self.confidence = val


class LocalClassifier:
    """Stage 3: Fast, 100% deterministic rule-based semantic classifier."""

    def __init__(self, rule_engine: RuleClassifier | None = None) -> None:
        self.rule_engine = rule_engine or RuleClassifier()

    def classify(self, candidate_units: List[CandidateUnit]) -> List[RuleClassifiedUnit]:
        classified: List[RuleClassifiedUnit] = []

        for cand in candidate_units:
            # Map candidate to temp ContentUnit for RuleClassifier
            temp_unit = ContentUnit(
                unit_id=cand.candidate_id,
                title=cand.parent_section_title,
                raw_text=cand.raw_content,
                normalized_text=cand.normalized_content,
                source_heading=cand.parent_section_title,
                source_order=cand.provenance.source_start_line or 0,
            )

            res = self.rule_engine.classify_unit(
                unit=temp_unit,
                parent_heading=cand.parent_section_title,
            )

            # Map ContentType to KnowledgeCategory
            c_type = res.content_type
            category = self._derive_category(c_type)

            classified.append(
                RuleClassifiedUnit(
                    candidate=cand,
                    content_type=c_type,
                    category=category,
                    confidence=res.confidence,
                    is_ambiguous=res.is_ambiguous,
                    classification_reasons=res.reasons,
                )
            )

        return classified

    def _derive_category(self, c_type: ContentType) -> KnowledgeCategory:
        if c_type in (ContentType.DEFINITION, ContentType.CONCEPT, ContentType.THEORY, ContentType.BACKGROUND, ContentType.TITLE):
            return KnowledgeCategory.CORE_CONCEPT
        elif c_type in (ContentType.PROCEDURE, ContentType.METHOD, ContentType.PROCESS, ContentType.INSTRUCTION, ContentType.SEQUENCE):
            return KnowledgeCategory.PROCEDURAL
        elif c_type in (ContentType.DATA, ContentType.EVIDENCE, ContentType.RESULT, ContentType.FINDING):
            return KnowledgeCategory.EMPIRICAL
        elif c_type in (ContentType.FORMULA,):
            return KnowledgeCategory.FORMAL
        elif c_type in (ContentType.ARGUMENT, ContentType.ANALYSIS, ContentType.DISCUSSION, ContentType.CONCLUSION, ContentType.LIMITATION, ContentType.IMPLICATION):
            return KnowledgeCategory.EVALUATIVE
        elif c_type in (ContentType.QUESTION, ContentType.WARNING, ContentType.REFLECTION, ContentType.PROBLEM, ContentType.HYPOTHESIS, ContentType.ACTIVITY):
            return KnowledgeCategory.STIMULUS
        return KnowledgeCategory.CORE_CONCEPT
