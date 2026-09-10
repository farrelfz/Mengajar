"""
Universal Document Intelligence System V5 — Lifecycle State Machine Tests.

Phase 3A.2 Tests 18–21:
- Test 18: Complete 10 lifecycle states representation
- Test 19: Valid lifecycle state transitions sequence
- Test 20: Illegal lifecycle transition rejection
- Test 21: Audit trail / history preservation
"""

import pytest

from app.quality.causal.lifecycle import (
    InvalidLifecycleTransitionError,
    QualitySignalLifecycleRecord,
    QualitySignalLifecycleState,
    SignalLifecycleStateMachine,
)


def test_18_complete_ten_lifecycle_states_representation():
    """Test 18: QualitySignalLifecycleState covers all 10 canonical lifecycle states."""
    expected = {
        "RAW_DETECTION",
        "NORMALIZED",
        "CORRELATED",
        "CAUSAL_HYPOTHESIS",
        "CLUSTERED",
        "REPAIR_PROPOSED",
        "REPAIR_APPLIED",
        "REVALIDATED",
        "RESOLVED",
        "UNRESOLVED",
    }
    actual = {s.value for s in QualitySignalLifecycleState}
    assert actual == expected
    assert len(QualitySignalLifecycleState) == 10


def test_19_valid_lifecycle_state_transition_sequence():
    """Test 19: Clean progression through legal lifecycle pipeline."""
    # 1. Initialize
    rec = SignalLifecycleStateMachine.create_initial(signal_id="sig_test_001")
    assert rec.current_state == QualitySignalLifecycleState.RAW_DETECTION

    # 2. RAW_DETECTION -> NORMALIZED
    rec = SignalLifecycleStateMachine.transition(
        rec, QualitySignalLifecycleState.NORMALIZED, rationale="Normalized via RenderedSignalAdapter"
    )
    assert rec.current_state == QualitySignalLifecycleState.NORMALIZED

    # 3. NORMALIZED -> CORRELATED
    rec = SignalLifecycleStateMachine.transition(
        rec, QualitySignalLifecycleState.CORRELATED, rationale="Correlated with adjacent bounding boxes"
    )
    assert rec.current_state == QualitySignalLifecycleState.CORRELATED

    # 4. CORRELATED -> CAUSAL_HYPOTHESIS
    rec = SignalLifecycleStateMachine.transition(
        rec, QualitySignalLifecycleState.CAUSAL_HYPOTHESIS, rationale="Attributed to BLUEPRINT layer"
    )
    assert rec.current_state == QualitySignalLifecycleState.CAUSAL_HYPOTHESIS

    # 5. CAUSAL_HYPOTHESIS -> REPAIR_PROPOSED
    rec = SignalLifecycleStateMachine.transition(
        rec, QualitySignalLifecycleState.REPAIR_PROPOSED, rationale="Proposed card splitting",
        active_repair_proposal_id="prop_001"
    )
    assert rec.current_state == QualitySignalLifecycleState.REPAIR_PROPOSED
    assert rec.active_repair_proposal_id == "prop_001"

    # 6. REPAIR_PROPOSED -> REPAIR_APPLIED
    rec = SignalLifecycleStateMachine.transition(
        rec, QualitySignalLifecycleState.REPAIR_APPLIED, rationale="Applied split in blueprint"
    )
    assert rec.current_state == QualitySignalLifecycleState.REPAIR_APPLIED

    # 7. REPAIR_APPLIED -> REVALIDATED
    rec = SignalLifecycleStateMachine.transition(
        rec, QualitySignalLifecycleState.REVALIDATED, rationale="Re-rendered and inspected",
        revalidation_signal_id="sig_reval_001"
    )
    assert rec.current_state == QualitySignalLifecycleState.REVALIDATED
    assert rec.revalidation_signal_id == "sig_reval_001"

    # 8. REVALIDATED -> RESOLVED
    rec = SignalLifecycleStateMachine.transition(
        rec, QualitySignalLifecycleState.RESOLVED, rationale="Verified defect absent"
    )
    assert rec.current_state == QualitySignalLifecycleState.RESOLVED


def test_20_illegal_lifecycle_transition_rejection():
    """Test 20: Direct jump from RAW_DETECTION to RESOLVED or other illegal transitions are rejected."""
    rec = SignalLifecycleStateMachine.create_initial(signal_id="sig_test_002")

    # RAW_DETECTION -> RESOLVED is ILLEGAL
    with pytest.raises(InvalidLifecycleTransitionError) as exc_info:
        SignalLifecycleStateMachine.transition(
            rec, QualitySignalLifecycleState.RESOLVED, rationale="Bypassing normalization"
        )
    assert exc_info.value.from_state == QualitySignalLifecycleState.RAW_DETECTION
    assert exc_info.value.to_state == QualitySignalLifecycleState.RESOLVED

    # RAW_DETECTION -> NORMALIZED is valid
    rec_norm = SignalLifecycleStateMachine.transition(
        rec, QualitySignalLifecycleState.NORMALIZED, rationale="Valid normalization"
    )

    # NORMALIZED -> REPAIR_APPLIED is ILLEGAL (cannot apply repair before proposing)
    with pytest.raises(InvalidLifecycleTransitionError) as exc_info2:
        SignalLifecycleStateMachine.transition(
            rec_norm, QualitySignalLifecycleState.REPAIR_APPLIED, rationale="Premature repair"
        )
    assert exc_info2.value.from_state == QualitySignalLifecycleState.NORMALIZED
    assert exc_info2.value.to_state == QualitySignalLifecycleState.REPAIR_APPLIED


def test_21_audit_trail_history_preservation():
    """Test 21: Audit trail preserves full transition history with timestamps and rationales."""
    rec0 = SignalLifecycleStateMachine.create_initial(signal_id="sig_audit_001")
    assert len(rec0.state_history) == 1
    assert rec0.state_history[0][0] == QualitySignalLifecycleState.RAW_DETECTION

    rec1 = SignalLifecycleStateMachine.transition(
        rec0, QualitySignalLifecycleState.NORMALIZED, rationale="Step 1 complete"
    )
    rec2 = SignalLifecycleStateMachine.transition(
        rec1, QualitySignalLifecycleState.CORRELATED, rationale="Step 2 complete"
    )

    # Original records remain immutable
    assert len(rec0.state_history) == 1
    assert len(rec1.state_history) == 2
    assert len(rec2.state_history) == 3

    states = [entry[0] for entry in rec2.state_history]
    rationales = [entry[2] for entry in rec2.state_history]

    assert states == [
        QualitySignalLifecycleState.RAW_DETECTION,
        QualitySignalLifecycleState.NORMALIZED,
        QualitySignalLifecycleState.CORRELATED,
    ]
    assert "Step 1 complete" in rationales
    assert "Step 2 complete" in rationales
