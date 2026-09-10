"""
Unit tests for Phase 6.12 Review Provenance, 6.13 Repair Bridge, and 6.14 Benchmark Bridge.
"""

import json
import tempfile
from pathlib import Path
import pytest

from app.benchmarking.governance import BenchmarkLaunderingAttemptError, ChangeClassification
from app.quality.repair.mutation_contract import RepairMutationScope
from app.review.bridge import (
    BenchmarkCandidateProposal,
    BenchmarkGovernanceBridge,
    BenchmarkProposalType,
    ReviewRepairBridge,
)
from app.review.contracts import (
    DirectiveCategory,
    DirectiveType,
    ReviewDirective,
)
from app.review.provenance import ReviewProvenanceLedger
from app.review.safety import IllegalDirectiveException


def test_review_provenance_ledger_lifecycle_and_integrity():
    with tempfile.TemporaryDirectory() as tmp_dir:
        ledger_path = Path(tmp_dir) / "ledger.jsonl"
        ledger = ReviewProvenanceLedger(ledger_path=ledger_path)

        # 1. Empty ledger is valid
        is_ok, count, _ = ledger.verify_ledger_integrity()
        assert is_ok
        assert count == 0

        # 2. Append entries
        e1 = ledger.append_entry(
            case_id="case_001",
            artifact_id="art_001",
            event_type="CASE_OPENED",
            actor_id="system",
            new_state="OPEN",
        )
        assert e1.previous_hash == "0" * 64
        assert len(e1.entry_hash) == 64

        e2 = ledger.append_entry(
            case_id="case_001",
            artifact_id="art_001",
            event_type="CASE_LEASED",
            actor_id="rev_01",
            previous_state="OPEN",
            new_state="LEASED",
        )
        assert e2.previous_hash == e1.entry_hash

        # Verify integrity
        is_valid, count_verified, err = ledger.verify_ledger_integrity()
        assert is_valid
        assert count_verified == 2
        assert err is None


def test_review_provenance_ledger_tamper_detection():
    with tempfile.TemporaryDirectory() as tmp_dir:
        ledger_path = Path(tmp_dir) / "ledger.jsonl"
        ledger = ReviewProvenanceLedger(ledger_path=ledger_path)

        ledger.append_entry(case_id="c1", artifact_id="a1", event_type="E1", actor_id="act1", new_state="OPEN")
        ledger.append_entry(case_id="c1", artifact_id="a1", event_type="E2", actor_id="act1", new_state="LEASED")

        # Tamper with the file: mutate a field in entry 1
        with open(ledger_path, "r", encoding="utf-8") as fp:
            lines = fp.readlines()
        tampered_entry = json.loads(lines[0])
        tampered_entry["actor_id"] = "MALICIOUS_IMPOSTOR"
        lines[0] = json.dumps(tampered_entry) + "\n"
        with open(ledger_path, "w", encoding="utf-8") as fp:
            fp.writelines(lines)

        # Re-verify -> tampering detected
        is_valid, bad_idx, err = ledger.verify_ledger_integrity()
        assert not is_valid
        assert bad_idx == 0
        assert "Entry tampering detected" in err or "Hash chain broken" in err


def test_review_repair_bridge_translation():
    # Valid directive
    directive = ReviewDirective(
        directive_type=DirectiveType.SPLIT_SLIDE,
        category=DirectiveCategory.REPAIR,
        parameters={"split_index": 2},
        rationale="Split slide 2 into two sequential beats.",
        reviewer_id="rev_42",
    )
    hint = ReviewRepairBridge.translate_directive(directive, artifact_type="PRESENTATION")
    assert hint.target_layer == "LEVEL_R3_ARTIFACT_STRUCTURE"
    assert hint.mutation_scope == RepairMutationScope.LEVEL_4_BLUEPRINT_REGROUPING
    assert hint.parameters["split_index"] == 2
    assert len(hint.validation_signature) == 64

    # Invalid directive (wrong artifact)
    with pytest.raises(IllegalDirectiveException):
        ReviewRepairBridge.translate_directive(directive, artifact_type="WORKSHEET")


def test_benchmark_governance_bridge():
    proposal = BenchmarkCandidateProposal(
        case_id="case_101",
        artifact_id="art_reg_01",
        artifact_type="PRESENTATION",
        proposal_type=BenchmarkProposalType.NEW_GOLDEN_CASE,
        proposer_id="rev_senior_01",
        rationale="Novel presentation layout edge case with dual equations.",
        classification=ChangeClassification.CORPUS_EXPANSION,
        previous_scores={"semantic_integrity": 0.85},
        proposed_scores={"semantic_integrity": 0.88},
    )

    ok, rec, msg = BenchmarkGovernanceBridge.validate_and_submit_proposal(proposal)
    assert ok
    assert rec.change_classification == ChangeClassification.CORPUS_EXPANSION
    assert rec.new_scores["semantic_integrity"] == 0.88

    # Attempt benchmark laundering: lower baseline from 0.85 to 0.70
    bad_proposal = proposal.model_copy(
        update={"proposed_scores": {"semantic_integrity": 0.70}}
    )
    with pytest.raises(BenchmarkLaunderingAttemptError):
        BenchmarkGovernanceBridge.validate_and_submit_proposal(bad_proposal)
