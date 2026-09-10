"""
Universal Knowledge Core — Scientific Document Fidelity Validator.

Phase 2B Controlled Renderer Execution & Artifact Fidelity:
Evaluates Scientific Documents (KTI) across Indonesian KTI chapter structure,
claim-to-evidence ratio, explicit citation grounding, and limitation demarcation.
"""

from __future__ import annotations

from typing import Any, Dict, List, Set, Tuple

from app.intelligence.schemas import KtiBab
from app.integration.artifact_bridge.contracts import RenderArtifact
from app.integration.render_execution.renderer_result import RendererExecutionResult
from app.integration.renderer_adapters.contracts import LegacyScientificDocument
from app.quality.artifact_fidelity.base import (
    ArtifactFidelityEvaluation,
    BaseArtifactFidelityValidator,
)

EXPECTED_BAB_SEQUENCE = [
    KtiBab.BAB_1,
    KtiBab.BAB_2,
    KtiBab.BAB_3,
    KtiBab.BAB_4,
    KtiBab.BAB_5,
]


class ScientificDocumentFidelityValidator(BaseArtifactFidelityValidator):
    """Evaluates rendered scientific documents (KTI) against academic integrity contracts."""

    @property
    def supported_artifact_type(self) -> str:
        return "SCIENTIFIC_DOCUMENT"

    def evaluate(
        self,
        render_artifact: RenderArtifact,
        legacy_model: LegacyScientificDocument,
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
            violations.append(f"Dropped source arguments in scientific document: {len(missing_bps)} missing.")
            semantic_score = max(0.0, 1.0 - (len(missing_bps) / max(len(source_bp_ids), 1)))
        else:
            semantic_score = 1.0

        # 2. Structural Fidelity (KTI Bab Sequence: BAB 1 to BAB 5)
        structural_violations = 0
        actual_babs = [b.bab for b in legacy_model.babs]
        if actual_babs != EXPECTED_BAB_SEQUENCE:
            violations.append(f"KTI Bab sequence broken: {actual_babs} != {EXPECTED_BAB_SEQUENCE}")
            structural_violations += 1

        structural_score = max(0.0, 1.0 - (structural_violations * 0.5))

        # 3. Artifact-Specific Fidelity (Scientific Evidence Grounding & Integrity)
        evidence_violations = 0
        total_subsections = 0
        total_evidence_cited = 0

        for bab in legacy_model.babs:
            for sub in bab.subsections:
                total_subsections += 1
                total_evidence_cited += len(sub.evidence_items)

                # Integrity check: unsupported claims must not be mixed with empirical evidence without limitation
                if sub.unsupported_claims and sub.evidence_ids and not sub.limitations:
                    violations.append(
                        f"Integrity violation in subsection {sub.subsection_id}: "
                        f"unsupported claims mixed with empirical evidence without limitation demarcation."
                    )
                    evidence_violations += 1

        if legacy_model.unsupported_claims_flagged:
            warnings.extend(legacy_model.unsupported_claims_flagged)

        evidence_score = max(0.0, 1.0 - (evidence_violations * 0.35))

        # 4. Visual Layout Fidelity
        visual_score = 1.0
        if execution_result.total_pages == 0:
            violations.append("Zero pages rendered for scientific document.")
            visual_score = 0.0
        if execution_result.errors:
            violations.extend(execution_result.errors)
            visual_score -= 0.3

        # 5. Traceability Fidelity (Evidence graph preservation)
        traces_count = len(legacy_model.grouping_decision_traces)
        if traces_count < total_subsections:
            warnings.append("Incomplete decision traces across scientific subsections.")
            traceability_score = traces_count / max(total_subsections, 1)
        else:
            traceability_score = 1.0

        # 6. Execution Reliability
        if execution_result.success and execution_result.pdf_path and execution_result.pdf_path.exists():
            reliability_score = 1.0
        else:
            violations.append("Scientific document rendering failed or PDF missing.")
            reliability_score = 0.0

        overall_score = round(
            (
                semantic_score * 0.20
                + structural_score * 0.20
                + evidence_score * 0.25
                + visual_score * 0.15
                + traceability_score * 0.10
                + reliability_score * 0.10
            ),
            3,
        )

        is_passing = overall_score >= 0.85 and len(violations) == 0

        return ArtifactFidelityEvaluation(
            artifact_type="SCIENTIFIC_DOCUMENT",
            overall_score=overall_score,
            is_passing=is_passing,
            semantic_fidelity=round(semantic_score, 3),
            structural_fidelity=round(structural_score, 3),
            artifact_specific_fidelity=round(evidence_score, 3),
            visual_layout_fidelity=round(visual_score, 3),
            traceability_fidelity=round(traceability_score, 3),
            execution_reliability=round(reliability_score, 3),
            violations=tuple(violations),
            warnings=tuple(warnings),
            traceability_stats={
                "total_source_elements": len(source_bp_ids),
                "rendered_source_elements": len(rendered_bp_ids),
                "total_babs": len(legacy_model.babs),
                "total_subsections": total_subsections,
                "total_evidence_cited": total_evidence_cited,
            },
            metadata={
                "document_title": legacy_model.title,
                "total_pages": execution_result.total_pages,
            },
        )
