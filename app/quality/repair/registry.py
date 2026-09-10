"""
Universal Document Intelligence System V5 — Repair Strategy Registry.

Phase 3B: Central deterministic registry indexing repair strategies by artifact type,
failure codes, root cause categories, and mutation classes.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Sequence

from app.quality.repair.contracts import RepairMutationClass
from app.quality.repair.root_cause import RootCauseType
from app.quality.repair.strategies.base import RepairStrategy


class RepairStrategyRegistry:
    """Deterministic registry indexing all available repair strategies."""

    def __init__(self) -> None:
        self._strategies: Dict[str, RepairStrategy] = {}

    def register(self, strategy: RepairStrategy) -> None:
        """Registers a repair strategy into the registry."""
        self._strategies[strategy.strategy_id] = strategy

    def get_strategy(self, strategy_id: str) -> Optional[RepairStrategy]:
        """Retrieves a strategy by its unique ID."""
        return self._strategies.get(strategy_id)

    def find_strategies(
        self,
        artifact_type: str,
        failure_code: str,
        root_cause: RootCauseType,
        forbidden_classes: Sequence[RepairMutationClass] = (),
    ) -> List[RepairStrategy]:
        """Finds all matching strategies ordered by minimal mutation cost and priority."""
        matches = []
        forbidden_set = set(forbidden_classes)

        for strat in self._strategies.values():
            if strat.mutation_class in forbidden_set:
                continue
            if strat.supports(artifact_type, failure_code, root_cause):
                matches.append(strat)

        # Sort deterministically: lower priority first, then lower mutation cost
        matches.sort(key=lambda s: (s.priority, s.mutation_cost, s.strategy_id))
        return matches

    def all_strategies(self) -> List[RepairStrategy]:
        """Returns all registered strategies."""
        return list(self._strategies.values())

    def clear(self) -> None:
        """Clears all registered strategies (useful in test isolation)."""
        self._strategies.clear()


def register_default_strategies(registry: RepairStrategyRegistry) -> None:
    """Populates registry with all format-specific canonical strategies."""
    from app.quality.repair.strategies.presentation import (
        PresentationDensitySplitStrategy,
        PresentationLayoutRemapStrategy,
        PresentationComponentReflowStrategy,
        PresentationPaddingAdjustmentStrategy,
    )
    from app.quality.repair.strategies.handout import (
        HandoutPaginationStrategy,
        HandoutHierarchyRepairStrategy,
        HandoutDensityBalanceStrategy,
    )
    from app.quality.repair.strategies.worksheet import (
        WorksheetAntiSpoilingRepairStrategy,
        WorksheetInquirySequenceStrategy,
        WorksheetWorkspaceExpansionStrategy,
        WorksheetTypographyScaleStrategy,
        WorksheetLayoutAlternationStrategy,
    )
    from app.quality.repair.strategies.scientific import (
        ScientificEvidenceMappingStrategy,
        ScientificClaimDowngradeStrategy,
        ScientificLimitationIsolationStrategy,
        ScientificMethodologyOrderStrategy,
        ScientificCitationLinkingStrategy,
    )

    strategies = [
        # Presentation
        PresentationDensitySplitStrategy(),
        PresentationLayoutRemapStrategy(),
        PresentationComponentReflowStrategy(),
        PresentationPaddingAdjustmentStrategy(),
        # Handout
        HandoutPaginationStrategy(),
        HandoutHierarchyRepairStrategy(),
        HandoutDensityBalanceStrategy(),
        # Worksheet
        WorksheetAntiSpoilingRepairStrategy(),
        WorksheetInquirySequenceStrategy(),
        WorksheetWorkspaceExpansionStrategy(),
        WorksheetTypographyScaleStrategy(),
        WorksheetLayoutAlternationStrategy(),
        # Scientific Document
        ScientificEvidenceMappingStrategy(),
        ScientificClaimDowngradeStrategy(),
        ScientificLimitationIsolationStrategy(),
        ScientificMethodologyOrderStrategy(),
        ScientificCitationLinkingStrategy(),
    ]

    for s in strategies:
        registry.register(s)


# Global Canonical Strategy Registry with all defaults populated
DEFAULT_STRATEGY_REGISTRY = RepairStrategyRegistry()
register_default_strategies(DEFAULT_STRATEGY_REGISTRY)
