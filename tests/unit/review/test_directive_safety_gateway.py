"""
Unit tests for Phase 6.8 Directive Safety Gateway & Authority Boundaries.
"""

import pytest

from app.review.contracts import (
    DirectiveCategory,
    DirectiveType,
    ReviewDirective,
)
from app.review.safety import (
    AuthorityBoundaryGuard,
    DirectiveSafetyValidator,
    IllegalDirectiveException,
    SovereignAuthorityBypassAttemptError,
)


def test_valid_directive_accepted():
    dir_valid = ReviewDirective(
        directive_type=DirectiveType.SPLIT_SLIDE,
        category=DirectiveCategory.REPAIR,
        parameters={"split_index": 2},
        rationale="Split overcrowded slide into two conceptual beats.",
        reviewer_id="rev_01",
    )
    result = DirectiveSafetyValidator.validate(dir_valid, artifact_type="PRESENTATION")
    assert result.is_valid
    assert result.signature is not None
    assert len(result.violations) == 0


def test_force_export_directive_blocked():
    dir_bad = ReviewDirective(
        directive_type=DirectiveType.ADJUST_TOKEN,
        category=DirectiveCategory.REPAIR,
        parameters={"token_name": "padding", "value": 10, "force_export": True},
        rationale="Force export even if blockers remain.",
        reviewer_id="rev_01",
    )
    with pytest.raises(IllegalDirectiveException) as exc_info:
        DirectiveSafetyValidator.validate(dir_bad, artifact_type="PRESENTATION")
    assert "force artifact export" in str(exc_info.value)


def test_disable_anti_spoiling_blocked():
    dir_spoil = ReviewDirective(
        directive_type=DirectiveType.REMAP_COMPONENT,
        category=DirectiveCategory.REPAIR,
        parameters={"target_container": "step_2", "reveal_answers": True},
        rationale="Provide solution directly to student.",
        reviewer_id="rev_01",
    )
    with pytest.raises(IllegalDirectiveException) as exc_info:
        DirectiveSafetyValidator.validate(dir_spoil, artifact_type="WORKSHEET")
    assert "Revealing solutions" in str(exc_info.value) or "anti-spoiling" in str(exc_info.value)


def test_worksheet_solution_text_leak_blocked():
    dir_leak = ReviewDirective(
        directive_type=DirectiveType.REMAP_COMPONENT,
        category=DirectiveCategory.REPAIR,
        parameters={"target_container": "step_2", "hint": "Kunci jawaban nomor 1 adalah 42"},
        rationale="Add hint text to container.",
        reviewer_id="rev_01",
    )
    with pytest.raises(IllegalDirectiveException) as exc_info:
        DirectiveSafetyValidator.validate(dir_leak, artifact_type="WORKSHEET")
    assert "anti-spoiling" in str(exc_info.value)


def test_citation_fabrication_blocked():
    dir_fake_cite = ReviewDirective(
        directive_type=DirectiveType.REQUEST_CITATION_BACKING,
        category=DirectiveCategory.EVIDENCE,
        parameters={"claim_id": "c1", "fabricate_citation": True},
        rationale="Generate plausible citation.",
        reviewer_id="rev_01",
    )
    with pytest.raises(IllegalDirectiveException) as exc_info:
        DirectiveSafetyValidator.validate(dir_fake_cite, artifact_type="SCIENTIFIC_DOCUMENT")
    assert "fabricating citations" in str(exc_info.value)


def test_incompatible_artifact_directive_rejected():
    # SPLIT_SLIDE is only valid for PRESENTATION, not WORKSHEET
    dir_incompat = ReviewDirective(
        directive_type=DirectiveType.SPLIT_SLIDE,
        category=DirectiveCategory.REPAIR,
        parameters={"split_index": 1},
        rationale="Split slide on a worksheet document.",
        reviewer_id="rev_01",
    )
    with pytest.raises(IllegalDirectiveException) as exc_info:
        DirectiveSafetyValidator.validate(dir_incompat, artifact_type="WORKSHEET")
    assert "incompatible with artifact format 'WORKSHEET'" in str(exc_info.value)


def test_missing_required_parameter_rejected():
    dir_missing_param = ReviewDirective(
        directive_type=DirectiveType.SPLIT_SLIDE,
        category=DirectiveCategory.REPAIR,
        parameters={},  # Missing 'split_index'
        rationale="Split slide without specifying index.",
        reviewer_id="rev_01",
    )
    with pytest.raises(IllegalDirectiveException) as exc_info:
        DirectiveSafetyValidator.validate(dir_missing_param, artifact_type="PRESENTATION")
    assert "missing required parameter 'split_index'" in str(exc_info.value)


def test_authority_boundary_guard_export_eligibility():
    # If Level-0 decision is MANUAL_REVIEW_REQUIRED, human approval cannot authorize export
    with pytest.raises(SovereignAuthorityBypassAttemptError):
        AuthorityBoundaryGuard.verify_export_eligibility(
            quality_decision="MANUAL_REVIEW_REQUIRED",
            human_approved=True,
        )

    # If Level-0 decision is EXPORT_APPROVED, export is eligible
    assert AuthorityBoundaryGuard.verify_export_eligibility(
        quality_decision="EXPORT_APPROVED",
        human_approved=True,
    )
