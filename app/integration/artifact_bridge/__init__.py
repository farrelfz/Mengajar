"""
Universal Knowledge Core — Artifact Blueprint Bridge Package.

Phase 1D:
Anti-corruption bridge layer translating semantic ArtifactBlueprints into
renderer-neutral RenderArtifact contracts for Presentation, Handout, Worksheet,
and Scientific Document artifacts.
"""

from app.integration.artifact_bridge.contracts import (
    RenderArtifact,
    RenderMetadata,
    RenderSection,
    RenderTraceabilityRef,
    RenderUnit,
)
from app.integration.artifact_bridge.base import ArtifactBlueprintBridge
from app.integration.artifact_bridge.presentation_bridge import PresentationBlueprintBridge
from app.integration.artifact_bridge.handout_bridge import HandoutBlueprintBridge
from app.integration.artifact_bridge.worksheet_bridge import WorksheetBlueprintBridge
from app.integration.artifact_bridge.scientific_document_bridge import ScientificDocumentBlueprintBridge
from app.integration.artifact_bridge.bridge_validator import (
    ArtifactBridgeValidator,
    BridgeValidationReport,
)

__all__ = [
    "RenderArtifact",
    "RenderMetadata",
    "RenderSection",
    "RenderTraceabilityRef",
    "RenderUnit",
    "ArtifactBlueprintBridge",
    "PresentationBlueprintBridge",
    "HandoutBlueprintBridge",
    "WorksheetBlueprintBridge",
    "ScientificDocumentBlueprintBridge",
    "ArtifactBridgeValidator",
    "BridgeValidationReport",
]
