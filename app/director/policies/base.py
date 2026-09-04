"""
Base Domain Direction Policy contract and registry.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any
from pydantic import BaseModel, Field

from app.capabilities.taxonomy import CapabilityFamily, VisualGrammar
from app.director.contracts import (
    AudienceProfile,
    InstructionalIntent,
    LearningGoal,
    MaterialStrategyType,
)


class BaseDomainPolicy(ABC):
    """Abstract base class for domain-specific pedagogical and narrative direction policies."""

    domain_name: str = "general"
    preferred_strategies: list[MaterialStrategyType] = [
        MaterialStrategyType.CONCRETE_TO_ABSTRACT,
        MaterialStrategyType.QUICK_EXPLANATION,
    ]
    preferred_families: list[CapabilityFamily] = [
        CapabilityFamily.CONCEPT_STRUCTURE,
        CapabilityFamily.PROCESS_VISUALIZATION,
    ]
    preferred_visual_grammars: list[VisualGrammar] = [
        VisualGrammar.CONCEPT_PANEL,
        VisualGrammar.PROCESS_FLOW,
    ]

    def evaluate_strategy_fit(
        self,
        strategy: MaterialStrategyType,
        goal: LearningGoal,
        audience: AudienceProfile,
        intent: InstructionalIntent,
        format_id: str,
    ) -> float:
        """
        Calculates a compatibility score [0.0 - 1.0] for a strategy given goal, audience, and format.
        """
        score = 0.5

        if strategy in self.preferred_strategies:
            score += 0.3

        # Intent alignment
        if intent == InstructionalIntent.TEACH and strategy in [
            MaterialStrategyType.CONCRETE_TO_ABSTRACT,
            MaterialStrategyType.MISCONCEPTION_CORRECTION,
            MaterialStrategyType.WORKED_EXAMPLE_PROGRESSIVE,
        ]:
            score += 0.15
        elif intent == InstructionalIntent.EXPLAIN and strategy in [
            MaterialStrategyType.QUICK_EXPLANATION,
            MaterialStrategyType.CONCEPTUAL_DISCOVERY,
        ]:
            score += 0.15
        elif intent == InstructionalIntent.PRACTICE and strategy in [
            MaterialStrategyType.WORKED_EXAMPLE_PROGRESSIVE,
            MaterialStrategyType.EXAM_PREPARATION,
        ]:
            score += 0.15

        # Format considerations
        if format_id == "presentation_16_9" and strategy in [
            MaterialStrategyType.PRESENTATION_STORY,
            MaterialStrategyType.QUICK_EXPLANATION,
            MaterialStrategyType.CONCRETE_TO_ABSTRACT,
        ]:
            score += 0.1

        return min(1.0, score)


class DomainPolicyRegistry:
    """Registry maintaining active domain direction policies."""

    def __init__(self) -> None:
        self._policies: dict[str, BaseDomainPolicy] = {}

    def register(self, policy: BaseDomainPolicy) -> None:
        self._policies[policy.domain_name.lower()] = policy

    def get(self, domain_name: str) -> BaseDomainPolicy:
        key = domain_name.lower()
        if key in self._policies:
            return self._policies[key]
        return self._policies.get("general", DefaultDomainPolicy())

    def list_domains(self) -> list[str]:
        return list(self._policies.keys())


class DefaultDomainPolicy(BaseDomainPolicy):
    domain_name = "general"
