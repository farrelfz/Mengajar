"""
Unit tests for Phase 6.9 Blind Review, Phase 6.10 Disagreement, and Phase 6.11 Calibration.
"""

from app.review.contracts import (
    AdjudicationOutcome,
    BlindReviewMode,
    DirectiveCategory,
    DirectiveType,
    DisagreementType,
    ExpertDecisionType,
    ReviewCase,
    ReviewDecision,
    ReviewDirective,
    ReviewEvidencePackage,
    ReviewState,
    ReviewTrigger,
    ReviewerCapability,
    ReviewerProfile,
)
from app.review.evidence import EvidencePackageBuilder
from app.review.governance import (
    AdjudicationManager,
    BlindReviewPolicy,
    DisagreementAnalyzer,
    ReviewerCalibrationEngine,
)


def test_blind_review_policy():
    pkg = EvidencePackageBuilder.assemble(
        case_id="case_001",
        artifact_id="art_001",
        artifact_type="PRESENTATION",
        trigger=ReviewTrigger.QUALITY_MANUAL_REVIEW,
        quality_decision="MANUAL_REVIEW_REQUIRED",
        repair_history=[{"strategy": "split_slide", "is_committed": False}],
    )
    assert pkg.quality_decision == "MANUAL_REVIEW_REQUIRED"
    assert len(pkg.failed_strategies) == 1

    # Apply BLIND_REVIEW mode
    blind = BlindReviewPolicy.apply_mask(pkg, mode=BlindReviewMode.BLIND_REVIEW)
    assert blind.quality_decision == "MASKED_FOR_BLIND_REVIEW"
    assert len(blind.failed_strategies) == 0


def test_disagreement_analyzer_consensus():
    d1 = ReviewDecision(
        case_id="case_001",
        reviewer_id="rev_1",
        decision_type=ExpertDecisionType.CONFIRM_DEFECT,
        rationale="Element collision confirmed on slide 2 based on coordinates.",
        root_cause_assessment="OVERFLOW",
    )
    d2 = ReviewDecision(
        case_id="case_001",
        reviewer_id="rev_2",
        decision_type=ExpertDecisionType.CONFIRM_DEFECT,
        rationale="Also confirmed bounding collision on slide 2.",
        root_cause_assessment="OVERFLOW",
    )

    report = DisagreementAnalyzer.analyze([d1, d2])
    assert report.agreement_score == 1.0
    assert report.adjudication_outcome == AdjudicationOutcome.CONSENSUS
    assert len(report.disagreement_types) == 0


def test_disagreement_analyzer_divergence():
    d1 = ReviewDecision(
        case_id="case_001",
        reviewer_id="rev_1",
        decision_type=ExpertDecisionType.CONFIRM_DEFECT,
        rationale="Defect is genuine overflow in text container.",
        root_cause_assessment="CONTAINER_TOO_SMALL",
    )
    d2 = ReviewDecision(
        case_id="case_001",
        reviewer_id="rev_2",
        decision_type=ExpertDecisionType.DISPUTE_FALSE_POSITIVE,
        rationale="Margin was intentional breathing room, not defect.",
        root_cause_assessment="INTENTIONAL_DESIGN",
    )

    report = DisagreementAnalyzer.analyze([d1, d2])
    assert report.agreement_score < 0.80
    assert DisagreementType.OBSERVATION_DISAGREEMENT in report.disagreement_types
    assert DisagreementType.ROOT_CAUSE_DISAGREEMENT in report.disagreement_types
    assert report.adjudication_outcome in (
        AdjudicationOutcome.SECOND_REVIEW_REQUIRED,
        AdjudicationOutcome.EXPERT_ADJUDICATION_REQUIRED,
    )


def test_disagreement_analyzer_safety_blocker_invariant():
    d1 = ReviewDecision(
        case_id="case_001",
        reviewer_id="rev_1",
        decision_type=ExpertDecisionType.CONFIRM_DEFECT,
        rationale="Both reviewers agree on the defect here.",
    )
    d2 = ReviewDecision(
        case_id="case_001",
        reviewer_id="rev_2",
        decision_type=ExpertDecisionType.CONFIRM_DEFECT,
        rationale="Both reviewers agree on the defect here.",
    )

    # Even with 100% agreement, if safety blocker is raised, adjudication is required
    report = DisagreementAnalyzer.analyze([d1, d2], has_safety_blocker=True)
    assert report.safety_blocker_raised
    assert report.adjudication_outcome == AdjudicationOutcome.EXPERT_ADJUDICATION_REQUIRED


def test_adjudication_manager():
    senior = ReviewerProfile(
        reviewer_id="senior_01",
        name="Dr. Senior",
        capabilities=(ReviewerCapability.PEDAGOGY,),
        is_senior_adjudicator=True,
        calibration_score=0.95,
    )
    uncalibrated = ReviewerProfile(
        reviewer_id="uncal_01",
        name="Junior Novice",
        capabilities=(ReviewerCapability.PEDAGOGY,),
        is_senior_adjudicator=False,
        calibration_score=0.70,
    )

    case = ReviewCase(
        artifact_id="art_001",
        artifact_type="WORKSHEET",
        artifact_digest="d" * 64,
        trigger=ReviewTrigger.QUALITY_MANUAL_REVIEW,
        current_state=ReviewState.UNDER_REVIEW,
    )

    binding_dec = ReviewDecision(
        case_id=case.case_id,
        reviewer_id=senior.reviewer_id,
        decision_type=ExpertDecisionType.CONFIRM_DEFECT,
        rationale="Senior review confirms pedagogical defect in worksheet activity.",
    )

    # Uncalibrated fails
    ok_uncal, _, msg = AdjudicationManager.adjudicate(case, uncalibrated, binding_dec)
    assert not ok_uncal
    assert "not authorized as a senior adjudicator" in msg

    # Senior succeeds
    ok_senior, updated_case, _ = AdjudicationManager.adjudicate(case, senior, binding_dec)
    assert ok_senior
    assert len(updated_case.decisions) == 1


def test_reviewer_calibration_engine():
    rev = ReviewerProfile(reviewer_id="rev_test", name="Tester", calibration_score=0.80)
    outcomes = [
        {"decision": ExpertDecisionType.CONFIRM_DEFECT, "ground_truth": ExpertDecisionType.CONFIRM_DEFECT},
        {"decision": ExpertDecisionType.CONFIRM_DEFECT, "ground_truth": ExpertDecisionType.CONFIRM_DEFECT},
        {"decision": ExpertDecisionType.DISPUTE_FALSE_POSITIVE, "ground_truth": ExpertDecisionType.CONFIRM_DEFECT},  # Leniency
        {"decision": ExpertDecisionType.CONFIRM_DEFECT, "ground_truth": ExpertDecisionType.CONFIRM_DEFECT},
    ]
    assessment = ReviewerCalibrationEngine.evaluate_reviewer(rev, outcomes)
    assert assessment.total_golden_cases == 4
    assert assessment.correct_count == 3
    assert assessment.false_negatives == 1
    assert assessment.leniency_index == 0.25
    assert assessment.accuracy == 0.75
