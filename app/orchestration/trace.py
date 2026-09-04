"""
Execution Trace: Machine-readable event stream capturing the lifecycle of each job.
"""

from __future__ import annotations

import time
from typing import Any
from pydantic import BaseModel, Field


class ExecutionEvent(BaseModel):
    sequence: int
    timestamp: float
    job_id: str
    stage_id: str | None = None
    event_type: str
    message: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)


class ExecutionTrace(BaseModel):
    job_id: str
    events: list[ExecutionEvent] = Field(default_factory=list)

    def log_event(self, event_type: str, stage_id: str | None = None, message: str = "", metadata: dict[str, Any] | None = None) -> None:
        seq = len(self.events) + 1
        ev = ExecutionEvent(
            sequence=seq,
            timestamp=time.time(),
            job_id=self.job_id,
            stage_id=stage_id,
            event_type=event_type,
            message=message,
            metadata=metadata or {},
        )
        self.events.append(ev)
