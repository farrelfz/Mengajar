"""
Universal Document Intelligence System V5 — Repair Forensics Exporter.

Phase 3D.1: Exports exhaustive forensic records (JSON and Markdown) for any artifact
requiring manual review or failing convergence, covering all 16 mandatory forensic dimensions.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

from app.orchestration.production_context import ArtifactProductionContext
from app.quality.repair.effectiveness.contracts import RepairAttempt, RepairEffectivenessResult
from app.quality.repair.effectiveness.escalation import RepairEscalationDecision
from app.quality.repair.effectiveness.firewall import StrategyRejectionRecord
from app.quality.repair.effectiveness.zero_effect_detector import DomainFingerprint


class RepairForensicsExporter:
    """Exports structured 16-section repair forensics to JSON and Markdown."""

    @classmethod
    def export_forensics(
        cls,
        context: ArtifactProductionContext,
        output_dir: Path,
        attempts: Sequence[RepairAttempt] = (),
        effectiveness_results: Sequence[RepairEffectivenessResult] = (),
        disqualified_strategies: Sequence[Tuple[str, str]] = (),
        rejections: Sequence[StrategyRejectionRecord] = (),
        escalation_decisions: Sequence[RepairEscalationDecision] = (),
        domain_fingerprints: Sequence[DomainFingerprint] = (),
        final_failure_reason: str = "Repair budget exhausted without achieving zero blockers.",
        recommended_owning_layer: str = "R1",
    ) -> Tuple[Path, Path]:
        """
        Generates:
        1. <output_dir>/repair_forensics.json
        2. <output_dir>/repair_forensics.md
        Strictly containing all 16 forensic dimensions.
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        json_path = output_dir / "repair_forensics.json"
        md_path = output_dir / "repair_forensics.md"

        init_report = context.quality_authority_result
        init_findings = [
            {
                "failure_code": f.failure_code,
                "severity": getattr(f, "severity", "MAJOR"),
                "domain": str(getattr(f, "domain", "")),
                "message": getattr(f, "message", ""),
            }
            for f in (init_report.findings if init_report else ())
        ]

        data: Dict[str, Any] = {
            "1_initial_findings": init_findings,
            "2_root_cause_hypotheses": [
                {
                    "finding_code": f.failure_code,
                    "cause_type": "GRID_GEOMETRY" if "COLLISION" in f.failure_code else "CONTENT_DENSITY",
                }
                for f in (init_report.findings if init_report else ())
            ],
            "3_candidate_strategies": [a.strategy_id for a in attempts],
            "4_rejected_strategies_and_reasons": [
                {"strategy_id": r.strategy_id, "reason": r.reason, "stage": r.filter_stage}
                for r in rejections
            ],
            "5_selected_strategy": [a.strategy_id for a in attempts],
            "6_mutation_scope": [a.mutation_scope.name for a in attempts],
            "7_pre_post_fingerprints": [
                {
                    "structural_hash": df.structural_hash,
                    "semantic_hash": df.semantic_hash,
                    "composite_hash": df.composite_hash,
                    "components": df.component_signatures,
                }
                for df in domain_fingerprints
            ],
            "8_finding_severity_deltas": [er.severity_delta for er in effectiveness_results],
            "9_quality_deltas": [er.quality_delta for er in effectiveness_results],
            "10_root_cause_persistence": [
                {"iteration": er.attempt_id, "improved": er.root_cause_improved}
                for er in effectiveness_results
            ],
            "11_strategy_effectiveness": [
                {
                    "strategy_id": er.strategy_id,
                    "overall_status": er.overall_status.value,
                    "finding_resolution_ratio": er.finding_resolution_ratio,
                    "rationale": er.rationale,
                }
                for er in effectiveness_results
            ],
            "12_escalation_decisions": [
                {
                    "prev": ed.previous_strategy_id,
                    "next": ed.escalated_strategy_id,
                    "reason": ed.escalation_reason.value,
                    "layer": ed.target_owning_layer,
                }
                for ed in escalation_decisions
            ],
            "13_disqualified_strategies": [
                {"strategy_id": s_id, "reason": r} for s_id, r in disqualified_strategies
            ],
            "14_budget_consumption": [
                {"strategy_id": a.strategy_id, "cost": a.mutation_cost} for a in attempts
            ],
            "15_final_convergence_failure_reason": final_failure_reason,
            "16_recommended_next_owning_layer": recommended_owning_layer,
        }

        # Write JSON
        json_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

        # Write Markdown
        md_lines = [
            f"# Repair Forensics Report: {context.artifact_type} ({context.job_id})",
            "",
            "## 1. Initial Findings",
            *[f"- **{f['failure_code']}** ({f['severity']}): {f['message']}" for f in init_findings],
            "",
            "## 2. Root Cause Hypotheses",
            *[f"- Finding `{h['finding_code']}` attributed to `{h['cause_type']}`" for h in data["2_root_cause_hypotheses"]],
            "",
            "## 3. Candidate Strategies Evaluated",
            *[f"- `{s}`" for s in data["3_candidate_strategies"]],
            "",
            "## 4. Rejected Strategies and Reasons",
            *[f"- **{r['strategy_id']}** (Stage: {r['stage']}): {r['reason']}" for r in data["4_rejected_strategies_and_reasons"]],
            "",
            "## 5. Selected Strategies Applied",
            *[f"- Cycle {idx}: `{s}`" for idx, s in enumerate(data["5_selected_strategy"], start=1)],
            "",
            "## 6. Mutation Scope Boundaries",
            *[f"- Cycle {idx}: `{s}`" for idx, s in enumerate(data["6_mutation_scope"], start=1)],
            "",
            "## 7. Pre/Post Domain Fingerprints",
            *[f"- Hash: `{fp['composite_hash']}` (Struct: `{fp['structural_hash']}`, Sem: `{fp['semantic_hash']}`)" for fp in data["7_pre_post_fingerprints"]],
            "",
            "## 8. Finding Severity Deltas",
            *[f"- Cycle {idx}: severity delta = {sd}" for idx, sd in enumerate(data["8_finding_severity_deltas"], start=1)],
            "",
            "## 9. Quality Deltas",
            *[f"- Cycle {idx}: quality delta = {qd}" for idx, qd in enumerate(data["9_quality_deltas"], start=1)],
            "",
            "## 10. Root Cause Persistence",
            *[f"- Cycle {rc['iteration']}: improved = {rc['improved']}" for rc in data["10_root_cause_persistence"]],
            "",
            "## 11. Strategy Effectiveness Classification",
            *[f"- **{e['strategy_id']}**: `{e['overall_status']}` ({e['rationale']})" for e in data["11_strategy_effectiveness"]],
            "",
            "## 12. Escalation Decisions",
            *[f"- `{ed['prev']}` -> `{ed['next']}` (Reason: {ed['reason']}, Target Layer: {ed['layer']})" for ed in data["12_escalation_decisions"]],
            "",
            "## 13. Disqualified Strategies",
            *[f"- **{d['strategy_id']}**: {d['reason']}" for d in data["13_disqualified_strategies"]],
            "",
            "## 14. Budget Consumption",
            *[f"- `{b['strategy_id']}` consumed {b['cost']} mutation units" for b in data["14_budget_consumption"]],
            "",
            "## 15. Final Convergence Failure Reason",
            f"> {final_failure_reason}",
            "",
            "## 16. Recommended Next Owning Layer",
            f"**Recommended Owning Layer**: `{recommended_owning_layer}`",
            "",
        ]
        md_path.write_text("\n".join(md_lines), encoding="utf-8")

        return json_path, md_path
