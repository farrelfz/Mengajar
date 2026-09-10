"""
Universal Knowledge Core — Comprehensive Fidelity Report.

Phase 2B Controlled Renderer Execution & Artifact Fidelity:
Aggregates multi-artifact fidelity evaluations into a system-wide audit report.
"""

from __future__ import annotations

import json
import time
from typing import Any, Dict, List, Tuple
from pydantic import BaseModel, ConfigDict, Field

from app.quality.artifact_fidelity.base import ArtifactFidelityEvaluation


class ComprehensiveFidelityReport(BaseModel):
    """System-wide fidelity evaluation aggregating all four artifacts."""
    model_config = ConfigDict(frozen=True)

    report_id: str
    manifest_title: str
    evaluations: Dict[str, ArtifactFidelityEvaluation]
    macro_fidelity_score: float
    all_passing: bool
    total_violations: int = 0
    total_warnings: int = 0
    metadata: Dict[str, Any] = Field(default_factory=dict)
    generated_at: float = Field(default_factory=time.time)

    def to_markdown(self) -> str:
        """Generates a GitHub-flavored Markdown audit report."""
        lines = [
            f"# PHASE 2B CONTROLLED RENDERER FIDELITY REPORT",
            f"**Manifest Title**: {self.manifest_title}",
            f"**Report ID**: `{self.report_id}`",
            f"**Macro Fidelity Score**: `{self.macro_fidelity_score:.3f}`",
            f"**System Status**: `{'PASS' if self.all_passing else 'FAIL'}`",
            "",
            "## Artifact Multi-Dimensional Fidelity Matrix",
            "| Artifact Type | Overall Score | Status | Semantic | Structural | Specific | Visual | Traceability | Reliability |",
            "| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |",
        ]

        for art_type, eval_res in self.evaluations.items():
            status_badge = "✅ PASS" if eval_res.is_passing else "❌ FAIL"
            lines.append(
                f"| **{art_type}** | `{eval_res.overall_score:.3f}` | {status_badge} | "
                f"`{eval_res.semantic_fidelity:.2f}` | `{eval_res.structural_fidelity:.2f}` | "
                f"`{eval_res.artifact_specific_fidelity:.2f}` | `{eval_res.visual_layout_fidelity:.2f}` | "
                f"`{eval_res.traceability_fidelity:.2f}` | `{eval_res.execution_reliability:.2f}` |"
            )

        lines.extend([
            "",
            "## Traceability & Anti-Corruption Audit",
        ])

        for art_type, eval_res in self.evaluations.items():
            lines.append(f"### {art_type}")
            lines.append(f"- **Total Violations**: {len(eval_res.violations)}")
            lines.append(f"- **Total Warnings**: {len(eval_res.warnings)}")
            for v in eval_res.violations:
                lines.append(f"  - ❌ **Violation**: {v}")
            for w in eval_res.warnings:
                lines.append(f"  - ⚠️ **Warning**: {w}")
            lines.append(f"- **Traceability Stats**: `{eval_res.traceability_stats}`")
            lines.append("")

        return "\n".join(lines)
