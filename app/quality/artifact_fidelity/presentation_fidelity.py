"""
Universal Knowledge Core — Presentation Fidelity Validator.

Phase 2B Controlled Renderer Execution & Artifact Fidelity:
Evaluates Presentation 16:9 slide decks across semantic, structural, pedagogical,
visual layout, traceability, and execution reliability dimensions.
"""

from __future__ import annotations

from typing import Any, Dict, List, Set, Tuple

from app.integration.artifact_bridge.contracts import RenderArtifact
from app.integration.render_execution.renderer_result import RendererExecutionResult
from app.integration.renderer_adapters.contracts import LegacyPresentationDeck
from app.quality.artifact_fidelity.base import (
    ArtifactFidelityEvaluation,
    BaseArtifactFidelityValidator,
)


class PresentationFidelityValidator(BaseArtifactFidelityValidator):
    """Evaluates rendered presentation decks against source contracts."""

    @property
    def supported_artifact_type(self) -> str:
        return "PRESENTATION"

    def evaluate(
        self,
        render_artifact: RenderArtifact,
        legacy_model: LegacyPresentationDeck,
        execution_result: RendererExecutionResult,
    ) -> ArtifactFidelityEvaluation:
        violations: List[str] = []
        warnings: List[str] = []

        # 1. Semantic Fidelity (Concept preservation and content fidelity)
        source_bp_ids: Set[str] = {
            u.traceability_refs.blueprint_element_id for u in render_artifact.units
        }
        rendered_bp_ids: Set[str] = set(execution_result.source_element_ids_rendered)
        missing_bps = source_bp_ids - rendered_bp_ids

        if missing_bps:
            violations.append(f"Dropped source blueprint elements: {len(missing_bps)} elements missing from slides.")
            semantic_score = max(0.0, 1.0 - (len(missing_bps) / max(len(source_bp_ids), 1)))
        else:
            semantic_score = 1.0

        # 2. Structural Fidelity (Slide bounds, layout appropriateness)
        if execution_result.total_pages == 0:
            violations.append("Zero slides rendered in presentation output.")
            structural_score = 0.0
        elif execution_result.total_pages != len(legacy_model.slides):
            violations.append(
                f"Page count mismatch: PDF has {execution_result.total_pages} pages, "
                f"expected {len(legacy_model.slides)} slides."
            )
            structural_score = 0.5
        else:
            structural_score = 1.0

        # 3. Artifact-Specific Fidelity (Pedagogical Narrative Progression & Cognitive Load)
        pedagogical_violations = 0
        for slide in legacy_model.slides:
            if slide.cognitive_load > 1.8:
                violations.append(f"Cognitive overload on slide {slide.slide_id}: {slide.cognitive_load} > 1.8")
                pedagogical_violations += 1

        pedagogical_score = max(0.0, 1.0 - (pedagogical_violations * 0.2))

        # 4. Visual & Layout Fidelity (Aspect ratio, sanitization, hallucinations)
        visual_score = 1.0
        if execution_result.errors:
            violations.extend(execution_result.errors)
            visual_score -= 0.3
        if execution_result.warnings:
            warnings.extend(execution_result.warnings)
            visual_score -= 0.1
        visual_score = max(0.0, visual_score)

        # 5. Traceability Fidelity (Many-to-One audit, decision traces)
        traces_count = len(legacy_model.grouping_decision_traces)
        if traces_count < len(legacy_model.slides):
            warnings.append(f"Missing decision traces: {len(legacy_model.slides) - traces_count} slides lack traces.")
            traceability_score = traces_count / max(len(legacy_model.slides), 1)
        else:
            traceability_score = 1.0

        # 6. Execution Reliability
        if execution_result.success and execution_result.pdf_path and execution_result.pdf_path.exists():
            reliability_score = 1.0
        else:
            violations.append("Renderer execution failed or PDF artifact missing.")
            reliability_score = 0.0

        overall_score = round(
            (
                semantic_score * 0.25
                + structural_score * 0.15
                + pedagogical_score * 0.20
                + visual_score * 0.15
                + traceability_score * 0.15
                + reliability_score * 0.10
            ),
            3,
        )

        is_passing = overall_score >= 0.85 and len(violations) == 0

        return ArtifactFidelityEvaluation(
            artifact_type="PRESENTATION",
            overall_score=overall_score,
            is_passing=is_passing,
            semantic_fidelity=round(semantic_score, 3),
            structural_fidelity=round(structural_score, 3),
            artifact_specific_fidelity=round(pedagogical_score, 3),
            visual_layout_fidelity=round(visual_score, 3),
            traceability_fidelity=round(traceability_score, 3),
            execution_reliability=round(reliability_score, 3),
            violations=tuple(violations),
            warnings=tuple(warnings),
            traceability_stats={
                "total_source_elements": len(source_bp_ids),
                "rendered_source_elements": len(rendered_bp_ids),
                "total_slides": len(legacy_model.slides),
                "decision_traces_recorded": traces_count,
            },
            metadata={
                "deck_title": legacy_model.deck_title,
                "pdf_path": str(execution_result.pdf_path) if execution_result.pdf_path else None,
            },
        )
