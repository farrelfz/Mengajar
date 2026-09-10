"""
Universal Document Intelligence System V5 — Benchmark Quality Matrix.

Phase 2C: Governs the 28-artifact benchmark execution matrix (7 Fixtures x 4 Artifact Types).
Generates JSON and Markdown reports with diagnostic truth (never artificial perfection).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, ConfigDict, Field


class BenchmarkArtifactEntry(BaseModel):
    """Single benchmark execution entry for one fixture and one artifact type."""
    model_config = ConfigDict(frozen=True)

    fixture_name: str
    artifact_type: str
    fidelity_score: float
    quality_score: float
    status: str  # PASS, PASS_WITH_WARNINGS, BLOCKED
    critical_failures: tuple[str, ...] = Field(default_factory=tuple)
    warnings: tuple[str, ...] = Field(default_factory=tuple)
    duration_ms: float = 0.0


class BenchmarkQualityMatrix(BaseModel):
    """Full 28-artifact benchmark matrix and diagnostic summary."""
    model_config = ConfigDict(frozen=True)

    matrix_id: str
    entries: tuple[BenchmarkArtifactEntry, ...] = Field(default_factory=tuple)

    @property
    def total_entries(self) -> int:
        return len(self.entries)

    def to_markdown(self) -> str:
        lines = [
            "# PHASE 2C — BENCHMARK QUALITY MATRIX (28 ARTIFACTS)",
            "**Universal Document Intelligence System V5**",
            "",
            "| Fixture | Artifact Type | Fidelity | Quality | Decision Status | Blocker / Primary Finding |",
            "| :--- | :--- | :---: | :---: | :---: | :--- |",
        ]
        for e in self.entries:
            blocker = e.critical_failures[0] if e.critical_failures else ("None" if not e.warnings else e.warnings[0])
            status_icon = "✅ PASS" if e.status == "PASS" else ("⚠️ WARN" if e.status == "PASS_WITH_WARNINGS" else "🛑 BLOCKED")
            lines.append(
                f"| **{e.fixture_name}** | {e.artifact_type} | `{e.fidelity_score:.3f}` | `{e.quality_score:.3f}` | {status_icon} | {blocker} |"
            )
        lines.append("")
        return "\n".join(lines)

    def save_reports(self, output_dir: Path) -> Tuple[Path, Path]:
        output_dir.mkdir(parents=True, exist_ok=True)
        md_path = output_dir / "benchmark_quality_matrix.md"
        json_path = output_dir / "benchmark_quality_matrix.json"

        md_path.write_text(self.to_markdown(), encoding="utf-8")
        
        json_data = {
            "matrix_id": self.matrix_id,
            "total_entries": self.total_entries,
            "entries": [e.model_dump() for e in self.entries],
        }
        json_path.write_text(json.dumps(json_data, indent=2), encoding="utf-8")

        return md_path, json_path
