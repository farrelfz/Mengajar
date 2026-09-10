"""
Universal Document Intelligence System V5 — Causal Quality Reporter.

Phase 3A.1: Serializes CanonicalQualityAssessment models into comprehensive,
actionable Markdown and JSON diagnostic reports for future Phase 3B repair.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Tuple

from app.quality.causal.contracts import CanonicalQualityAssessment


class CausalQualityReporter:
    """Generates structured causal diagnostic reports."""

    @classmethod
    def to_markdown(cls, assessment: CanonicalQualityAssessment) -> str:
        lines = [
            f"# Causal Quality & Authority Report — {assessment.artifact_type}",
            f"**Assessment ID**: `{assessment.assessment_id}`",
            f"**PDF Path**: `{assessment.rendered_pdf_path or 'N/A'}`",
            f"**Total Pages**: {assessment.page_count}",
            "",
            "## Executive Decision",
            f"- **Decision**: `{assessment.decision.value}`",
            f"- **Can Export**: `{assessment.can_export}`",
            f"- **Repair Required**: `{assessment.repair_required}`",
            f"- **Manual Review Required**: `{assessment.manual_review_required}`",
            f"- **Overall Quality Score**: `{assessment.overall_quality_score:.3f}`",
            f"- **Rationale**: {assessment.rationale}",
            "",
            "## Dimensional Score Breakdown",
            "| Dimension | Score | Status |",
            "| :--- | :---: | :--- |",
        ]

        for dim, score in assessment.dimensional_scores.items():
            status_icon = "✅ PASS" if score >= 0.85 else ("⚠️ WARN" if score >= 0.70 else "🛑 CRITICAL")
            lines.append(f"| {dim.replace('_', ' ').title()} | `{score:.3f}` | {status_icon} |")

        # Failure Clusters Section
        lines.extend([
            "",
            f"## Failure Clusters & Causal Attribution ({len(assessment.failure_clusters)})",
        ])

        if assessment.failure_clusters:
            for idx, cluster in enumerate(assessment.failure_clusters, start=1):
                cause = cluster.primary_root_cause
                cause_code = cause.cause_code if cause else "UNKNOWN"
                cause_layer = cause.cause_layer.value if cause else "UNKNOWN"
                conf_str = f"{cause.confidence_score:.2f} ({cause.confidence_level.value})" if cause else "N/A"
                allowed_repairs = [r.value for r in cause.allowed_repair_classes] if cause else []
                forbidden_repairs = list(cause.forbidden_repairs) if cause else []

                lines.extend([
                    f"### Cluster {idx:02d}: {cause_code}",
                    f"- **Affected Pages**: {list(cluster.affected_pages)}",
                    f"- **Observed Symptoms**: {[s.value for s in cluster.symptoms]}",
                    f"- **Probable Root Cause**: `{cause_code}`",
                    f"- **Owning Architecture Layer**: `{cause_layer}`",
                    f"- **Causal Confidence**: `{conf_str}`",
                    f"- **Allowed Future Repair**: `{allowed_repairs}`",
                    f"- **Forbidden Repairs**: `{forbidden_repairs}`",
                    f"- **Supporting Evidence**:",
                ])
                if cause and cause.supporting_evidence:
                    for ev in cause.supporting_evidence:
                        lines.append(f"  - {ev}")
                else:
                    lines.append("  - *None specified.*")

                lines.append(f"- **Cluster Rationale**: {cluster.rationale}")
                lines.append("")
        else:
            lines.append("- *Zero failure clusters detected.*")

        # Canonical Failures List
        lines.extend([
            "",
            f"## Canonical Failures ({len(assessment.failures)})",
            "| Code | Category | Severity | Scope | Pages | Symptom |",
            "| :--- | :--- | :---: | :---: | :---: | :--- |",
        ])

        if assessment.failures:
            for f in assessment.failures:
                lines.append(
                    f"| `{f.failure_code.value}` | `{f.category.value}` | `{f.severity.value}` | "
                    f"`{f.scope.value}` | {list(f.affected_pages)} | {f.symptom[:60]}... |"
                )
        else:
            lines.append("| - | - | - | - | - | *Zero failures detected.* |")

        lines.append("")
        return "\n".join(lines)

    @classmethod
    def save_reports(
        cls,
        assessment: CanonicalQualityAssessment,
        output_dir: Path,
        prefix: str = "causal_quality_report",
    ) -> Tuple[Path, Path]:
        output_dir.mkdir(parents=True, exist_ok=True)
        md_path = output_dir / f"{prefix}.md"
        json_path = output_dir / f"{prefix}.json"

        md_content = cls.to_markdown(assessment)
        md_path.write_text(md_content, encoding="utf-8")

        json_data = assessment.model_dump()
        json_path.write_text(json.dumps(json_data, indent=2, default=str), encoding="utf-8")

        return md_path, json_path
