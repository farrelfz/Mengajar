"""
Pluggable Refinement Strategies: Modular handlers for specific refinement intents.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from app.refinement.contracts import RefinementAction, RefinementIntent
from app.refinement.patches import (
    BaseRefinementPatch,
    CapabilityReplacementPatch,
    DensitySplitPatch,
    PedagogicalSequencePatch,
    RedundancyDeduplicationPatch,
)


class BaseRefinementStrategy(ABC):
    """Abstract base for refinement strategies."""

    @abstractmethod
    def can_handle(self, action: RefinementAction) -> bool:
        pass

    @abstractmethod
    def create_patch(self, action: RefinementAction) -> BaseRefinementPatch:
        pass


class PedagogicalRefinementStrategy(BaseRefinementStrategy):
    def can_handle(self, action: RefinementAction) -> bool:
        return action.intent in [RefinementIntent.REORDER, RefinementIntent.ADD_SCAFFOLDING]

    def create_patch(self, action: RefinementAction) -> BaseRefinementPatch:
        return PedagogicalSequencePatch(action)


class DensityRefinementStrategy(BaseRefinementStrategy):
    def can_handle(self, action: RefinementAction) -> bool:
        return action.intent in [RefinementIntent.REBALANCE_DENSITY, RefinementIntent.CONDENSE]

    def create_patch(self, action: RefinementAction) -> BaseRefinementPatch:
        return DensitySplitPatch(action)


class CapabilityRefinementStrategy(BaseRefinementStrategy):
    def can_handle(self, action: RefinementAction) -> bool:
        return action.intent == RefinementIntent.REPLACE_CAPABILITY

    def create_patch(self, action: RefinementAction) -> BaseRefinementPatch:
        return CapabilityReplacementPatch(action)


class RedundancyRefinementStrategy(BaseRefinementStrategy):
    def can_handle(self, action: RefinementAction) -> bool:
        return action.intent == RefinementIntent.REMOVE_REDUNDANCY

    def create_patch(self, action: RefinementAction) -> BaseRefinementPatch:
        return RedundancyDeduplicationPatch(action)
