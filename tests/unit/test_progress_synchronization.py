"""
Unit Tests for Pipeline Progress & Stage Synchronization (Phase 11).

Guarantees:
- Exactly 10 canonical pipeline stages exist
- Denominator is strictly derived from len(PIPELINE_STAGES)
- Stage start, completion, and transition logs share identical denominators
- Out-of-bounds stage numbers raise PipelineProgressSynchronizationError
- Repair iterations and QA rounds are dimensionally distinct from pipeline stages
- Terminal status distinguishes expected quality rejection from system crashes
"""

import inspect
import pytest

from app.orchestration.stage_registry import (
    PIPELINE_STAGES,
    TOTAL_PIPELINE_STAGES,
    PipelineStage,
    PipelineStageDefinition,
    PipelineStageRegistry,
    PipelineProgressReporter,
    PipelineTerminalStatus,
)
from app.orchestration.failures import (
    PipelineProgressSynchronizationError,
    PipelineStateSynchronizationError,
)
from app.orchestration.pipeline_state import (
    PipelineState,
    PipelineStatus,
    ExportDecision,
    ExportDecisionStatus,
)
from app.presentation.quality_gate import (
    QualityRound,
    GateResult,
    GateStatus,
    Severity,
    Repairability,
)
from app.presentation.decision_engine import QualityDecisionEngine


# ─────────────────────────────────────────────────────────────
# TEST 1: Exactly 10 pipeline stages exist
# ─────────────────────────────────────────────────────────────
def test_01_exactly_ten_stages_exist():
    assert len(PIPELINE_STAGES) == 10
    stage_numbers = [s.number for s in PIPELINE_STAGES]
    assert stage_numbers == list(range(1, 11))


# ─────────────────────────────────────────────────────────────
# TEST 2: TOTAL_PIPELINE_STAGES equals len(registry)
# ─────────────────────────────────────────────────────────────
def test_02_total_stages_equals_registry_length():
    assert TOTAL_PIPELINE_STAGES == len(PIPELINE_STAGES)
    assert PipelineStageRegistry.total_stages() == len(PIPELINE_STAGES)
    assert TOTAL_PIPELINE_STAGES == 10


# ─────────────────────────────────────────────────────────────
# TEST 3: Stage 1 logs TASK 1/10
# ─────────────────────────────────────────────────────────────
def test_03_stage_1_logs_task_1_of_10():
    captured = []
    reporter = PipelineProgressReporter(log_sink=captured.append)
    reporter.stage_started(PIPELINE_STAGES[0], detail="Parsing AST")

    assert len(captured) >= 1
    log_text = "\n".join(captured)
    assert f"TASK 1/{TOTAL_PIPELINE_STAGES}" in log_text
    assert "Structural Parsing & Source Integrity" in log_text
    assert "/5" not in log_text


# ─────────────────────────────────────────────────────────────
# TEST 4: Stage 10 logs TASK 10/10
# ─────────────────────────────────────────────────────────────
def test_04_stage_10_logs_task_10_of_10():
    captured = []
    reporter = PipelineProgressReporter(log_sink=captured.append)
    reporter.stage_started(PIPELINE_STAGES[9], detail="Convergence loop")

    assert len(captured) >= 1
    log_text = "\n".join(captured)
    assert f"TASK 10/{TOTAL_PIPELINE_STAGES}" in log_text
    assert "Repair & Refinement Loop" in log_text
    assert "/5" not in log_text


# ─────────────────────────────────────────────────────────────
# TEST 5: Completion logs use same denominator
# ─────────────────────────────────────────────────────────────
def test_05_completion_logs_use_canonical_denominator():
    captured = []
    reporter = PipelineProgressReporter(log_sink=captured.append)
    stage = PIPELINE_STAGES[1]  # Stage 2
    reporter.stage_started(stage)
    reporter.stage_completed(stage, message="272 blocks classified", duration=0.15)

    comp_msg = [c for c in captured if "SELESAI" in c][0]
    assert f"[SELESAI 2/{TOTAL_PIPELINE_STAGES}]" in comp_msg
    assert "[SELESAI 2/5]" not in comp_msg
    assert "[SELESAI 2/8]" not in comp_msg


# ─────────────────────────────────────────────────────────────
# TEST 6: Transition logs use same denominator
# ─────────────────────────────────────────────────────────────
def test_06_transition_logs_use_canonical_denominator():
    captured = []
    reporter = PipelineProgressReporter(log_sink=captured.append)
    stage_1 = PIPELINE_STAGES[0]
    stage_2 = PIPELINE_STAGES[1]

    reporter.stage_started(stage_1)
    reporter.stage_completed(stage_1, message="Source verified")
    reporter.stage_transition(stage_2)

    trans_msg = [c for c in captured if "Lanjut ke" in c][0]
    assert f"[{stage_2.number}/{TOTAL_PIPELINE_STAGES}]" in trans_msg
    assert f"[{stage_2.number}/5]" not in trans_msg
    assert stage_2.name in trans_msg


# ─────────────────────────────────────────────────────────────
# TEST 7: No stage can exceed total stage count
# ─────────────────────────────────────────────────────────────
def test_07_no_stage_can_exceed_total_stage_count():
    reporter = PipelineProgressReporter()
    invalid_stage = PipelineStageDefinition(
        number=11,
        key="INVALID_STAGE",
        name="Out of bounds",
        description="Invalid",
    )
    with pytest.raises(PipelineProgressSynchronizationError) as exc_info:
        reporter.stage_started(invalid_stage)
    assert "Invalid progress state: 11/10" in str(exc_info.value)

    invalid_zero_stage = PipelineStageDefinition(
        number=0,
        key="ZERO_STAGE",
        name="Zero index",
        description="Invalid",
    )
    with pytest.raises(PipelineProgressSynchronizationError):
        reporter.stage_started(invalid_zero_stage)


# ─────────────────────────────────────────────────────────────
# TEST 8: No hardcoded total_tasks parameter allowed in reporter
# ─────────────────────────────────────────────────────────────
def test_08_no_hardcoded_total_tasks_parameter_in_reporter():
    sig_start = inspect.signature(PipelineProgressReporter.stage_started)
    assert "total_tasks" not in sig_start.parameters
    assert "total_stages" not in sig_start.parameters

    sig_done = inspect.signature(PipelineProgressReporter.stage_completed)
    assert "total_tasks" not in sig_done.parameters
    assert "total_stages" not in sig_done.parameters

    sig_trans = inspect.signature(PipelineProgressReporter.stage_transition)
    assert "total_tasks" not in sig_trans.parameters
    assert "total_stages" not in sig_trans.parameters


# ─────────────────────────────────────────────────────────────
# TEST 9: Repair iteration does not increment pipeline task number
# ─────────────────────────────────────────────────────────────
def test_09_repair_iteration_does_not_increment_task_number():
    captured = []
    reporter = PipelineProgressReporter(log_sink=captured.append)
    stage_10 = PIPELINE_STAGES[9]

    reporter.stage_started(stage_10)
    iter_1_log = reporter.repair_iteration_started(iteration=1, max_iterations=2)
    iter_2_log = reporter.repair_iteration_started(iteration=2, max_iterations=2)

    assert "REPAIR ITERATION 1/2" in iter_1_log
    assert "REPAIR ITERATION 2/2" in iter_2_log
    # Task number must strictly remain TASK 10/10, never TASK 11/10 or TASK 12/10
    assert "TASK 11" not in "\n".join(captured)
    assert "TASK 12" not in "\n".join(captured)
    assert reporter.active_stage.number == 10


# ─────────────────────────────────────────────────────────────
# TEST 10: QA rounds are independent from task numbers
# ─────────────────────────────────────────────────────────────
def test_10_qa_rounds_independent_from_task_numbers():
    captured = []
    reporter = PipelineProgressReporter(log_sink=captured.append)

    qa_1 = reporter.qa_round_started(round_idx=1, pdf_version=1)
    qa_2 = reporter.qa_round_started(round_idx=2, pdf_version=2)

    assert "QA ROUND 1 (Artifact Version: PDF v1)" in qa_1
    assert "QA ROUND 2 (Artifact Version: PDF v2)" in qa_2
    # Ensure neither round label mutates task numbering
    assert "TASK 1" not in qa_1
    assert "TASK 2" not in qa_2


# ─────────────────────────────────────────────────────────────
# TEST 11: Pipeline blocked quality is not logged as system ERROR
# ─────────────────────────────────────────────────────────────
def test_11_pipeline_blocked_quality_not_system_error():
    captured = []
    reporter = PipelineProgressReporter(log_sink=captured.append)

    msg = reporter.terminal_decision(
        status=PipelineTerminalStatus.PIPELINE_BLOCKED_QUALITY,
        reason="Duplicate slide rate 15.0% >= 10.0%",
        final_qa_round=2,
        artifact_version=2,
        export_approved=False,
    )

    assert "⛔ PIPELINE BLOCKED — QUALITY GATES NOT CONVERGED" in msg
    assert "Status: PIPELINE_BLOCKED_QUALITY" in msg
    assert "Export: BLOCKED" in msg
    # Must NOT format as a generic raw system crash
    assert "❌ PIPELINE SYSTEM ERROR" not in msg


# ─────────────────────────────────────────────────────────────
# TEST 12: Final state cannot be success with unresolved critical gates
# ─────────────────────────────────────────────────────────────
def test_12_final_state_cannot_be_success_with_critical_failures():
    state = PipelineState(job_id="job_crit")
    critical_gate = GateResult(
        gate_id="gate_05",
        gate_name="Duplicate Slide Rate",
        passed=False,
        status=GateStatus.CRITICAL_FAILURE,
        severity=Severity.CRITICAL,
        repairability=Repairability.DETERMINISTIC_REPAIRABLE,
        qa_version=1,
    )
    round_1 = QualityRound(
        round_id=1,
        artifact_version=1,
        gate_results=[critical_gate],
        critical_failures=1,
        blocking_reasons=["Duplicate Slide Rate critical failure"],
        overall_score=0.60,
    )
    state.set_active_qa(round_1)
    dec = QualityDecisionEngine.evaluate(round_1, state)
    assert dec.status == ExportDecisionStatus.BLOCKED
    state.export_decision = dec

    with pytest.raises(PipelineStateSynchronizationError) as exc_info:
        state.verify_export_invariants()
    assert "critical gate failures" in str(exc_info.value)


# ─────────────────────────────────────────────────────────────
# TEST 13: Progress reporter uses registry only
# ─────────────────────────────────────────────────────────────
def test_13_progress_reporter_uses_registry_only():
    reporter = PipelineProgressReporter()
    for stage_def in PIPELINE_STAGES:
        # Every stage passed must be verified against the canonical registry
        retrieved = PipelineStageRegistry.get_stage(stage_def.number)
        assert retrieved == stage_def
        assert retrieved.key == stage_def.key
        assert retrieved.name == stage_def.name
        assert retrieved.number == stage_def.number

    # String key lookup also routes to the same object
    for stage_def in PIPELINE_STAGES:
        assert PipelineStageRegistry.get_stage(stage_def.key) == stage_def


# ─────────────────────────────────────────────────────────────
# TEST 14: All existing stages map to PipelineStage enum
# ─────────────────────────────────────────────────────────────
def test_14_all_existing_stages_map_to_enum():
    enum_keys = {e.value for e in PipelineStage}
    stage_keys = {s.key for s in PIPELINE_STAGES}
    assert enum_keys == stage_keys
    assert len(enum_keys) == 10
