"""
Unit tests for Phase 6.1 Canonical Review Contracts and ReviewStateMachine.
"""

import json
import pytest
from pydantic import ValidationError

from app.review.contracts import (
    AdjudicationOutcome,
    CaseIdentity,
    DirectiveCategory,
    DirectiveType,
    DisagreementType,
    EpistemicStatus,
    EvidenceSufficiencyLevel,
    EvidenceSufficiencyResult,
    ExpertDecisionType,
    ReviewCase,
    ReviewConfidence,
    ReviewDecision,
    ReviewDirective,
    ReviewEvidencePackage,
    ReviewObservation,
    ReviewInterpretation,
    ReviewState,
    ReviewTrigger,
    ReviewabilityStatus,
    ReviewerCapability,
    ReviewerProfile,
)
from app.review.review_state import (
    IllegalReviewStateTransitionError,
    ReviewStateMachine,
)


def test_review_state_machine_legal_flow():
    sm = ReviewStateMachine(initial_state=ReviewState.OPEN)
    assert sm.current_state == ReviewState.OPEN
    assert sm.can_transition_to(ReviewState.LEASED)

    rec1 = sm.transition(ReviewState.LEASED, actor_id="rev_01", reason="Leased for review")
    assert sm.current_state == ReviewState.LEASED
    assert rec1.from_state == ReviewState.OPEN
    assert rec1.to_state == ReviewState.LEASED

    sm.transition(ReviewState.UNDER_REVIEW, actor_id="rev_01")
    sm.transition(ReviewState.DIRECTIVE_PROPOSED, actor_id="rev_01")
    sm.transition(ReviewState.DIRECTIVE_VALIDATED, actor_id="validator")
    sm.transition(ReviewState.REPAIR_REPLAY_REQUESTED, actor_id="bridge")
    sm.transition(ReviewState.RESOLVED, actor_id="system", reason="Replay successful")
    assert sm.current_state == ReviewState.RESOLVED
    assert len(sm.history) == 7


def test_review_state_machine_illegal_transition():
    sm = ReviewStateMachine(initial_state=ReviewState.OPEN)
    # Direct jump from OPEN to RESOLVED is forbidden
    with pytest.raises(IllegalReviewStateTransitionError) as exc_info:
        sm.transition(ReviewState.RESOLVED)
    assert exc_info.value.from_state == ReviewState.OPEN
    assert exc_info.value.to_state == ReviewState.RESOLVED


def test_review_decision_immutability_and_validation():
    obs = ReviewObservation(
        statement="Title text collides with top navigation boundary",
        target_element="title_node_1",
        page_or_slide=1,
        epistemic_status=EpistemicStatus.VERIFIED,
    )
    interp = ReviewInterpretation(
        hypothesis="Font line-height token excessive for viewport height",
        affected_layer="LEVEL_R0_RENDER_TOKEN",
        epistemic_status=EpistemicStatus.LIKELY,
    )
    dir_item = ReviewDirective(
        directive_type=DirectiveType.ADJUST_TOKEN,
        category=DirectiveCategory.REPAIR,
        target_element_id="title_node_1",
        parameters={"token": "line-height", "delta": -0.2},
        rationale="Decrease line height to prevent bounding collision",
        reviewer_id="rev_42",
    )
    decision = ReviewDecision(
        case_id="rc_test_001",
        reviewer_id="rev_42",
        decision_type=ExpertDecisionType.CONFIRM_DEFECT,
        confidence=ReviewConfidence.HIGH,
        epistemic_status=EpistemicStatus.VERIFIED,
        rationale="Confirmed physical collision between title and frame based on PyMuPDF evidence.",
        observations=(obs,),
        interpretations=(interp,),
        directives=(dir_item,),
    )

    # Immutability
    with pytest.raises(ValidationError):
        decision.rationale = "New modified rationale"

    # JSON round-trip
    dumped = decision.model_dump_json()
    loaded = ReviewDecision.model_validate_json(dumped)
    assert loaded.decision_id == decision.decision_id
    assert len(loaded.observations) == 1
    assert loaded.observations[0].statement == obs.statement


def test_review_decision_rationale_min_length():
    with pytest.raises(ValidationError):
        ReviewDecision(
            case_id="rc_test_002",
            reviewer_id="rev_42",
            decision_type=ExpertDecisionType.CONFIRM_DEFECT,
            rationale="Too short",  # < 20 chars
        )


def test_reviewer_profile_capabilities():
    prof = ReviewerProfile(
        name="Dr. Alice Smith",
        capabilities=(ReviewerCapability.SCIENTIFIC_WRITING, ReviewerCapability.CITATION_FORENSICS),
        calibration_score=0.92,
        is_senior_adjudicator=True,
    )
    assert prof.has_capability(ReviewerCapability.SCIENTIFIC_WRITING)
    assert not prof.has_capability(ReviewerCapability.INQUIRY_LEARNING)
    assert prof.can_adjudicate()

    # Lower calibration disqualifies senior adjudication
    uncalibrated = prof.model_copy(update={"calibration_score": 0.75})
    assert not uncalibrated.can_adjudicate()


def test_review_case_creation_and_defaults():
    case = ReviewCase(
        artifact_id="art_phys_01",
        job_id="job_001",
        artifact_type="PRESENTATION",
        artifact_digest="a" * 64,
        trigger=ReviewTrigger.CONVERGENCE_FAILURE,
    )
    assert case.current_state == ReviewState.OPEN
    assert case.reviewability == ReviewabilityStatus.EXPERT_REVIEW_REQUIRED
    assert case.priority_score == 0.5
    assert case.artifact_id == "art_phys_01"
