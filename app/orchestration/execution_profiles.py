"""
Universal Document Intelligence System V5 — Artifact Execution Profiles.

Phase 3D: Configuration profiles decoupling artifact-specific transformation,
bridging, and rendering logic from the common production orchestration skeleton.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, Type

from app.intelligence.transformation import (
    ArtifactType,
    HandoutTransformer,
    PresentationTransformer,
    ResolvedArtifactIntent,
    ScientificDocumentTransformer,
    WorksheetTransformer,
    get_default_intent,
)

from app.integration.artifact_bridge.presentation_bridge import PresentationBlueprintBridge
from app.integration.artifact_bridge.handout_bridge import HandoutBlueprintBridge
from app.integration.artifact_bridge.worksheet_bridge import WorksheetBlueprintBridge
from app.integration.artifact_bridge.scientific_document_bridge import ScientificDocumentBlueprintBridge

from app.integration.render_execution.presentation_executor import PresentationExecutor
from app.integration.render_execution.handout_executor import HandoutExecutor
from app.integration.render_execution.worksheet_executor import WorksheetExecutor
from app.integration.render_execution.scientific_document_executor import ScientificDocumentExecutor


@dataclass(frozen=True)
class ArtifactExecutionProfile:
    """Immutable execution configuration for a specific artifact type."""
    artifact_type: str
    transformer_factory: Callable[[], Any]
    bridge_factory: Callable[[], Any]
    executor_factory: Callable[[], Any]
    default_intent_factory: Callable[[], ResolvedArtifactIntent]
    max_repair_iterations: int
    emphasis_description: str


class ArtifactExecutionProfileRegistry:
    """Registry maintaining authoritative profiles for all four artifact types."""

    _PROFILES: Dict[str, ArtifactExecutionProfile] = {
        "PRESENTATION": ArtifactExecutionProfile(
            artifact_type="PRESENTATION",
            transformer_factory=PresentationTransformer,
            bridge_factory=PresentationBlueprintBridge,
            executor_factory=PresentationExecutor,
            default_intent_factory=lambda: get_default_intent(ArtifactType.PRESENTATION),
            max_repair_iterations=4,
            emphasis_description="Narrative progression, visual grammar, cognitive load, layout rhythm, slide density",
        ),
        "HANDOUT": ArtifactExecutionProfile(
            artifact_type="HANDOUT",
            transformer_factory=HandoutTransformer,
            bridge_factory=HandoutBlueprintBridge,
            executor_factory=HandoutExecutor,
            default_intent_factory=lambda: get_default_intent(ArtifactType.HANDOUT),
            max_repair_iterations=3,
            emphasis_description="Reading hierarchy, explanatory completeness, page balance, typography, continuous narrative",
        ),
        "WORKSHEET": ArtifactExecutionProfile(
            artifact_type="WORKSHEET",
            transformer_factory=WorksheetTransformer,
            bridge_factory=WorksheetBlueprintBridge,
            executor_factory=WorksheetExecutor,
            default_intent_factory=lambda: get_default_intent(ArtifactType.WORKSHEET),
            max_repair_iterations=3,
            emphasis_description="Inquiry progression, anti-spoiling, student workspace, observation flow, response affordance",
        ),
        "SCIENTIFIC_DOCUMENT": ArtifactExecutionProfile(
            artifact_type="SCIENTIFIC_DOCUMENT",
            transformer_factory=ScientificDocumentTransformer,
            bridge_factory=ScientificDocumentBlueprintBridge,
            executor_factory=ScientificDocumentExecutor,
            default_intent_factory=lambda: get_default_intent(ArtifactType.SCIENTIFIC_DOCUMENT),
            max_repair_iterations=3,
            emphasis_description="Claim grounding, evidence integrity, citation preservation, scientific argument, BAB hierarchy",
        ),
    }

    @classmethod
    def get_profile(cls, artifact_type: str) -> ArtifactExecutionProfile:
        norm = artifact_type.strip().upper()
        if norm not in cls._PROFILES:
            raise KeyError(
                f"No execution profile registered for artifact type '{artifact_type}'. "
                f"Supported: {tuple(cls._PROFILES.keys())}"
            )
        return cls._PROFILES[norm]
