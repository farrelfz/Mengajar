"""
Universal Knowledge Core — Base Artifact Blueprint Bridge.

Phase 1D Artifact Blueprint Bridge Integration:
Abstract base bridge interface converting semantic ArtifactBlueprints into RenderArtifacts.

100% offline, deterministic, zero AI calls, zero renderer imports.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, Any, Type

from app.intelligence.transformation.blueprints import ArtifactBlueprint
from app.integration.artifact_bridge.contracts import RenderArtifact


class ArtifactBlueprintBridge(ABC):
    """Abstract anti-corruption bridge layer translating semantic blueprints into render contracts."""

    @property
    @abstractmethod
    def supported_blueprint_type(self) -> Type[ArtifactBlueprint]:
        """Returns the expected ArtifactBlueprint subclass."""
        pass

    def validate_blueprint(self, blueprint: ArtifactBlueprint) -> None:
        """Validates that inbound blueprint matches the expected blueprint type."""
        expected_type = self.supported_blueprint_type
        if not isinstance(blueprint, expected_type):
            raise TypeError(
                f"Bridge {self.__class__.__name__} expects blueprint of type {expected_type.__name__}, "
                f"got {type(blueprint).__name__}"
            )

    @abstractmethod
    def bridge(self, blueprint: ArtifactBlueprint) -> RenderArtifact:
        """Translates a semantic blueprint into a renderer-neutral RenderArtifact."""
        pass
