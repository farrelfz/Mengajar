"""
Universal Document Intelligence System V5 — Format-Specific Repair Strategies.

Exports all concrete repair strategies for Presentation, Handout, Worksheet,
and Scientific Document artifacts.
"""

from app.quality.repair.strategies.base import RepairStrategy
from app.quality.repair.strategies.presentation import (
    PresentationDensitySplitStrategy,
    PresentationLayoutRemapStrategy,
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
)
from app.quality.repair.strategies.scientific import (
    ScientificEvidenceMappingStrategy,
    ScientificClaimDowngradeStrategy,
    ScientificLimitationIsolationStrategy,
    ScientificMethodologyOrderStrategy,
)

__all__ = [
    "RepairStrategy",
    "PresentationDensitySplitStrategy",
    "PresentationLayoutRemapStrategy",
    "PresentationPaddingAdjustmentStrategy",
    "HandoutPaginationStrategy",
    "HandoutHierarchyRepairStrategy",
    "HandoutDensityBalanceStrategy",
    "WorksheetAntiSpoilingRepairStrategy",
    "WorksheetInquirySequenceStrategy",
    "WorksheetWorkspaceExpansionStrategy",
    "ScientificEvidenceMappingStrategy",
    "ScientificClaimDowngradeStrategy",
    "ScientificLimitationIsolationStrategy",
    "ScientificMethodologyOrderStrategy",
]
