"""
Unit tests for Phase 6.2 Review Intake and Phase 6.3 Review Queue Intelligence.
"""

import shutil
import tempfile
import time
from pathlib import Path
import pytest

from app.review.contracts import (
    ReviewState,
    ReviewTrigger,
    ReviewabilityStatus,
    ReviewerCapability,
    ReviewerProfile,
)
from app.review.intake import ReviewIntakeRouter, ReviewabilityClassifier
from app.review.queue import (
    ExpertiseRouter,
    PriorityBand,
    ReviewPriorityModel,
    ReviewQueueRegistry,
)


def test_reviewability_classifier():
    # 1. Trivial defect -> AUTO_RESOLVABLE
    status, reason = ReviewabilityClassifier.classify(
        findings=[{"failure_code": "FONT_TOO_SMALL"}]
    )
    assert status == ReviewabilityStatus.AUTO_RESOLVABLE

    # 2. Complex defect -> EXPERT_REVIEW_REQUIRED
    status, reason = ReviewabilityClassifier.classify(
        findings=[{"failure_code": "UNSUPPORTED_SCIENTIFIC_CLAIM"}]
    )
    assert status == ReviewabilityStatus.EXPERT_REVIEW_REQUIRED

    # 3. Missing renders -> INSUFFICIENT_EVIDENCE
    status, reason = ReviewabilityClassifier.classify(
        findings=[{"failure_code": "ANY"}],
        has_render_artifacts=False,
    )
    assert status == ReviewabilityStatus.INSUFFICIENT_EVIDENCE

    # 4. System error -> SYSTEM_ERROR
    status, reason = ReviewabilityClassifier.classify(
        findings=[{"failure_code": "CORRUPTED_MANIFEST"}]
    )
    assert status == ReviewabilityStatus.SYSTEM_ERROR

    # 5. Archived artifact -> NON_REVIEWABLE
    status, reason = ReviewabilityClassifier.classify(
        findings=[],
        is_closed_or_archived=True,
    )
    assert status == ReviewabilityStatus.NON_REVIEWABLE


def test_intake_router_capability_derivation():
    # Presentation
    caps_pres = ReviewIntakeRouter.determine_capabilities("PRESENTATION", [])
    assert ReviewerCapability.DOCUMENT_LAYOUT in caps_pres
    assert ReviewerCapability.VISUAL_DESIGN in caps_pres

    # Worksheet with answer spoiling note
    caps_ws = ReviewIntakeRouter.determine_capabilities(
        "WORKSHEET", [{"message": "Potential answer spoiling in section 2"}]
    )
    assert ReviewerCapability.INQUIRY_LEARNING in caps_ws

    # Scientific with citation issue
    caps_sci = ReviewIntakeRouter.determine_capabilities(
        "SCIENTIFIC_DOCUMENT", [{"message": "Unverified citation DOI"}]
    )
    assert ReviewerCapability.SCIENTIFIC_WRITING in caps_sci
    assert ReviewerCapability.CITATION_FORENSICS in caps_sci


def test_priority_model_calculation():
    # Critical case with hard blocker
    crit = ReviewPriorityModel.calculate(
        trigger=ReviewTrigger.QUALITY_MANUAL_REVIEW,
        hard_blocker_count=2,
        is_certification_benchmark=True,
    )
    assert crit.overall_score >= 0.70
    assert crit.band in (PriorityBand.P0_CRITICAL, PriorityBand.P1_HIGH)
    assert "sev=" in crit.explanation

    # Low priority case
    low = ReviewPriorityModel.calculate(
        trigger=ReviewTrigger.UNKNOWN_ROOT_CAUSE,
        hard_blocker_count=0,
        critical_finding_count=0,
        is_certification_benchmark=False,
    )
    assert low.overall_score < 0.50
    assert low.band in (PriorityBand.P2_NORMAL, PriorityBand.P3_BACKGROUND)


def test_queue_registry_lifecycle_and_leasing():
    tmp_dir = Path(tempfile.mkdtemp())
    try:
        registry = ReviewQueueRegistry(base_dir=tmp_dir)

        # Ingest 2 cases
        case1 = ReviewIntakeRouter.ingest_case(
            artifact_id="art_001",
            artifact_type="WORKSHEET",
            trigger=ReviewTrigger.CONVERGENCE_FAILURE,
            findings=[{"failure_code": "INQUIRY_ARC_BROKEN"}],
            hard_blockers=["BLOCK_01"],
        )
        case2 = ReviewIntakeRouter.ingest_case(
            artifact_id="art_002",
            artifact_type="PRESENTATION",
            trigger=ReviewTrigger.QUALITY_MANUAL_REVIEW,
            findings=[{"failure_code": "TEXT_CONTAINER_OVERFLOW"}],
        )

        registry.register_case(case1)
        registry.register_case(case2)

        # Listing
        all_cases = registry.list_cases()
        assert len(all_cases) == 2
        # case1 has hard blocker, should have higher priority
        assert all_cases[0].case_id == case1.case_id

        # Lease case1 to reviewer_A
        ok, leased_case, msg = registry.lease_case(case1.case_id, reviewer_id="rev_A")
        assert ok
        assert leased_case.current_state == ReviewState.LEASED
        assert leased_case.assigned_reviewer_id == "rev_A"

        # Another reviewer cannot lease case1 while locked
        ok2, _, _ = registry.lease_case(case1.case_id, reviewer_id="rev_B")
        assert not ok2

        # Releasing lease returns case to OPEN
        released = registry.release_case_lease(case1.case_id, reviewer_id="rev_A")
        assert released
        refreshed = registry.get_case(case1.case_id)
        assert refreshed.current_state == ReviewState.OPEN
        assert refreshed.assigned_reviewer_id is None

        # Test index rebuild from disk
        new_registry = ReviewQueueRegistry(base_dir=tmp_dir)
        assert len(new_registry.list_cases()) == 2

    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


def test_expertise_router():
    rev_pedagogy = ReviewerProfile(
        name="Prof. John",
        capabilities=(ReviewerCapability.PEDAGOGY, ReviewerCapability.INQUIRY_LEARNING),
        max_concurrent_leases=2,
    )
    rev_layout = ReviewerProfile(
        name="Jane Designer",
        capabilities=(ReviewerCapability.DOCUMENT_LAYOUT, ReviewerCapability.VISUAL_DESIGN),
        max_concurrent_leases=2,
    )

    ws_case = ReviewIntakeRouter.ingest_case(
        artifact_id="ws_01",
        artifact_type="WORKSHEET",
        trigger=ReviewTrigger.QUALITY_MANUAL_REVIEW,
        findings=[{"message": "Inquiry reflection step missing"}],
    )

    # Prof. John is eligible for worksheet
    ok_john, _ = ExpertiseRouter.can_review_case(rev_pedagogy, ws_case)
    assert ok_john

    # Jane is NOT eligible (lacks inquiry/pedagogy)
    ok_jane, reason_jane = ExpertiseRouter.can_review_case(rev_layout, ws_case)
    assert not ok_jane
    assert "lacks required capabilities" in reason_jane
