"""
Universal Document Intelligence System V5 — Blueprint Validation Module.

Phase 4.1: Deterministic upstream validation of Markdown-derived artifact blueprints.
Operates before Python transformation pipeline. Signal layer only — NOT export authority.
"""

from .contracts import BlueprintFailureType, BlueprintValidationReport
from .validators import (
    PresentationBlueprintValidator,
    HandoutBlueprintValidator,
    WorksheetBlueprintValidator,
    ScientificDocumentBlueprintValidator,
)
from .anti_pattern_detector import BlueprintAntiPatternDetector

__all__ = [
    "BlueprintFailureType",
    "BlueprintValidationReport",
    "PresentationBlueprintValidator",
    "HandoutBlueprintValidator",
    "WorksheetBlueprintValidator",
    "ScientificDocumentBlueprintValidator",
    "BlueprintAntiPatternDetector",
]
