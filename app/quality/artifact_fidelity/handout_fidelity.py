"""
Universal Knowledge Core — Handout Fidelity Validator.

Phase 2B Controlled Renderer Execution & Artifact Fidelity:
Evaluates Handout reading documents across semantic coverage, heading hierarchy,
reading flow, callout preservation, and execution reliability.
"""

from __future__ import annotations

from typing import Any, Dict, List, Set, Tuple

from app.integration.artifact_bridge.contracts import RenderArtifact
from app.integration.render_execution.renderer_result import RendererExecutionResult
from app.integration.renderer_adapters.contracts import DocumentContent
from app.quality.artifact_fidelity.base import (
    ArtifactFidelityEvaluation,
    BaseArtifactFidelityValidator,
)


class HandoutFidelityValidator(BaseArtifactFidelityValidator):
    """Evaluates rendered handout reading documents."""

    @property
    def supported_artifact_type(self) -> str:
        return "HANDOUT"

    def evaluate(
        self,
        render_artifact: RenderArtifact,
        legacy_model: DocumentContent,
        execution_result: RendererExecutionResult,
    ) -> ArtifactFidelityEvaluation:
        violations: List[str] = []
        warnings: List[str] = []

        # 1. Semantic Fidelity
        source_bp_ids: Set[str] = {
            u.traceability_refs.blueprint_element_id for u in render_artifact.units
        }
        rendered_bp_ids: Set[str] = set(execution_result.source_element_ids_rendered)
        missing_bps = source_bp_ids - rendered_bp_ids

        if missing_bps:
            violations.append(f"Dropped source elements in handout: {len(missing_bps)} missing.")
            semantic_score = max(0.0, 1.0 - (len(missing_bps) / max(len(source_bp_ids), 1)))
        else:
            semantic_score = 1.0

        # 2. Structural Fidelity (Hierarchy continuity)
        structural_violations = 0
        last_level = 1
        for sec in legacy_model.sections:
            if sec.level > last_level + 1 and last_level > 0:
                violations.append(f"Heading inversion in section {sec.section_id}: jumped to level {sec.level}")
                structural_violations += 1
            last_level = sec.level

            if not sec.content and not sec.definitions and not sec.examples:
                violations.append(f"Empty reading section detected: {sec.section_id}")
                structural_violations += 1

        structural_score = max(0.0, 1.0 - (structural_violations * 0.25))

        # 3. Artifact-Specific Fidelity (Reading Depth & Callout Enrichment)
        total_defs = sum(len(s.definitions) for s in legacy_model.sections)
        total_exs = sum(len(s.examples) for s in legacy_model.sections)
        reading_score = 1.0
        if total_defs == 0 and total_exs == 0:
            warnings.append("Handout contains zero concept definitions or examples.")
            reading_score = 0.8

        # 4. Visual Layout Fidelity
        visual_score = 1.0
        if execution_result.total_pages == 0:
            violations.append("Zero pages rendered for handout.")
            visual_score = 0.0
        if execution_result.errors:
            violations.extend(execution_result.errors)
            visual_score -= 0.3

        # 5. Traceability Fidelity
        traces_count = len(legacy_model.grouping_decision_traces)
        if traces_count < len(legacy_model.sections):
            warnings.append("Incomplete decision traces across handout sections.")
            traceability_score = traces_count / max(len(legacy_model.sections), 1)
        else:
            traceability_score = 1.0

        # 6. Execution Reliability
        if execution_result.success and execution_result.pdf_path and execution_result.pdf_path.exists():
            reliability_score = 1.0
        else:
            violations.append("Handout rendering failed or PDF missing.")
            reliability_score = 0.0

        overall_score = round(
            (
                semantic_score * 0.25
                + structural_score * 0.20
                + reading_score * 0.15
                + visual_score * 0.15
                + traceability_score * 0.15
                + reliability_score * 0.10
            ),
            3,
        )

        is_passing = overall_score >= 0.85 and len(violations) == 0

        return ArtifactFidelityEvaluation(
            artifact_type="HANDOUT",
            overall_score=overall_score,
            is_passing=is_passing,
            semantic_fidelity=round(semantic_score, 3),
            structural_fidelity=round(structural_score, 3),
            artifact_specific_fidelity=round(reading_score, 3),
            visual_layout_fidelity=round(visual_score, 3),
            traceability_fidelity=round(traceability_score, 3),
            execution_reliability=round(reliability_score, 3),
            violations=tuple(violations),
            warnings=tuple(warnings),
            traceability_stats={
                "total_source_elements": len(source_bp_ids),
                "rendered_source_elements": len(rendered_bp_ids),
                "total_sections": len(legacy_model.sections),
                "total_definitions": total_defs,
                "total_examples": total_exs,
            },
            metadata={
                "document_title": legacy_model.title,
                "total_pages": execution_result.total_pages,
            },
        )
