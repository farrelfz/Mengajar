"""
Quality Decision Engine & Export Authority.

The sole authority permitted to approve or block final presentation export.
Derives decisions strictly from the final authoritative QualityRound.
"""

from __future__ import annotations

import time
from typing import Any
from pydantic import BaseModel, Field

from app.orchestration.pipeline_state import ExportDecision, ExportDecisionStatus, PipelineState
from app.presentation.quality_gate import GateStatus, QualityRound


class QualityDecisionEngine:
    """Evaluates final QualityRound and produces authoritative ExportDecision."""

    @classmethod
    def evaluate(
        cls,
        final_round: QualityRound,
        state: PipelineState,
        max_iterations_reached: bool = False,
    ) -> ExportDecision:
        reasons: list[str] = []
        warnings: list[str] = []

        # Check for critical failures or blocked gates
        critical_gates = [
            g for g in final_round.gate_results
            if g.status in (GateStatus.CRITICAL_FAILURE, GateStatus.BLOCKED)
        ]
        if critical_gates:
            for cg in critical_gates:
                reasons.append(f"Critical Gate Failed: {cg.gate_name} ({cg.details})")

        # Check for repairable gates
        repairable_gates = [
            g for g in final_round.gate_results
            if g.status == GateStatus.REPAIR_REQUIRED
        ]
        if repairable_gates:
            if not max_iterations_reached:
                for rg in repairable_gates:
                    reasons.append(f"Repair Required: {rg.gate_name} ({rg.details})")
                return ExportDecision(
                    status=ExportDecisionStatus.REPAIR_REQUIRED,
                    authoritative_qa_round=final_round.round_id,
                    qa_artifact_version=final_round.artifact_version,
                    pdf_artifact_version=state.version_tracker.get_version("pdf"),
                    reasons=reasons,
                    warnings=warnings,
                    timestamp=time.time(),
                )
            else:
                for rg in repairable_gates:
                    reasons.append(f"Unresolved Gate (Budget Exhausted): {rg.gate_name} ({rg.details})")

        # Collect warnings
        warning_gates = [g for g in final_round.gate_results if g.status == GateStatus.WARNING]
        for wg in warning_gates:
            warnings.append(f"{wg.gate_name}: {wg.details}")

        # Final decision determination
        if reasons:
            decision_status = ExportDecisionStatus.BLOCKED
        elif warnings:
            decision_status = ExportDecisionStatus.EXPORT_APPROVED_WITH_WARNINGS
        else:
            decision_status = ExportDecisionStatus.EXPORT_APPROVED

        return ExportDecision(
            status=decision_status,
            authoritative_qa_round=final_round.round_id,
            qa_artifact_version=final_round.artifact_version,
            pdf_artifact_version=state.version_tracker.get_version("pdf"),
            reasons=reasons,
            warnings=warnings,
            timestamp=time.time(),
        )
