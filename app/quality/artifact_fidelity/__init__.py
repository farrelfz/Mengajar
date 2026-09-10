"""
Universal Knowledge Core — Artifact Fidelity Evaluation Package.

Phase 2B Controlled Renderer Execution & Artifact Fidelity:
Comprehensive evaluation framework verifying semantic preservation, structural
adherence, active learning/scientific integrity, visual quality, and bidirectional
traceability.
"""

from app.quality.artifact_fidelity.base import (
    ArtifactFidelityEvaluation,
    BaseArtifactFidelityValidator,
)
from app.quality.artifact_fidelity.fidelity_report import ComprehensiveFidelityReport
from app.quality.artifact_fidelity.handout_fidelity import HandoutFidelityValidator
from app.quality.artifact_fidelity.presentation_fidelity import PresentationFidelityValidator
from app.quality.artifact_fidelity.scientific_fidelity import (
    ScientificDocumentFidelityValidator,
)
from app.quality.artifact_fidelity.unified_fidelity_validator import (
    UnifiedFidelityValidator,
)
from app.quality.artifact_fidelity.worksheet_fidelity import WorksheetFidelityValidator

__all__ = [
    "ArtifactFidelityEvaluation",
    "BaseArtifactFidelityValidator",
    "PresentationFidelityValidator",
    "HandoutFidelityValidator",
    "WorksheetFidelityValidator",
    "ScientificDocumentFidelityValidator",
    "ComprehensiveFidelityReport",
    "UnifiedFidelityValidator",
]
