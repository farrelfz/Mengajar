"""
Unit tests for Machine-Readable Execution Trace.
"""

import pytest
from app.orchestration.trace import ExecutionTrace


def test_execution_trace_logs_ordered_events():
    trace = ExecutionTrace(job_id="job_trace_1")
    trace.log_event("JOB_CREATED", message="Job initialized")
    trace.log_event("STAGE_STARTED", stage_id="validation")
    trace.log_event("STAGE_COMPLETED", stage_id="validation")
    trace.log_event("JOB_COMPLETED")

    assert len(trace.events) == 4
    assert [e.sequence for e in trace.events] == [1, 2, 3, 4]
    assert trace.events[0].event_type == "JOB_CREATED"
    assert trace.events[3].event_type == "JOB_COMPLETED"
