"""
Universal Knowledge Core — Renderer Executor Contract.

Phase 2B Controlled Renderer Execution & Artifact Fidelity:
Abstract base interface for legacy renderer execution wrappers.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Optional

from app.integration.artifact_bridge.contracts import RenderArtifact
from app.integration.render_execution.renderer_result import RendererExecutionResult


class RendererExecutor(ABC):
    """Abstract executor driving legacy rendering engines with adapted models."""

    @property
    @abstractmethod
    def supported_artifact_type(self) -> str:
        """Target artifact type (PRESENTATION, HANDOUT, WORKSHEET, SCIENTIFIC_DOCUMENT)."""
        pass

    @abstractmethod
    def execute(
        self,
        legacy_model: Any,
        output_dir: Path,
        output_filename: Optional[str] = None,
    ) -> RendererExecutionResult:
        """Executes the legacy renderer using the adapted intermediate model."""
        pass

    @abstractmethod
    def execute_from_render_artifact(
        self,
        render_artifact: RenderArtifact,
        output_dir: Path,
        output_filename: Optional[str] = None,
        **adapter_kwargs: Any,
    ) -> RendererExecutionResult:
        """Adapts RenderArtifact and executes the legacy renderer end-to-end."""
        pass
