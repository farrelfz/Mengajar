"""Canonical best-effort observation boundary for all production callers.

This module is deliberately passive: it copies already-existing context/result
facts into the read model and turns any write problem into a bounded log record.
"""
from __future__ import annotations

import hashlib
import logging
import os
import time
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from app.read_models.service import JobReadModelService

logger = logging.getLogger(__name__)

OBSERVATION_JOB_CREATED = "OBSERVATION_JOB_CREATED"
OBSERVATION_PIPELINE_STARTED = "OBSERVATION_PIPELINE_STARTED"
OBSERVATION_QUALITY_AVAILABLE = "OBSERVATION_QUALITY_AVAILABLE"
OBSERVATION_REPAIR_ITERATION = "OBSERVATION_REPAIR_ITERATION"
OBSERVATION_CONVERGENCE_UPDATED = "OBSERVATION_CONVERGENCE_UPDATED"
OBSERVATION_TERMINAL = "OBSERVATION_TERMINAL"


def resolve_environment(*, explicit: str | None = None, output_dir: Path | str | None = None) -> str:
    """Select an isolated root without changing production identity semantics."""
    if explicit in {"production", "benchmark", "test"}:
        return explicit
    if os.environ.get("PYTEST_CURRENT_TEST"):
        return "test"
    if output_dir and "benchmark" in str(output_dir).lower():
        return "benchmark"
    return "production"


def read_model_root(environment: str) -> Path:
    # Preserve the existing production path for backwards compatibility.
    return Path("artifacts/read_models/jobs") if environment == "production" else Path("artifacts/read_models") / environment / "jobs"


class ProductionObservationAdapter:
    """Single non-authoritative observation contract reused by all entrypoints."""
    def __init__(self, *, environment: str | None = None, output_dir: Path | str | None = None, service: JobReadModelService | None = None) -> None:
        self.environment = resolve_environment(explicit=environment, output_dir=output_dir)
        self.service = service or JobReadModelService(read_model_root(self.environment))

    def observe_context(self, context: Any, event: str) -> None:
        try:
            snapshot, diagnostic = self.service.observe_production_context(context, observation_event=event)
            if diagnostic:
                self._diagnostic(context.job_id, event, diagnostic)
        except Exception as exc:  # never mask production behaviour
            self._diagnostic(getattr(context, "job_id", None), event, exc)

    def observe_material_result(self, result: Any, *, event: str = OBSERVATION_TERMINAL, title: str | None = None) -> None:
        """Adapt legacy MaterialProductionPipeline output without introducing a second pipeline."""
        try:
            final_state = "EXPORTED" if getattr(result, "success", False) else "FAILED"
            decision = getattr(result, "export_decision", None)
            decision_value = getattr(decision, "status", decision)
            if str(getattr(decision_value, "value", decision_value)) == "BLOCKED":
                final_state = "BLOCKED"
            job = SimpleNamespace(
                job_id=getattr(result, "job_id", "unknown_job"), title=title, model=None,
                created_at=time.time(), status=final_state.lower(), current_step=event,
                pdf_url=None, pdf_filename=Path(getattr(result, "pdf_path", "")).name or None,
                percent=100, error="; ".join(getattr(result, "errors", ()) or ()),
            )
            _, diagnostic = self.service.observe_web_job(job, result=result, observation_event=event)
            if diagnostic:
                self._diagnostic(job.job_id, event, diagnostic)
        except Exception as exc:
            self._diagnostic(getattr(result, "job_id", None), event, exc)

    @staticmethod
    def _diagnostic(job_id: str | None, stage: str, error: Any) -> None:
        # Logging is the bounded fallback.  It never attempts a second snapshot.
        logger.warning(
            "OBSERVABILITY_PROJECTION_WRITE_FAILED job_id=%s stage=%s exception_type=%s detail=%s recoverable=true",
            job_id, stage, type(error).__name__, error,
        )
