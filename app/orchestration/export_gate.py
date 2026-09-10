"""
Universal Document Intelligence System V5 — Authorized Export Gate.

Phase 3D: Strict security barrier preventing unauthorized document exports.
Guarantees that artifacts cannot be emitted as production deliverables without
explicit, authoritative approval from UnifiedQualityAuthority.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.orchestration.production_context import ArtifactProductionContext
from app.orchestration.production_state import ProductionState
from app.orchestration.versioning import ProductionVersionManager
from app.quality.contracts.authority import UnifiedQualityReport
from app.quality.contracts.decisions import ExportDecision


class UnauthorizedExportError(PermissionError):
    """Raised when an export is attempted without authoritative clearance."""
    def __init__(self, message: str, decision: Optional[ExportDecision] = None, blockers: Sequence[str] = ()):
        super().__init__(message)
        self.decision = decision
        self.blockers = tuple(blockers)


@dataclass(frozen=True)
class ExportPackage:
    """Complete, verified deliverable bundle emitted upon authorized export."""
    artifact_path: Path
    final_dir: Path
    generation_report_json: Path
    generation_report_md: Path
    quality_report_json: Path
    quality_report_md: Path
    repair_history_json: Path
    provenance_json: Path
    convergence_report_json: Path
    warnings_md: Optional[Path] = None


class AuthorizedExportGate:
    """Enforces export governance rules and packages verified production deliverables."""

    @classmethod
    def verify_and_export(
        cls,
        context: ArtifactProductionContext,
        version_manager: ProductionVersionManager,
    ) -> ExportPackage:
        """Verifies quality authority approval and packages output into final/."""
        report = context.quality_authority_result

        # 1. Non-Negotiable Gate Checks
        if report is None:
            raise UnauthorizedExportError(
                "Cannot export artifact: Quality Authority evaluation was never performed.",
            )

        if not report.can_export or report.decision not in (
            ExportDecision.EXPORT_APPROVED,
            ExportDecision.EXPORT_APPROVED_WITH_WARNINGS,
        ):
            raise UnauthorizedExportError(
                f"Export rejected by Quality Authority: Decision={report.decision.value}. "
                f"Hard blockers: {report.hard_blockers}",
                decision=report.decision,
                blockers=report.hard_blockers,
            )

        # 2. Verify State Machine is in an Approved State
        current_state = context.state_machine.current_state
        if current_state not in (
            ProductionState.APPROVED,
            ProductionState.APPROVED_WITH_WARNINGS,
            ProductionState.EXPORTING,
        ):
            raise UnauthorizedExportError(
                f"Export rejected: Pipeline state machine is in '{current_state.value}', not in an approved state.",
            )

        if current_state != ProductionState.EXPORTING:
            context.transition_state(ProductionState.EXPORTING, reason="Authorized export initiated.")

        final_dir = version_manager.base_output_dir / "final"
        final_dir.mkdir(parents=True, exist_ok=True)

        artifact_name = version_manager.artifact_name

        # Copy approved artifact PDF
        target_pdf = None
        if context.render_result and context.render_result.pdf_path and Path(context.render_result.pdf_path).exists():
            target_pdf = final_dir / f"{artifact_name}.pdf"
            src_pdf = Path(context.render_result.pdf_path)
            if src_pdf.resolve() != target_pdf.resolve():
                import shutil
                shutil.copy2(src_pdf, target_pdf)
        else:
            # Fallback to last recorded PDF
            if version_manager.iterations and version_manager.iterations[-1].pdf_path:
                target_pdf = final_dir / f"{artifact_name}.pdf"
                src_pdf = version_manager.iterations[-1].pdf_path
                if src_pdf.resolve() != target_pdf.resolve():
                    import shutil
                    shutil.copy2(src_pdf, target_pdf)

        # Copy approved artifact HTML if present
        target_html = None
        if context.render_result and context.render_result.html_path and Path(context.render_result.html_path).exists():
            target_html = final_dir / f"{artifact_name}.html"
            src_html = Path(context.render_result.html_path)
            if src_html.resolve() != target_html.resolve():
                import shutil
                shutil.copy2(src_html, target_html)
        else:
            if version_manager.iterations and version_manager.iterations[-1].html_path:
                target_html = final_dir / f"{artifact_name}.html"
                src_html = version_manager.iterations[-1].html_path
                if src_html.resolve() != target_html.resolve():
                    import shutil
                    shutil.copy2(src_html, target_html)

        # Generate markdown reports
        gen_rep_json = final_dir / "generation_report.json"
        gen_rep_md = final_dir / "generation_report.md"
        qa_rep_json = final_dir / "quality_authority_report.json"
        qa_rep_md = final_dir / "quality_authority_report.md"
        repair_hist_json = final_dir / "repair_history.json"
        prov_json = final_dir / "provenance.json"
        conv_json = final_dir / "convergence_report.json"
        manifest_json = final_dir / "manifest.json"
        warnings_md = None

        # Write canonical manifest.json
        manifest_data = {
            "job_id": context.job_id,
            "artifact_type": context.artifact_type,
            "source_references": list(context.get_source_references()),
            "final_state": ProductionState.EXPORTED.value,
            "decision": report.decision.value,
            "overall_quality_score": report.overall_quality_score,
            "total_iterations": context.iteration,
            "convergence_state": context.convergence_state.value,
            "iteration_hashes": [
                {"iteration": it.iteration, "blueprint_hash": it.blueprint_hash, "pdf_hash": it.pdf_hash}
                for it in version_manager.iterations
            ],
            "repair_log": [r.model_dump(mode="json") for r in context.repair_history],
            "timing_metrics": context.timing_metrics,
        }
        with open(manifest_json, "w", encoding="utf-8") as f:
            json.dump(manifest_data, f, indent=2, default=str)

        # Write quality json and markdown
        with open(qa_rep_json, "w", encoding="utf-8") as f:
            f.write(report.model_dump_json(indent=2))

        qa_md_content = cls._format_quality_markdown(report)
        with open(qa_rep_md, "w", encoding="utf-8") as f:
            f.write(qa_md_content)

        # Write repair history
        rep_hist_data = [r.model_dump(mode="json") for r in context.repair_history]
        with open(repair_hist_json, "w", encoding="utf-8") as f:
            json.dump(rep_hist_data, f, indent=2, default=str)

        # Write convergence report
        conv_data = {
            "convergence_state": context.convergence_state.value,
            "total_iterations": context.iteration,
            "final_score": report.overall_quality_score,
            "decision": report.decision.value,
        }
        with open(conv_json, "w", encoding="utf-8") as f:
            json.dump(conv_data, f, indent=2)

        # Write provenance
        prov_data = {
            "job_id": context.job_id,
            "artifact_type": context.artifact_type,
            "timing_metrics": context.timing_metrics,
            "source_references": list(context.get_source_references()),
        }
        with open(prov_json, "w", encoding="utf-8") as f:
            json.dump(prov_data, f, indent=2)

        # Write generation report
        gen_data = {
            "job_id": context.job_id,
            "artifact_type": context.artifact_type,
            "success": True,
            "decision": report.decision.value,
            "overall_score": report.overall_quality_score,
            "iterations_required": context.iteration,
            "timing_metrics": context.timing_metrics,
        }
        with open(gen_rep_json, "w", encoding="utf-8") as f:
            json.dump(gen_data, f, indent=2)

        gen_md_content = (
            f"# Generation Report: {context.job_id}\n\n"
            f"- **Artifact Type**: {context.artifact_type}\n"
            f"- **Decision**: {report.decision.value}\n"
            f"- **Quality Score**: {report.overall_quality_score:.3f}\n"
            f"- **Iterations**: {context.iteration}\n"
            f"- **Total Duration**: {sum(context.timing_metrics.values()):.2f}s\n"
        )
        with open(gen_rep_md, "w", encoding="utf-8") as f:
            f.write(gen_md_content)

        if report.warnings:
            warnings_md = final_dir / "warnings.md"
            with open(warnings_md, "w", encoding="utf-8") as f:
                f.write("# Export Warnings\n\n")
                for w in report.warnings:
                    f.write(f"- [WARNING] {w}\n")

        context.transition_state(ProductionState.EXPORTED, reason="Export bundle successfully written.")

        return ExportPackage(
            artifact_path=target_pdf or (final_dir / f"{artifact_name}.pdf"),
            final_dir=final_dir,
            generation_report_json=gen_rep_json,
            generation_report_md=gen_rep_md,
            quality_report_json=qa_rep_json,
            quality_report_md=qa_rep_md,
            repair_history_json=repair_hist_json,
            provenance_json=prov_json,
            convergence_report_json=conv_json,
            warnings_md=warnings_md,
        )

    @staticmethod
    def _format_quality_markdown(report: UnifiedQualityReport) -> str:
        md = [
            f"# Unified Quality Authority Report: {report.artifact_type}",
            f"**Authoritative Decision**: `{report.decision.value}`  ",
            f"**Can Export**: `{report.can_export}`  ",
            f"**Overall Quality Score**: `{report.overall_quality_score:.3f}`  ",
            "",
            "## Domain Scores",
        ]
        for d, s in report.domain_scores.items():
            md.append(f"- **{d}**: `{s:.3f}`")
        if report.hard_blockers:
            md.append("\n## Hard Blockers")
            for b in report.hard_blockers:
                md.append(f"- [BLOCKER] {b}")
        if report.warnings:
            md.append("\n## Warnings")
            for w in report.warnings:
                md.append(f"- [WARNING] {w}")
        return "\n".join(md)
