"""
Adaptation Policies: Centralized macro strategies for steering personalized adaptations.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any
from app.personalization.contracts import (
    AdaptationPolicyType,
    CognitiveSupportNeed,
    DensityTolerance,
    KnowledgeLevel,
    LearnerProfile,
    LearningGoalType,
    ScaffoldingStrategy,
)


class BaseAdaptationPolicy(ABC):
    """Abstract base for personalization adaptation policies."""

    @property
    @abstractmethod
    def policy_type(self) -> AdaptationPolicyType:
        pass

    @abstractmethod
    def resolve_density_modifier(self, profile: LearnerProfile) -> float:
        pass

    @abstractmethod
    def resolve_scaffolding(self, profile: LearnerProfile) -> ScaffoldingStrategy:
        pass


class BalancedPolicy(BaseAdaptationPolicy):
    @property
    def policy_type(self) -> AdaptationPolicyType:
        return AdaptationPolicyType.BALANCED

    def resolve_density_modifier(self, profile: LearnerProfile) -> float:
        if profile.density_tolerance == DensityTolerance.LOW:
            return 0.8
        elif profile.density_tolerance == DensityTolerance.HIGH:
            return 1.2
        return 1.0

    def resolve_scaffolding(self, profile: LearnerProfile) -> ScaffoldingStrategy:
        if profile.cognitive_support == CognitiveSupportNeed.HIGH_SUPPORT:
            return ScaffoldingStrategy.FULL_SUPPORT
        elif profile.cognitive_support == CognitiveSupportNeed.GUIDED:
            return ScaffoldingStrategy.GUIDED
        elif profile.cognitive_support == CognitiveSupportNeed.CHALLENGE_ORIENTED:
            return ScaffoldingStrategy.MINIMAL
        return ScaffoldingStrategy.GUIDED


class AccessibilityFirstPolicy(BaseAdaptationPolicy):
    @property
    def policy_type(self) -> AdaptationPolicyType:
        return AdaptationPolicyType.ACCESSIBILITY_FIRST

    def resolve_density_modifier(self, profile: LearnerProfile) -> float:
        return 0.75

    def resolve_scaffolding(self, profile: LearnerProfile) -> ScaffoldingStrategy:
        return ScaffoldingStrategy.FULL_SUPPORT


class MasteryFirstPolicy(BaseAdaptationPolicy):
    @property
    def policy_type(self) -> AdaptationPolicyType:
        return AdaptationPolicyType.MASTERY_FIRST

    def resolve_density_modifier(self, profile: LearnerProfile) -> float:
        return 1.25

    def resolve_scaffolding(self, profile: LearnerProfile) -> ScaffoldingStrategy:
        return ScaffoldingStrategy.MINIMAL


class ExamPreparationPolicy(BaseAdaptationPolicy):
    @property
    def policy_type(self) -> AdaptationPolicyType:
        return AdaptationPolicyType.EXAM_PREPARATION

    def resolve_density_modifier(self, profile: LearnerProfile) -> float:
        return 1.1

    def resolve_scaffolding(self, profile: LearnerProfile) -> ScaffoldingStrategy:
        return ScaffoldingStrategy.STEPWISE


class AdaptationPolicyRegistry:
    """Registry of adaptation policies."""

    _POLICIES: dict[AdaptationPolicyType, BaseAdaptationPolicy] = {
        AdaptationPolicyType.BALANCED: BalancedPolicy(),
        AdaptationPolicyType.ACCESSIBILITY_FIRST: AccessibilityFirstPolicy(),
        AdaptationPolicyType.MASTERY_FIRST: MasteryFirstPolicy(),
        AdaptationPolicyType.EXAM_PREPARATION: ExamPreparationPolicy(),
        AdaptationPolicyType.CONSERVATIVE: BalancedPolicy(),
    }

    @classmethod
    def get_policy(cls, policy_type: AdaptationPolicyType) -> BaseAdaptationPolicy:
        return cls._POLICIES.get(policy_type, BalancedPolicy())
