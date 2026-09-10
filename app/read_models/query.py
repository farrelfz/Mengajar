"""Read-only query boundary over immutable job snapshots."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any
from app.read_models.contracts import ProjectionDiagnostic
from app.read_models.service import JobReadModelService

class JobReadQueryService:
    def __init__(self, root: Path | str = "artifacts/read_models/jobs") -> None:
        self.service = JobReadModelService(root)
        self.root = Path(root)
    def list_jobs(self) -> dict[str, Any]:
        jobs=[]; diagnostics=[]
        if not self.root.exists(): return {"jobs": jobs, "diagnostics": diagnostics}
        for directory in sorted(p for p in self.root.iterdir() if p.is_dir()):
            item=self.get_job(directory.name)
            if item["snapshot"]: jobs.append(item["snapshot"])
            diagnostics.extend(item["diagnostics"])
        return {"jobs": jobs, "diagnostics": diagnostics}
    def get_job(self, job_id: str) -> dict[str, Any]:
        path=self.service._dir(job_id) / "latest.json"; diagnostics=[]
        try:
            if path.exists(): return {"snapshot": json.loads(path.read_text(encoding="utf-8")), "diagnostics": diagnostics}
        except Exception as exc:
            diagnostics.append({"code":"STALE_OR_CORRUPT_LATEST", "message":str(exc), "severity":"WARNING"})
        snapshot, rebuild_diags=self.service.rebuild_latest(job_id)
        diagnostics.extend(d.model_dump() for d in rebuild_diags)
        return {"snapshot": snapshot.model_dump(mode="json") if snapshot else None, "diagnostics": diagnostics}
    def get_job_timeline(self, job_id: str) -> dict[str, Any]: return self._section(job_id, "state", "transitions")
    def get_quality_summary(self, job_id: str) -> dict[str, Any]: return self._section(job_id, "quality")
    def get_repair_history(self, job_id: str) -> dict[str, Any]: return self._section(job_id, "repair")
    def get_convergence_summary(self, job_id: str) -> dict[str, Any]: return self._section(job_id, "convergence")
    def get_benchmark_summary(self, job_id: str) -> dict[str, Any]: return self._section(job_id, "benchmark")
    def get_review_summary(self, job_id: str) -> dict[str, Any]: return self._section(job_id, "review")
    def get_artifact_inventory(self, job_id: str) -> dict[str, Any]: return self._section(job_id, "artifacts")
    def _section(self, job_id: str, section: str, key: str | None=None) -> dict[str, Any]:
        result=self.get_job(job_id); snapshot=result["snapshot"]
        if not snapshot: return {"data": None, "diagnostics": result["diagnostics"] + [{"code":"JOB_NOT_PROJECTED", "message":"No readable snapshot", "severity":"WARNING"}]}
        data=snapshot.get(section, {}); return {"data": data.get(key) if key else data, "diagnostics": result["diagnostics"]}
