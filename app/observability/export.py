"""
Export functions for rendering deterministic JSON manifests.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.observability.tracing import active_reports


def make_relative(path_str: str) -> str:
    """Safely convert absolute file paths to workspace-relative ones for determinism."""
    try:
        p = Path(path_str).resolve()
        workspace = Path("/home/si/Codingan/Mencari nafkah/Mengajar").resolve()
        if workspace in p.parents or p == workspace:
            return str(p.relative_to(workspace))
    except Exception:
        pass
    return path_str


def export_report(run_id: str) -> dict[str, Any]:
    """Retrieve and serialize full run telemetries with sorted keys for structural determinism."""
    report = active_reports.get(run_id)
    if not report:
        return {}

    # Use natural sequence order for spans, events, and errors
    spans = [s.dict() for s in report.spans]
    events = [e.dict() for e in report.events]
    metrics = sorted(
        [m.dict() for m in report.metrics], key=lambda x: x["name"]
    )
    errors = [er.dict() for er in report.errors]
    lineage = sorted(
        [l.dict() for l in report.artifact_lineage], key=lambda x: x["artifact_id"]
    )

    # Convert absolute paths in lineage
    for item in lineage:
        item["artifact_path"] = make_relative(item["artifact_path"])

    summary = report.run_summary.dict()
    diagnostics = report.diagnostics.dict() if report.diagnostics else None

    return {
        "schema_version": "1.0.0",
        "run": summary,
        "spans": spans,
        "events": events,
        "metrics": metrics,
        "errors": errors,
        "lineage": lineage,
        "diagnostics": diagnostics,
    }


def export_json(run_id: str, dest_path: str) -> None:
    """Write serialized trace to a file on disk."""
    data = export_report(run_id)
    p = Path(dest_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2), encoding="utf-8")
