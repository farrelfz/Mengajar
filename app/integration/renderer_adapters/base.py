"""
Universal Knowledge Core — Base Renderer Contract Adapter.

Phase 2A Controlled Renderer Adapter Integration:
Defines the abstract RendererContractAdapter enforcing offline determinism,
strict type and traceability validation, and absence of renderer imports or AI logic.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from app.integration.artifact_bridge.contracts import RenderArtifact, RenderUnit


class RendererContractAdapter(ABC):
    """Abstract base class for all legacy contract adapters.

    Translates renderer-neutral RenderArtifact instances into legacy intermediate
    models without modifying existing renderers.

    Rules:
    - 100% Deterministic & Offline
    - Zero AI calls or semantic inference
    - Immutable input contract (input RenderArtifact must never be mutated)
    - Zero renderer imports (no ReportLab, Playwright, Jinja, or HTMLAssembler)
    - Rejects wrong artifact types, missing traceability, and unsupported units
    """

    @property
    @abstractmethod
    def supported_artifact_type(self) -> str:
        """The uppercase artifact type this adapter accepts (e.g. PRESENTATION)."""
        pass

    def validate_artifact(self, render_artifact: RenderArtifact) -> None:
        """Validates input RenderArtifact contract integrity before adaptation.

        Raises:
            TypeError: If input is not a RenderArtifact instance.
            ValueError: If artifact_type mismatches, units are empty, or traceability is missing.
        """
        if not isinstance(render_artifact, RenderArtifact):
            raise TypeError(
                f"Expected RenderArtifact instance, got '{type(render_artifact).__name__}'."
            )

        if render_artifact.artifact_type.upper() != self.supported_artifact_type.upper():
            raise ValueError(
                f"Unsupported artifact type '{render_artifact.artifact_type}' for "
                f"{self.__class__.__name__}. Expected '{self.supported_artifact_type}'."
            )

        if not render_artifact.units:
            raise ValueError(
                f"RenderArtifact '{render_artifact.artifact_id}' contains no RenderUnits to adapt."
            )

        for unit in render_artifact.units:
            if not isinstance(unit, RenderUnit):
                raise TypeError(f"Invalid unit element of type '{type(unit).__name__}'.")
            if not unit.traceability_refs or not unit.traceability_refs.blueprint_element_id:
                raise ValueError(
                    f"Missing traceability reference in RenderUnit '{unit.unit_id}'. "
                    f"Every RenderUnit must contain a valid blueprint_element_id."
                )

    @abstractmethod
    def adapt(self, render_artifact: RenderArtifact, **kwargs: Any) -> Any:
        """Deterministically transforms RenderArtifact into legacy intermediate model."""
        pass
