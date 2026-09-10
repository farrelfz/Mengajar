"""
Universal Knowledge Core — Unified Fidelity Validator.

Phase 2B Controlled Renderer Execution & Artifact Fidelity:
Orchestrates artifact-specific fidelity evaluation, computes macro scores,
and enforces minimum fidelity quality gates.
"""

from __future__ import annotations

import time
import uuid
from typing import Any, Dict, List, Optional, Tuple

from app.integration.artifact_bridge.contracts import RenderArtifact
from app.integration.render_execution.renderer_result import RendererExecutionResult
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
from app.quality.artifact_fidelity.worksheet_fidelity import WorksheetFidelityValidator


class UnifiedFidelityValidator:
    """Unified engine coordinating fidelity evaluation across all four artifact types."""

    def __init__(self) -> None:
        self._validators: Dict[str, BaseArtifactFidelityValidator] = {
            "PRESENTATION": PresentationFidelityValidator(),
            "HANDOUT": HandoutFidelityValidator(),
            "WORKSHEET": WorksheetFidelityValidator(),
            "SCIENTIFIC_DOCUMENT": ScientificDocumentFidelityValidator(),
        }

    def evaluate_artifact(
        self,
        render_artifact: RenderArtifact,
        legacy_model: Any,
        execution_result: RendererExecutionResult,
    ) -> ArtifactFidelityEvaluation:
        """Evaluates a single artifact execution."""
        art_type = render_artifact.artifact_type.upper()
        validator = self._validators.get(art_type)
        if not validator:
            raise ValueError(f"No fidelity validator registered for artifact type '{art_type}'.")

        return validator.evaluate(render_artifact, legacy_model, execution_result)

    def evaluate_system(
        self,
        artifacts_data: Dict[str, Tuple[RenderArtifact, Any, RendererExecutionResult]],
        manifest_title: str = "Universal Knowledge System",
    ) -> ComprehensiveFidelityReport:
        """Evaluates all executed artifacts and produces a ComprehensiveFidelityReport."""
        evaluations: Dict[str, ArtifactFidelityEvaluation] = {}
        total_violations = 0
        total_warnings = 0

        for art_key, (r_art, l_model, exec_res) in artifacts_data.items():
            evaluation = self.evaluate_artifact(r_art, l_model, exec_res)
            evaluations[evaluation.artifact_type] = evaluation
            total_violations += len(evaluation.violations)
            total_warnings += len(evaluation.warnings)

        macro_score = (
            sum(e.overall_score for e in evaluations.values()) / max(len(evaluations), 1)
            if evaluations
            else 0.0
        )
        all_pass = all(e.is_passing for e in evaluations.values()) and total_violations == 0

        return ComprehensiveFidelityReport(
            report_id=f"fid_rep_{uuid.uuid4().hex[:8]}",
            manifest_title=manifest_title,
            evaluations=evaluations,
            macro_fidelity_score=round(macro_score, 3),
            all_passing=all_pass,
            total_violations=total_violations,
            total_warnings=total_warnings,
        )
