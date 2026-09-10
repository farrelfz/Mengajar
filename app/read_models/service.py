"""Atomic append-only persistence and projection adapters for Phase 7."""
from __future__ import annotations

import hashlib
import json
import os
import tempfile
import time
import threading
from pathlib import Path
from typing import Any

from app.read_models.contracts import (
    ArtifactProjection, BenchmarkProjection, ConvergenceProjection, JobIdentity,
    JobMetadata, JobSnapshot, JobStateProjection, ObservabilityProjection,
    ProjectionDiagnostic, QualityProjection, RepairProjection, ReviewProjection,
    SnapshotManifest,
)


def _plain(value: Any) -> Any:
    """Convert only for serialization; never derive a decision or score."""
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if hasattr(value, "model_dump"):
        return _plain(value.model_dump(mode="json"))
    if hasattr(value, "value"):
        return _plain(value.value)
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {str(k): _plain(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_plain(v) for v in value]
    if hasattr(value, "__dict__"):
        return _plain(vars(value))
    return str(value)


def _atomic_json(path: Path, payload: dict[str, Any]) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(raw)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, path)
        return hashlib.sha256(raw).hexdigest()
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)


class JobReadModelService:
    """Writes immutable snapshots. Failures are returned as diagnostics, never raised."""
    _locks: dict[str, threading.RLock] = {}
    _locks_guard = threading.Lock()
    def __init__(self, root: Path | str = "artifacts/read_models/jobs") -> None:
        self.root = Path(root)
    def _lock_for(self, job_id: str) -> threading.RLock:
        key = str(self._dir(job_id))
        with self._locks_guard:
            return self._locks.setdefault(key, threading.RLock())

    def _dir(self, job_id: str) -> Path:
        if not job_id or "/" in job_id or "\\" in job_id:
            raise ValueError("job_id must be a simple identifier")
        return self.root / job_id

    def _manifest(self, job_id: str) -> SnapshotManifest:
        path = self._dir(job_id) / "manifest.json"
        if not path.exists():
            # The manifest is an index/cache, never the source of truth.  Recover
            # numbering from immutable files so a lost cache cannot overwrite one.
            files = sorted((self._dir(job_id) / "snapshots").glob("snapshot_*.json"))
            entries = []
            for item in files:
                entries.append({"filename": item.name, "sha256": hashlib.sha256(item.read_bytes()).hexdigest(), "timestamp": item.stat().st_mtime})
            return SnapshotManifest(job_id=job_id, snapshot_count=len(entries), latest_snapshot=entries[-1]["filename"] if entries else None, snapshots=tuple(entries))
        return SnapshotManifest.model_validate_json(path.read_text(encoding="utf-8"))

    def append(self, snapshot: JobSnapshot, *, observation_key: str | None = None) -> tuple[JobSnapshot | None, ProjectionDiagnostic | None]:
        """Validate then atomically append. A write error is isolated from callers."""
        try:
            # Serialise local writers so two lifecycle callbacks cannot allocate
            # the same sequence number.  Atomic files still protect readers.
            with self._lock_for(snapshot.identity.job_id):
                directory = self._dir(snapshot.identity.job_id)
                manifest = self._manifest(snapshot.identity.job_id)
                if observation_key:
                    for entry in manifest.snapshots:
                        if entry.get("observation_key") == observation_key:
                            existing = directory / "snapshots" / entry["filename"]
                            return JobSnapshot.model_validate_json(existing.read_text(encoding="utf-8")), None
                number = manifest.snapshot_count + 1
                snapshot = snapshot.model_copy(update={"snapshot_number": number, "timestamp": time.time()})
                filename = f"snapshot_{number:06d}.json"
                digest = _atomic_json(directory / "snapshots" / filename, snapshot.model_dump(mode="json"))
                entry = {"filename": filename, "sha256": digest, "timestamp": snapshot.timestamp}
                if observation_key:
                    entry["observation_key"] = observation_key
                manifest = manifest.model_copy(update={
                    "snapshot_count": number, "latest_snapshot": filename,
                    "snapshots": (*manifest.snapshots, entry),
                })
                _atomic_json(directory / "manifest.json", manifest.model_dump(mode="json"))
                _atomic_json(directory / "latest.json", snapshot.model_dump(mode="json"))
                return snapshot, None
        except Exception as exc:  # observation must never fail production
            return None, ProjectionDiagnostic(code="OBSERVABILITY_PROJECTION_WRITE_FAILED", message=str(exc), severity="ERROR", timestamp=time.time())

    def rebuild_latest(self, job_id: str) -> tuple[JobSnapshot | None, tuple[ProjectionDiagnostic, ...]]:
        diagnostics: list[ProjectionDiagnostic] = []
        latest: JobSnapshot | None = None
        try:
            manifest = self._manifest(job_id)
            expected_hashes = {item["filename"]: item.get("sha256") for item in manifest.snapshots}
            files = sorted((self._dir(job_id) / "snapshots").glob("snapshot_*.json"))
            for path in files:
                try:
                    actual_hash = hashlib.sha256(path.read_bytes()).hexdigest()
                    expected_hash = expected_hashes.get(path.name)
                    if expected_hash and actual_hash != expected_hash:
                        diagnostics.append(ProjectionDiagnostic(code="SNAPSHOT_HASH_MISMATCH", message=f"{path.name} failed manifest SHA-256 verification", timestamp=time.time()))
                        continue
                    candidate = JobSnapshot.model_validate_json(path.read_text(encoding="utf-8"))
                    if latest is None or candidate.snapshot_number > latest.snapshot_number:
                        latest = candidate
                except Exception as exc:
                    diagnostics.append(ProjectionDiagnostic(code="CORRUPTED_SNAPSHOT_IGNORED", message=f"{path.name}: {exc}", timestamp=time.time()))
            if latest:
                _atomic_json(self._dir(job_id) / "latest.json", latest.model_dump(mode="json"))
                # Restore a missing registry/cache from the immutable snapshots.
                entries = tuple({"filename": p.name, "sha256": hashlib.sha256(p.read_bytes()).hexdigest(), "timestamp": p.stat().st_mtime} for p in files)
                restored = SnapshotManifest(job_id=job_id, snapshot_count=len(entries), latest_snapshot=f"snapshot_{latest.snapshot_number:06d}.json", snapshots=entries)
                _atomic_json(self._dir(job_id) / "manifest.json", restored.model_dump(mode="json"))
        except Exception as exc:
            diagnostics.append(ProjectionDiagnostic(code="READ_MODEL_REBUILD_FAILED", message=str(exc), severity="ERROR", timestamp=time.time()))
        return latest, tuple(diagnostics)

    def observe_web_job(self, job: Any, *, result: Any = None, diagnostic: ProjectionDiagnostic | None = None, observation_event: str = "OBSERVATION_WEB") -> tuple[JobSnapshot | None, ProjectionDiagnostic | None]:
        """Adapter for existing web jobs; copies observed fields without interpretation."""
        now = time.time()
        quality = getattr(result, "quality_report", None) or getattr(result, "quality_authority_result", None)
        if quality is None:
            quality = getattr(result, "quality", None)
        q = _plain(quality) if quality is not None else {}
        decision = q.get("decision") if isinstance(q, dict) else None
        if isinstance(decision, dict): decision = decision.get("status") or decision.get("decision")
        transitions = ({"from_state": "WEB", "to_state": getattr(job, "status", "UNKNOWN"), "timestamp": now,
                        "iteration": 0, "reason": getattr(job, "current_step", ""), "source": "app.web.server.JobState"},)
        inventory = []
        if getattr(job, "pdf_url", None):
            inventory.append({"kind": "pdf", "url": job.pdf_url, "filename": getattr(job, "pdf_filename", None)})
        snapshot = JobSnapshot(
            snapshot_number=0, timestamp=now,
            identity=JobIdentity(job_id=job.job_id, artifact_type=getattr(result, "artifact_type", None), created_at=getattr(job, "created_at", now)),
            metadata=JobMetadata(observed_value={"format": getattr(job, "format", None)}, source="app.web.server.JobState", timestamp=now, title=getattr(job, "title", None), model=getattr(job, "model", None)),
            state=JobStateProjection(observed_value=getattr(job, "status", "UNKNOWN"), source="app.web.server.JobState", timestamp=now, current_state=getattr(job, "status", "UNKNOWN").upper(), transitions=transitions, terminal=getattr(job, "status", "") in {"completed", "failed", "blocked", "cancelled"}),
            quality=QualityProjection(observed_value=q, source=type(quality).__name__ if quality else "absent", timestamp=now, overall_quality_score=q.get("overall_quality_score") if isinstance(q, dict) else None, domain_scores=q.get("domain_scores", {}) if isinstance(q, dict) else {}, dimension_scores=q.get("dimension_scores", {}) if isinstance(q, dict) else {}, hard_blockers=tuple(q.get("hard_blockers", ())) if isinstance(q, dict) else (), warnings=tuple(q.get("warnings", ())) if isinstance(q, dict) else (), findings=tuple(_plain(x) for x in q.get("findings", ())) if isinstance(q, dict) else (), decision=str(decision) if decision else None, export_eligible=q.get("can_export") if isinstance(q, dict) else None),
            repair=RepairProjection(observed_value={}, source="pipeline result", timestamp=now),
            convergence=ConvergenceProjection(observed_value={}, source="pipeline result", timestamp=now),
            benchmark=BenchmarkProjection(observed_value={}, source="benchmarking domain", timestamp=now),
            review=ReviewProjection(observed_value={}, source="review domain", timestamp=now),
            artifacts=ArtifactProjection(observed_value=inventory, source="app.web.server.JobState", timestamp=now, inventory=tuple(inventory)),
            observability=ObservabilityProjection(observed_value={"percent": getattr(job, "percent", 0)}, source="app.web.server.JobState", timestamp=now, errors=tuple([getattr(job, "error")] if getattr(job, "error", None) else ()), warnings=()),
            diagnostics=(diagnostic,) if diagnostic else (),
        )
        key = hashlib.sha256(f"{job.job_id}|{observation_event}|{getattr(job, 'status', '')}|{getattr(job, 'percent', 0)}|{getattr(job, 'error', '')}".encode()).hexdigest()
        return self.append(snapshot, observation_key=key)

    def observe_production_context(self, context: Any, *, benchmark: Any = None, review: Any = None, observation_event: str = "OBSERVATION_CONTEXT") -> tuple[JobSnapshot | None, ProjectionDiagnostic | None]:
        """Project the canonical production context without changing it.

        This adapter is intentionally duck-typed so orchestration callers can use
        it at a checkpoint without coupling Phase 7 to a pipeline implementation.
        """
        now = time.time()
        quality_obj = getattr(context, "quality_authority_result", None)
        quality = _plain(quality_obj) if quality_obj else {}
        machine = getattr(context, "state_machine", None)
        history = getattr(machine, "history", ())
        transitions = tuple(_plain(record) | {"source": "ProductionStateMachine"} for record in history)
        repairs = tuple(_plain(item) for item in getattr(context, "repair_history", ()))
        raw_output_dir = getattr(context, "output_dir", None)
        output_dir = Path(raw_output_dir) if raw_output_dir else None
        inventory = []
        if output_dir and output_dir.exists():
            for path in sorted(p for p in output_dir.rglob("*") if p.is_file()):
                inventory.append({"kind": path.suffix.lstrip(".") or "file", "path": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
        benchmark_data, review_data = _plain(benchmark) if benchmark else {}, _plain(review) if review else {}
        state = getattr(getattr(context, "state", None), "value", str(getattr(context, "state", "UNKNOWN")))
        snapshot = JobSnapshot(
            snapshot_number=0, timestamp=now,
            identity=JobIdentity(job_id=context.job_id, artifact_type=getattr(context, "artifact_type", None), created_at=now),
            metadata=JobMetadata(observed_value=_plain(getattr(context, "source_metadata", {})), source="ArtifactProductionContext", timestamp=now, source_hint=str(getattr(context, "source_input", ""))),
            state=JobStateProjection(observed_value=state, source="ProductionStateMachine", timestamp=now, current_state=state, transitions=transitions, terminal=state in {"EXPORTED", "BLOCKED", "MANUAL_REVIEW_REQUIRED", "FAILED", "CANCELLED"}),
            quality=QualityProjection(observed_value=quality, source="UnifiedQualityAuthority" if quality else "absent", timestamp=now, overall_quality_score=quality.get("overall_quality_score"), domain_scores=quality.get("domain_scores", {}), dimension_scores=quality.get("dimension_scores", {}), hard_blockers=tuple(quality.get("hard_blockers", ())), warnings=tuple(quality.get("warnings", ())), findings=tuple(quality.get("findings", ())), decision=str(quality.get("decision")) if quality.get("decision") else None, export_eligible=quality.get("can_export")),
            repair=RepairProjection(observed_value=repairs, source="ArtifactProductionContext.repair_history", timestamp=now, iterations=repairs),
            convergence=ConvergenceProjection(observed_value=_plain(getattr(context, "convergence_state", None)), source="ArtifactProductionContext.convergence_state", timestamp=now, state=str(getattr(getattr(context, "convergence_state", None), "value", getattr(context, "convergence_state", None))), current_iteration=getattr(context, "iteration", 0), diagnostics={}),
            benchmark=BenchmarkProjection(observed_value=benchmark_data, source="CertificationEngine" if benchmark else "absent", timestamp=now, certification_decision=str(benchmark_data.get("decision")) if isinstance(benchmark_data, dict) and benchmark_data.get("decision") else None, details=benchmark_data if isinstance(benchmark_data, dict) else {}),
            review=ReviewProjection(observed_value=review_data, source="ReviewStateMachine" if review else "absent", timestamp=now, case_id=review_data.get("case_id") if isinstance(review_data, dict) else None, state=str(review_data.get("state")) if isinstance(review_data, dict) and review_data.get("state") else None, directives=tuple(review_data.get("directives", ())) if isinstance(review_data, dict) else ()),
            artifacts=ArtifactProjection(observed_value=inventory, source="ArtifactProductionContext.output_dir", timestamp=now, inventory=tuple(inventory)),
            observability=ObservabilityProjection(observed_value=_plain(getattr(context, "timing_metrics", {})), source="ArtifactProductionContext", timestamp=now, stage_durations=_plain(getattr(context, "timing_metrics", {})), errors=tuple(getattr(context, "errors", ())), warnings=tuple(getattr(context, "warnings", ()))),
        )
        transitions_digest = hashlib.sha256(json.dumps(transitions, sort_keys=True, default=str).encode()).hexdigest()
        key = hashlib.sha256(f"{context.job_id}|{observation_event}|{state}|{getattr(context, 'iteration', 0)}|{transitions_digest}".encode()).hexdigest()
        return self.append(snapshot, observation_key=key)
