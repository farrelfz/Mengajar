"""
Unit tests for Artifact Lifecycle and Registry.
"""

import pytest
from app.orchestration.artifacts import ArtifactRecord, ArtifactRegistry
from app.orchestration.contracts import ArtifactLifecycleState


def test_artifact_registry_tracks_state():
    reg = ArtifactRegistry()
    rec = ArtifactRecord(
        artifact_id="art_001",
        job_id="job_art_1",
        artifact_type="pdf",
        producer_stage="rendering",
        status=ArtifactLifecycleState.DECLARED,
    )
    reg.register(rec)

    assert len(reg.get_job_artifacts("job_art_1")) == 1

    reg.update_status("art_001", ArtifactLifecycleState.APPROVED)
    arts = reg.get_job_artifacts("job_art_1")
    assert arts[0].status == ArtifactLifecycleState.APPROVED
