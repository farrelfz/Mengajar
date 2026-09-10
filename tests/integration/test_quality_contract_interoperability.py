"""
Universal Document Intelligence System V5 — Quality Contract Interoperability Integration Test.

Phase 3A.2 Golden Benchmark:
Validates end-to-end contract interoperability across all four artifact types:
1. PRESENTATION
2. HANDOUT
3. WORKSHEET
4. SCIENTIFIC_DOCUMENT

Covers:
- Physical render inspection ingestion & normalization via QualitySignalNormalizer
- QualitySnapshot generation and aggregation
- SignalLifecycleStateMachine progression
- Multi-format ScopePolicy resolution
- RepairProposal & RepairTransaction state machine transitions
- Schema immutability and non-destructive offline execution
"""

from pathlib import Path
import pytest

from app.quality.causal import (
    CanonicalFailureCode,
    CanonicalFailureDomain,
    CanonicalSeverity,
    DetectionConfidence,
    EvidenceReference,
    EvidenceSourceType,
    FailureScope,
    QualityLocation,
    QualitySignal,
    QualitySignalLifecycleState,
    QualitySnapshot,
    QualitySignalNormalizer,
    RepairProposal,
    RepairTransaction,
    RepairTransactionStatus,
    ScopePolicy,
    SignalLifecycleStateMachine,
)
from app.quality.rendered.quality_engine import MasterRenderedQualityEngine


@pytest.fixture(scope="module")
def benchmark_pdfs():
    base_dir = Path("outputs/benchmark/phase_2c/artifacts/01_oobleck_experiment")
    return {
        "PRESENTATION": base_dir / "presentation" / "presentation.pdf",
        "HANDOUT": base_dir / "handout" / "handout.pdf",
        "WORKSHEET": base_dir / "worksheet" / "worksheet.pdf",
        "SCIENTIFIC_DOCUMENT": base_dir / "scientific" / "scientific.pdf",
    }


def test_quality_contract_interoperability_end_to_end(benchmark_pdfs):
    """End-to-end integration test validating Phase 3A.2 contracts across all 4 formats."""
    rendered_engine = MasterRenderedQualityEngine()
    snapshots = {}

    for artifact_type, pdf_path in benchmark_pdfs.items():
        if not pdf_path.exists():
            pytest.skip(f"Benchmark PDF not found: {pdf_path}")

        # 1. Ingest physical render inspection
        insp = rendered_engine.inspect(pdf_path, artifact_type=artifact_type)
        assert insp.artifact_type == artifact_type

        # 2. Normalize via QualitySignalNormalizer
        signals = QualitySignalNormalizer.from_rendered_inspection(insp, artifact_type=artifact_type)
        assert isinstance(signals, list)

        # Invariant: Each signal must be immutable and detection-only
        for sig in signals:
            assert isinstance(sig, QualitySignal)
            assert sig.failure_domain == CanonicalFailureDomain.PHYSICAL_RENDER
            assert sig.location.artifact_type == artifact_type
            assert not hasattr(sig, "cause_layer")
            assert not hasattr(sig, "repair_action")

        # 3. Create QualitySnapshot
        snap = QualitySnapshot.from_signals(
            artifact_type=artifact_type,
            signals=signals,
            metadata={"pdf_path": str(pdf_path), "page_count": insp.page_count},
        )
        assert snap.artifact_type == artifact_type
        assert snap.total_signals == len(signals)
        snapshots[artifact_type] = snap

        # Round-trip dictionary serialization
        dumped = snap.to_dict()
        reloaded = QualitySnapshot.from_dict(dumped)
        assert reloaded.snapshot_id == snap.snapshot_id
        assert reloaded.total_signals == snap.total_signals

        # 4. Scope Policy Resolution across artifact types
        policy = ScopePolicy.for_artifact(artifact_type)
        sample_pages = [1, 2] if insp.page_count >= 2 else [1]
        scope = policy.determine_scope(sample_pages, total_pages=insp.page_count)
        assert scope in (FailureScope.LOCAL, FailureScope.CLUSTER, FailureScope.SYSTEMIC, FailureScope.ARTIFACT_WIDE)

    # 5. Signal Lifecycle and Repair Transaction Workflow
    # Simulate a detected text clipping defect
    ev = EvidenceReference(
        source_type=EvidenceSourceType.PYMUPDF_GEOMETRY,
        description="Text clipping 14pt outside container",
        measurement="overflow_pt",
        measurement_unit="pt",
        raw_value=14.0,
        threshold=0.0,
        comparison_operator=">",
        page_or_slide=2,
    )
    test_sig = QualitySignal(
        source_engine="master_rendered_quality_engine",
        failure_domain=CanonicalFailureDomain.PHYSICAL_RENDER,
        failure_code=CanonicalFailureCode.TEXT_CLIPPING,
        severity=CanonicalSeverity.CRITICAL,
        location=QualityLocation(artifact_type="PRESENTATION", slide_index=2),
        evidence=(ev,),
        description="Slide 2 text clipping",
    )

    # Lifecycle State Machine progression
    rec0 = SignalLifecycleStateMachine.create_initial(signal_id=test_sig.signal_id)
    assert rec0.current_state == QualitySignalLifecycleState.RAW_DETECTION

    rec_norm = SignalLifecycleStateMachine.transition(
        rec0, QualitySignalLifecycleState.NORMALIZED, rationale="Ingested by RenderedSignalAdapter"
    )
    rec_corr = SignalLifecycleStateMachine.transition(
        rec_norm, QualitySignalLifecycleState.CORRELATED, rationale="Correlated with geometry inspector"
    )
    rec_hyp = SignalLifecycleStateMachine.transition(
        rec_corr, QualitySignalLifecycleState.CAUSAL_HYPOTHESIS, rationale="Attributed to Layout/Blueprint"
    )

    # Formulate RepairProposal
    prop = RepairProposal(
        target_signal_ids=(test_sig.signal_id,),
        target_domain=CanonicalFailureDomain.PHYSICAL_RENDER,
        target_scope=FailureScope.LOCAL,
        target_location=test_sig.location,
        repair_action_type="REDUCE_LINE_HEIGHT_AND_PADDING",
        parameters={"padding_pt": 8, "line_height": 1.15},
        expected_impact="Fit all text lines within card bounding box",
        confidence=0.91,
    )

    rec_prop = SignalLifecycleStateMachine.transition(
        rec_hyp,
        QualitySignalLifecycleState.REPAIR_PROPOSED,
        rationale="Proposed geometry repair",
        active_repair_proposal_id=prop.proposal_id,
    )
    assert rec_prop.current_state == QualitySignalLifecycleState.REPAIR_PROPOSED

    # Formulate RepairTransaction
    initial_snap = QualitySnapshot.from_signals("PRESENTATION", [test_sig])
    tx = RepairTransaction(
        proposal=prop,
        initial_snapshot=initial_snap,
    )
    assert tx.status == RepairTransactionStatus.PROPOSED

    # Advance transaction through lifecycle
    tx_auth = tx.advance_status(RepairTransactionStatus.AUTHORIZED, note="Authority granted")
    tx_snap = tx_auth.advance_status(RepairTransactionStatus.SNAPSHOT_CREATED, note="Initial snapshot pinned")
    tx_appl = tx_snap.advance_status(RepairTransactionStatus.APPLIED, note="Applied CSS adjustment")
    tx_rend = tx_appl.advance_status(RepairTransactionStatus.RENDERED, note="Re-rendered presentation PDF")

    # Post-repair snapshot confirms resolution
    post_snap = QualitySnapshot.from_signals("PRESENTATION", [])
    tx_reval = tx_rend.advance_status(
        RepairTransactionStatus.REVALIDATED,
        note="Verified no clipping on re-rendered PDF",
        post_snapshot=post_snap,
    )
    tx_accepted = tx_reval.advance_status(RepairTransactionStatus.ACCEPTED, note="Defect completely resolved")

    assert tx_accepted.status == RepairTransactionStatus.ACCEPTED
    assert tx_accepted.applied_at is not None
    assert tx_accepted.revalidated_at is not None
    assert len(tx_accepted.history) == 6

    # Complete signal lifecycle
    rec_applied = SignalLifecycleStateMachine.transition(
        rec_prop, QualitySignalLifecycleState.REPAIR_APPLIED, rationale="Applied CSS fix"
    )
    rec_reval = SignalLifecycleStateMachine.transition(
        rec_applied, QualitySignalLifecycleState.REVALIDATED, rationale="Inspection passed"
    )
    rec_resolved = SignalLifecycleStateMachine.transition(
        rec_reval, QualitySignalLifecycleState.RESOLVED, rationale="Confirmed fixed"
    )
    assert rec_resolved.current_state == QualitySignalLifecycleState.RESOLVED
    assert len(rec_resolved.state_history) == 8
