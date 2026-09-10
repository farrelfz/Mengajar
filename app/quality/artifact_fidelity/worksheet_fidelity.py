"""
Universal Knowledge Core — Worksheet Fidelity Validator.

Phase 2B Controlled Renderer Execution & Artifact Fidelity:
Evaluates Student Worksheets across semantic coverage, pedagogical progression,
strict withhold explanation enforcement (anti-spoiling), and workspace presence.
"""

from __future__ import annotations

from typing import Any, Dict, List, Set, Tuple

from app.integration.artifact_bridge.contracts import RenderArtifact
from app.integration.render_execution.renderer_result import RendererExecutionResult
from app.integration.renderer_adapters.contracts import LegacyWorksheetDocument
from app.integration.renderer_adapters.grouping_validator import INQUIRY_FORWARD_ORDER
from app.quality.artifact_fidelity.base import (
    ArtifactFidelityEvaluation,
    BaseArtifactFidelityValidator,
)


class WorksheetFidelityValidator(BaseArtifactFidelityValidator):
    """Evaluates rendered student worksheets against pedagogical and integrity contracts."""

    @property
    def supported_artifact_type(self) -> str:
        return "WORKSHEET"

    def evaluate(
        self,
        render_artifact: RenderArtifact,
        legacy_model: LegacyWorksheetDocument,
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
            violations.append(f"Dropped source activities in worksheet: {len(missing_bps)} missing.")
            semantic_score = max(0.0, 1.0 - (len(missing_bps) / max(len(source_bp_ids), 1)))
        else:
            semantic_score = 1.0

        # 2. Structural Fidelity (Activity preservation and non-flattening)
        total_acts = sum(len(s.activities) for s in legacy_model.sections)
        if total_acts != len(render_artifact.units):
            violations.append(f"Activity count mismatch: {total_acts} != {len(render_artifact.units)} units.")
            structural_score = 0.5
        else:
            structural_score = 1.0

        # 3. Artifact-Specific Fidelity (Pedagogical Progression & Strict Withholding)
        pedagogical_violations = 0
        withholding_violations = 0
        workspace_violations = 0

        for sec in legacy_model.sections:
            activities = sec.activities
            # Inquiry progression check
            for i in range(len(activities) - 1):
                o1 = INQUIRY_FORWARD_ORDER.get(activities[i].activity_type, 0)
                o2 = INQUIRY_FORWARD_ORDER.get(activities[i + 1].activity_type, 0)
                if o1 > 0 and o2 > 0 and o2 < o1:
                    violations.append(
                        f"Inquiry regression in section {sec.section_id}: "
                        f"{activities[i+1].activity_type} after {activities[i].activity_type}"
                    )
                    pedagogical_violations += 1

            for act in activities:
                # Anti-spoiling: Withholding explanation enforcement
                if not act.withhold_explanation:
                    violations.append(f"Answer explanation leaked in activity {act.activity_id}")
                    withholding_violations += 1

                # Active learning workspace requirement
                if not act.requires_student_workspace:
                    warnings.append(f"Activity {act.activity_id} lacks student workspace")
                    workspace_violations += 1

        ped_score = max(
            0.0,
            1.0
            - (pedagogical_violations * 0.25)
            - (withholding_violations * 0.40)
            - (workspace_violations * 0.05),
        )

        # 4. Visual Layout Fidelity (Workspace boxes, activity badges)
        visual_score = 1.0
        if execution_result.total_pages == 0:
            violations.append("Zero pages rendered for worksheet.")
            visual_score = 0.0
        if execution_result.errors:
            violations.extend(execution_result.errors)
            visual_score -= 0.3

        # 5. Traceability Fidelity
        traces_count = len(legacy_model.grouping_decision_traces)
        if traces_count < len(legacy_model.sections):
            warnings.append("Incomplete decision traces across worksheet sections.")
            traceability_score = traces_count / max(len(legacy_model.sections), 1)
        else:
            traceability_score = 1.0

        # 6. Execution Reliability
        if execution_result.success and execution_result.pdf_path and execution_result.pdf_path.exists():
            reliability_score = 1.0
        else:
            violations.append("Worksheet rendering failed or PDF missing.")
            reliability_score = 0.0

        overall_score = round(
            (
                semantic_score * 0.20
                + structural_score * 0.20
                + ped_score * 0.25
                + visual_score * 0.15
                + traceability_score * 0.10
                + reliability_score * 0.10
            ),
            3,
        )

        is_passing = overall_score >= 0.85 and len(violations) == 0

        return ArtifactFidelityEvaluation(
            artifact_type="WORKSHEET",
            overall_score=overall_score,
            is_passing=is_passing,
            semantic_fidelity=round(semantic_score, 3),
            structural_fidelity=round(structural_score, 3),
            artifact_specific_fidelity=round(ped_score, 3),
            visual_layout_fidelity=round(visual_score, 3),
            traceability_fidelity=round(traceability_score, 3),
            execution_reliability=round(reliability_score, 3),
            violations=tuple(violations),
            warnings=tuple(warnings),
            traceability_stats={
                "total_source_elements": len(source_bp_ids),
                "rendered_source_elements": len(rendered_bp_ids),
                "total_activities": total_acts,
                "withholding_violations": withholding_violations,
            },
            metadata={
                "document_title": legacy_model.title,
                "total_pages": execution_result.total_pages,
            },
        )
