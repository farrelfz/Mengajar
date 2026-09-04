"""
Lineage tracking mapping production runs, input parameters, and generated files.
"""

from __future__ import annotations

from typing import Any, Optional

from app.observability.contracts import ArtifactLineageRecord, EventType
from app.observability.context import ObservabilityContextManager
from app.observability.tracing import get_current_report, record_event


def record_artifact(
    artifact_id: str,
    artifact_path: str,
    artifact_type: str,
    format_id: Optional[str] = None,
    page_count: Optional[int] = None,
    parent_artifacts: Optional[list[str]] = None,
    metadata: Optional[dict[str, Any]] = None,
) -> None:
    """Register output artifact metadata into the active trace reports lineage context."""
    if not ObservabilityContextManager.is_enabled():
        return

    report = get_current_report()
    if not report:
        return

    record = ArtifactLineageRecord(
        artifact_id=artifact_id,
        artifact_path=artifact_path,
        artifact_type=artifact_type,
        source_run_id=report.run_summary.run_id,
        trace_id=report.run_summary.trace_id,
        format_id=format_id,
        page_count=page_count,
        parent_artifacts=parent_artifacts or [],
        metadata=metadata or {},
    )
    report.artifact_lineage.append(record)

    record_event(
        EventType.ARTIFACT_RENDERED
        if "pdf" in artifact_type.lower() or "html" in artifact_type.lower()
        else EventType.ARTIFACT_VALIDATED,
        message=f"Artifact registered to lineage: {artifact_id} ({artifact_type})",
        attributes={"path": artifact_path, "parent_artifacts": parent_artifacts or []},
    )


class ArtifactLineageGraph:
    """Graph structure to trace outputs back to their planning dependencies."""

    def __init__(self, records: list[ArtifactLineageRecord]) -> None:
        self.records = records
        self.nodes: dict[str, ArtifactLineageRecord] = {
            r.artifact_id: r for r in records
        }
        self.edges_out: dict[str, set[str]] = {}
        self.edges_in: dict[str, set[str]] = {}

        for r in records:
            for parent in r.parent_artifacts:
                self.edges_out.setdefault(parent, set()).add(r.artifact_id)
                self.edges_in.setdefault(r.artifact_id, set()).add(parent)

    def get_ancestors(self, artifact_id: str) -> list[str]:
        """Traverse upstream parents to retrieve all dependencies of an artifact."""
        visited: set[str] = set()
        stack = list(self.edges_in.get(artifact_id, set()))
        while stack:
            curr = stack.pop()
            if curr not in visited:
                visited.add(curr)
                stack.extend(self.edges_in.get(curr, set()))
        return sorted(list(visited))

    def get_descendants(self, artifact_id: str) -> list[str]:
        """Traverse downstream children of an artifact."""
        visited: set[str] = set()
        stack = list(self.edges_out.get(artifact_id, set()))
        while stack:
            curr = stack.pop()
            if curr not in visited:
                visited.add(curr)
                stack.extend(self.edges_out.get(curr, set()))
        return sorted(list(visited))
