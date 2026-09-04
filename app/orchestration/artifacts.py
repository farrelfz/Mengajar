"""
Artifact Lifecycle: Registry tracking intermediate and output document artifacts.
"""

from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field
from app.orchestration.contracts import ArtifactLifecycleState


class ArtifactRecord(BaseModel):
    artifact_id: str
    job_id: str
    artifact_type: str
    producer_stage: str
    status: ArtifactLifecycleState = ArtifactLifecycleState.DECLARED
    path: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class ArtifactRegistry:
    """Registry maintaining artifact records and transitions."""

    def __init__(self) -> None:
        self._artifacts: dict[str, ArtifactRecord] = {}

    def register(self, record: ArtifactRecord) -> None:
        self._artifacts[record.artifact_id] = record

    def update_status(self, artifact_id: str, status: ArtifactLifecycleState) -> None:
        if artifact_id in self._artifacts:
            self._artifacts[artifact_id].status = status

    def get_job_artifacts(self, job_id: str) -> list[ArtifactRecord]:
        return [a for a in self._artifacts.values() if a.job_id == job_id]
