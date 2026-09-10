"""
Universal Knowledge Core — Artifact Fidelity Base Contracts.

Phase 2B Controlled Renderer Execution & Artifact Fidelity:
Defines the multi-dimensional evaluation contracts:
1. Semantic Fidelity
2. Structural Fidelity
3. Artifact-Specific Fidelity (Pedagogical or Scientific)
4. Visual & Layout Fidelity
5. Traceability Fidelity
6. Execution Reliability
"""

from __future__ import annotations

import time
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, ConfigDict, Field

from app.integration.artifact_bridge.contracts import RenderArtifact
from app.integration.render_execution.renderer_result import RendererExecutionResult


class ArtifactFidelityEvaluation(BaseModel):
    """Authoritative fidelity evaluation outcome for a rendered artifact."""
    model_config = ConfigDict(frozen=True)

    artifact_type: str
    overall_score: float
    is_passing: bool
    semantic_fidelity: float
    structural_fidelity: float
    artifact_specific_fidelity: float  # Pedagogical or Scientific
    visual_layout_fidelity: float
    traceability_fidelity: float
    execution_reliability: float
    violations: Tuple[str, ...] = Field(default_factory=tuple)
    warnings: Tuple[str, ...] = Field(default_factory=tuple)
    traceability_stats: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    evaluated_at: float = Field(default_factory=time.time)


class BaseArtifactFidelityValidator(ABC):
    """Abstract base validator for artifact-specific fidelity evaluation."""

    @property
    @abstractmethod
    def supported_artifact_type(self) -> str:
        """Target artifact type (PRESENTATION, HANDOUT, WORKSHEET, SCIENTIFIC_DOCUMENT)."""
        pass

    @abstractmethod
    def evaluate(
        self,
        render_artifact: RenderArtifact,
        legacy_model: Any,
        execution_result: RendererExecutionResult,
    ) -> ArtifactFidelityEvaluation:
        """Evaluates rendered artifact across all six fidelity dimensions."""
        pass
