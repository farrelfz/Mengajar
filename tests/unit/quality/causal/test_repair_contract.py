"""
Universal Document Intelligence System V5 — Repair Proposal & Transaction Tests.

Phase 3A.2 Tests 28–32:
- Test 28: RepairProposal structure and validation
- Test 29: RepairTransaction lifecycle statuses
- Test 30: Pre-repair snapshot preservation
- Test 31: Post-repair snapshot recording and status progression
- Test 32: Rollback transaction state recording
"""

import pytest

from app.quality.causal.contracts import (
    QualityLocation,
    QualitySignal,
    QualitySnapshot,
)
from app.quality.causal.provenance import (
    EvidenceReference,
    EvidenceSourceType,
)
from app.quality.causal.repair_contract import (
    RepairProposal,
    RepairTransaction,
    RepairTransactionStatus,
)
from app.quality.causal.taxonomy import (
    CanonicalFailureCode,
    CanonicalFailureDomain,
    CanonicalSeverity,
    FailureScope,
)


@pytest.fixture
def sample_snapshot():
    ev = EvidenceReference(
        source_type=EvidenceSourceType.PYMUPDF_GEOMETRY,
        description="Text clipping 15pt",
    )
    sig = QualitySignal(
        source_engine="rendered_engine",
        failure_domain=CanonicalFailureDomain.PHYSICAL_RENDER,
        failure_code=CanonicalFailureCode.TEXT_CLIPPING,
        severity=CanonicalSeverity.MAJOR,
        location=QualityLocation(artifact_type="PRESENTATION", slide_index=3),
        evidence=(ev,),
    )
    return QualitySnapshot.from_signals(artifact_type="PRESENTATION", signals=[sig])


def test_28_repair_proposal_structure_and_validation():
    """Test 28: RepairProposal validates required targets, action types, and confidence."""
    proposal = RepairProposal(
        target_signal_ids=("sig_123",),
        target_domain=CanonicalFailureDomain.PHYSICAL_RENDER,
        target_scope=FailureScope.LOCAL,
        target_location=QualityLocation(artifact_type="PRESENTATION", slide_index=3),
        repair_action_type="SPLIT_CARD_BEAT",
        parameters={"max_words_per_card": 35},
        expected_impact="Eliminate text clipping by partitioning card",
        confidence=0.88,
    )

    assert proposal.proposal_id.startswith("prop_")
    assert proposal.confidence == 0.88
    assert proposal.repair_action_type == "SPLIT_CARD_BEAT"
    assert proposal.target_domain == CanonicalFailureDomain.PHYSICAL_RENDER


def test_29_repair_transaction_lifecycle_statuses():
    """Test 29: RepairTransactionStatus covers all 9 canonical transaction states."""
    expected = {
        "PROPOSED",
        "AUTHORIZED",
        "SNAPSHOT_CREATED",
        "APPLIED",
        "RENDERED",
        "REVALIDATED",
        "ACCEPTED",
        "ROLLED_BACK",
        "FAILED",
    }
    actual = {s.value for s in RepairTransactionStatus}
    assert actual == expected
    assert len(RepairTransactionStatus) == 9


def test_30_pre_repair_snapshot_preservation(sample_snapshot):
    """Test 30: RepairTransaction retains immutable initial snapshot."""
    proposal = RepairProposal(
        target_signal_ids=("sig_123",),
        target_domain=CanonicalFailureDomain.PHYSICAL_RENDER,
        target_scope=FailureScope.LOCAL,
        target_location=QualityLocation(artifact_type="PRESENTATION", slide_index=3),
        repair_action_type="RESIZE_BOUNDS",
        expected_impact="Fix overflow",
        confidence=0.9,
    )

    tx = RepairTransaction(
        proposal=proposal,
        initial_snapshot=sample_snapshot,
    )

    assert tx.initial_snapshot == sample_snapshot
    assert tx.initial_snapshot.total_signals == 1
    assert tx.status == RepairTransactionStatus.PROPOSED


def test_31_post_repair_snapshot_recording_and_progression(sample_snapshot):
    """Test 31: Transaction advances through states recording snapshots and timestamps."""
    proposal = RepairProposal(
        target_signal_ids=("sig_123",),
        target_domain=CanonicalFailureDomain.PHYSICAL_RENDER,
        target_scope=FailureScope.LOCAL,
        target_location=QualityLocation(artifact_type="PRESENTATION", slide_index=3),
        repair_action_type="RESIZE_BOUNDS",
        expected_impact="Fix overflow",
        confidence=0.9,
    )

    tx = RepairTransaction(
        proposal=proposal,
        initial_snapshot=sample_snapshot,
    )

    # Progression: AUTHORIZED -> APPLIED -> RENDERED -> REVALIDATED -> ACCEPTED
    tx_auth = tx.advance_status(RepairTransactionStatus.AUTHORIZED, note="Approved by authority")
    assert tx_auth.status == RepairTransactionStatus.AUTHORIZED

    tx_app = tx_auth.advance_status(RepairTransactionStatus.APPLIED, note="Applied CSS change")
    assert tx_app.applied_at is not None

    tx_rend = tx_app.advance_status(RepairTransactionStatus.RENDERED, note="Re-rendered to PDF")
    assert tx_rend.status == RepairTransactionStatus.RENDERED

    # Post-repair snapshot (0 defects)
    clean_snapshot = QualitySnapshot.from_signals(artifact_type="PRESENTATION", signals=[])
    tx_reval = tx_rend.advance_status(
        RepairTransactionStatus.REVALIDATED,
        note="Inspected new PDF",
        post_snapshot=clean_snapshot,
    )
    assert tx_reval.revalidated_at is not None
    assert tx_reval.post_repair_snapshot == clean_snapshot

    tx_acc = tx_reval.advance_status(RepairTransactionStatus.ACCEPTED, note="Zero defects remaining")
    assert tx_acc.status == RepairTransactionStatus.ACCEPTED
    assert len(tx_acc.history) == 5


def test_32_rollback_transaction_state_recording(sample_snapshot):
    """Test 32: Transaction records rollback state and rollback reason upon failure/regression."""
    proposal = RepairProposal(
        target_signal_ids=("sig_123",),
        target_domain=CanonicalFailureDomain.PHYSICAL_RENDER,
        target_scope=FailureScope.LOCAL,
        target_location=QualityLocation(artifact_type="PRESENTATION", slide_index=3),
        repair_action_type="RESIZE_BOUNDS",
        expected_impact="Fix overflow",
        confidence=0.9,
    )

    tx = RepairTransaction(
        proposal=proposal,
        initial_snapshot=sample_snapshot,
    )

    tx_applied = tx.advance_status(RepairTransactionStatus.APPLIED, note="Applied geometry repair")

    # Revalidation detects regression
    tx_rolled_back = tx_applied.advance_status(
        RepairTransactionStatus.ROLLED_BACK,
        note="Detected font collision regression on slide 4",
        rollback_reason="COLLISION_REGRESSION",
    )

    assert tx_rolled_back.status == RepairTransactionStatus.ROLLED_BACK
    assert tx_rolled_back.rollback_reason == "COLLISION_REGRESSION"
    assert "COLLISION_REGRESSION" in tx_rolled_back.rollback_reason
