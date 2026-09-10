"""
End-to-End Review Lifecycle Benchmark across 4 Canonical Artifact Formats.

Phase 6: Validates complete lifecycle using real repository fixtures:
Production Failure -> Review Intake -> Reviewability Classification ->
Evidence Package -> Queue Routing -> Reviewer Assignment ->
Structured Decision -> Directive Safety Validation -> Repair Bridge ->
Cryptographic Ledger Provenance -> Case Resolution.
"""

import tempfile
from pathlib import Path
import pytest

from app.review import (
    DirectiveCategory,
    DirectiveType,
    EpistemicStatus,
    EvidencePackageBuilder,
    ExpertDecisionType,
    ReviewConfidence,
    ReviewDecision,
    ReviewDecisionEngine,
    ReviewDirective,
    ReviewIntakeRouter,
    ReviewObservation,
    ReviewInterpretation,
    ReviewProvenanceLedger,
    ReviewQueueRegistry,
    ReviewRepairBridge,
    ReviewState,
    ReviewTrigger,
    ReviewerCapability,
    ReviewerProfile,
    StaticReviewBundleGenerator,
)


@pytest.fixture
def lifecycle_env():
    with tempfile.TemporaryDirectory() as tmp_dir:
        base = Path(tmp_dir)
        registry = ReviewQueueRegistry(base_dir=base / "queue")
        ledger = ReviewProvenanceLedger(ledger_path=base / "provenance" / "ledger.jsonl")
        yield {"registry": registry, "ledger": ledger, "base": base}


def test_e2e_presentation_lifecycle(lifecycle_env):
    reg = lifecycle_env["registry"]
    ledger = lifecycle_env["ledger"]
    fixture_path = Path("tests/fixtures/oobleck_experiment.md")
    assert fixture_path.exists()
    content = fixture_path.read_text(encoding="utf-8")

    # 1. Production Failure -> Intake
    case = ReviewIntakeRouter.ingest_case(
        artifact_id="art_oobleck_pres",
        artifact_type="PRESENTATION",
        trigger=ReviewTrigger.CONVERGENCE_FAILURE,
        findings=[
            {
                "failure_code": "TEXT_CONTAINER_OVERFLOW",
                "message": "Slide 2 has 85 words, exceeding 60-word cognitive load bound.",
                "severity": "MAJOR",
                "finding_id": "fnd_pres_01",
            }
        ],
        hard_blockers=["BLOCKER_OVERFLOW"],
        metadata={"fixture_path": str(fixture_path), "content_length": len(content)},
    )
    reg.register_case(case)
    ledger.append_entry(case.case_id, case.artifact_id, "CASE_INTAKE", "orchestrator", new_state="OPEN")

    assert case.current_state == ReviewState.OPEN
    assert ReviewerCapability.DOCUMENT_LAYOUT in case.required_capabilities

    # 2. Evidence Package & Static Bundle
    ev_pkg = EvidencePackageBuilder.assemble(
        case_id=case.case_id,
        artifact_id=case.artifact_id,
        artifact_type=case.artifact_type,
        trigger=case.trigger,
        hard_blockers=case.metadata.get("hard_blockers", ["BLOCKER_OVERFLOW"]),
        findings=case.metadata.get("findings", []),
        render_snapshot_paths=["/tmp/pres_slide_2.png"],
        signals=[{"signal_id": "sig_geo_01", "location": (10, 10, 50, 50), "page_or_slide": 2}],
    )
    bundle_path = StaticReviewBundleGenerator.generate_bundle(case, ev_pkg, output_dir=lifecycle_env["base"] / "bundles" / case.case_id)
    assert (bundle_path / "static_review.html").exists()

    # 3. Queue Leasing to Qualified Reviewer
    reviewer = ReviewerProfile(
        reviewer_id="rev_pres_lead",
        name="Elena Visual",
        capabilities=(ReviewerCapability.DOCUMENT_LAYOUT, ReviewerCapability.VISUAL_DESIGN),
        calibration_score=0.94,
    )
    ok_lease, leased_case, _ = ok_lease, leased_case, _ = reg.lease_case(case.case_id, reviewer.reviewer_id)
    assert ok_lease
    assert leased_case.current_state == ReviewState.LEASED
    ledger.append_entry(case.case_id, case.artifact_id, "CASE_LEASED", reviewer.reviewer_id, previous_state="OPEN", new_state="LEASED")

    # 4. Structured Decision with Repair Directive (SPLIT_SLIDE)
    directive = ReviewDirective(
        directive_type=DirectiveType.SPLIT_SLIDE,
        category=DirectiveCategory.REPAIR,
        target_page_or_slide=2,
        parameters={"split_index": 2},
        rationale="Split overcrowded slide into concept beat and observation beat.",
        reviewer_id=reviewer.reviewer_id,
    )
    decision = ReviewDecision(
        case_id=case.case_id,
        reviewer_id=reviewer.reviewer_id,
        decision_type=ExpertDecisionType.CONFIRM_DEFECT,
        confidence=ReviewConfidence.HIGH,
        epistemic_status=EpistemicStatus.VERIFIED,
        rationale="Confirmed slide 2 text overflow from render; splitting slide restores progressive reveal.",
        observations=(
            ReviewObservation(
                statement="Text spills past 16:9 projection margin on slide 2.",
                page_or_slide=2,
            ),
        ),
        interpretations=(
            ReviewInterpretation(
                hypothesis="Excessive content density for single viewport.",
                affected_layer="LEVEL_R3_ARTIFACT_STRUCTURE",
            ),
        ),
        directives=(directive,),
    )

    # 5. Apply Decision
    ok_dec, decided_case, errs = ReviewDecisionEngine.apply_decision(leased_case, decision, ev_pkg)
    assert ok_dec, f"Decision failed: {errs}"
    assert decided_case.current_state == ReviewState.DIRECTIVE_PROPOSED
    reg.update_case(decided_case)
    ledger.append_entry(case.case_id, case.artifact_id, "DECISION_COMMITTED", reviewer.reviewer_id, previous_state="LEASED", new_state="DIRECTIVE_PROPOSED")

    # 6. Bridge Directive to Repair
    repair_hint = ReviewRepairBridge.translate_directive(directive, artifact_type="PRESENTATION")
    assert repair_hint.target_layer == "LEVEL_R3_ARTIFACT_STRUCTURE"
    assert len(repair_hint.validation_signature) == 64

    # 7. Complete Ledger Audit
    is_valid, count, err = ledger.verify_ledger_integrity()
    assert is_valid
    assert count == 3
    assert err is None


def test_e2e_worksheet_anti_spoiling_lifecycle(lifecycle_env):
    reg = lifecycle_env["registry"]
    ledger = lifecycle_env["ledger"]
    fixture_path = Path("tests/fixtures/oobleck_experiment.md")
    assert fixture_path.exists()

    # 1. Intake Worksheet with suspected answer leak
    case = ReviewIntakeRouter.ingest_case(
        artifact_id="art_oobleck_ws",
        artifact_type="WORKSHEET",
        trigger=ReviewTrigger.REPAIR_INVARIANT_FAILURE,
        findings=[
            {
                "failure_code": "WORKSHEET_ANSWER_LEAK",
                "message": "Activity prompt prematurely discloses non-Newtonian viscosity explanation.",
                "severity": "BLOCKING",
            }
        ],
        hard_blockers=["BLOCKER_ANSWER_LEAK"],
    )
    reg.register_case(case)
    ledger.append_entry(case.case_id, case.artifact_id, "CASE_INTAKE", "orchestrator", new_state="OPEN")

    reviewer = ReviewerProfile(
        reviewer_id="rev_ped_01",
        name="Prof. Inquiry",
        capabilities=(ReviewerCapability.PEDAGOGY, ReviewerCapability.INQUIRY_LEARNING),
        calibration_score=0.96,
    )
    ok_lease, leased_case, _ = reg.lease_case(case.case_id, reviewer.reviewer_id)

    # 2. Reviewer directs WITHHOLD_EXPLANATION
    directive = ReviewDirective(
        directive_type=DirectiveType.WITHHOLD_EXPLANATION,
        category=DirectiveCategory.PEDAGOGICAL,
        parameters={"section": "activity_1", "preserve_inquiry": True},
        rationale="Withhold explanation until reflection section to preserve inquiry arc.",
        reviewer_id=reviewer.reviewer_id,
    )
    decision = ReviewDecision(
        case_id=case.case_id,
        reviewer_id=reviewer.reviewer_id,
        decision_type=ExpertDecisionType.CONFIRM_DEFECT,
        rationale="Anti-spoiling invariant violated; explanation must be moved to conclusion.",
        directives=(directive,),
    )
    ok_dec, updated_case, errs = ReviewDecisionEngine.apply_decision(leased_case, decision)
    assert ok_dec
    assert updated_case.current_state == ReviewState.DIRECTIVE_PROPOSED

    # 3. Bridge Directive
    hint = ReviewRepairBridge.translate_directive(directive, artifact_type="WORKSHEET")
    assert hint.target_layer == "LEVEL_R4_SEMANTIC_TRANSFORMATION"


def test_e2e_scientific_document_citation_lifecycle(lifecycle_env):
    reg = lifecycle_env["registry"]
    ledger = lifecycle_env["ledger"]
    fixture_path = Path("tests/fixtures/kti_bab1.md")
    assert fixture_path.exists()

    # 1. Scientific paper with ungrounded claim
    case = ReviewIntakeRouter.ingest_case(
        artifact_id="art_kti_01",
        artifact_type="SCIENTIFIC_DOCUMENT",
        trigger=ReviewTrigger.BENCHMARK_REGRESSION,
        findings=[
            {
                "failure_code": "UNSUPPORTED_SCIENTIFIC_CLAIM",
                "message": "Claim in section 1.2 has no citation DOI or source manifest backing.",
                "severity": "BLOCKING",
            }
        ],
        hard_blockers=["BLOCKER_CITATION"],
    )
    reg.register_case(case)

    reviewer = ReviewerProfile(
        reviewer_id="rev_sci_01",
        name="Dr. Citation",
        capabilities=(ReviewerCapability.SCIENTIFIC_WRITING, ReviewerCapability.CITATION_FORENSICS),
        calibration_score=0.98,
    )
    ok_lease, leased_case, _ = reg.lease_case(case.case_id, reviewer.reviewer_id)

    # 2. Reviewer requests citation backing (EVIDENCE directive)
    directive = ReviewDirective(
        directive_type=DirectiveType.REQUEST_CITATION_BACKING,
        category=DirectiveCategory.EVIDENCE,
        parameters={"claim_id": "claim_sec1_2"},
        rationale="Demanding verifiable primary literature citation or DOI for claim.",
        reviewer_id=reviewer.reviewer_id,
    )
    decision = ReviewDecision(
        case_id=case.case_id,
        reviewer_id=reviewer.reviewer_id,
        decision_type=ExpertDecisionType.CONFIRM_DEFECT,
        rationale="Claim requires primary source grounding before scientific export clearance.",
        directives=(directive,),
    )
    ok_dec, updated_case, _ = ReviewDecisionEngine.apply_decision(leased_case, decision)
    assert ok_dec

    hint = ReviewRepairBridge.translate_directive(directive, artifact_type="SCIENTIFIC_DOCUMENT")
    assert hint.target_layer == "LEVEL_R5_SOURCE_INTELLIGENCE"


def test_e2e_handout_density_rebalance_lifecycle(lifecycle_env):
    reg = lifecycle_env["registry"]
    ledger = lifecycle_env["ledger"]
    fixture_path = Path("tests/fixtures/hand_fire_full.md")
    assert fixture_path.exists()

    # 1. Handout with density imbalance
    case = ReviewIntakeRouter.ingest_case(
        artifact_id="art_handout_01",
        artifact_type="HANDOUT",
        trigger=ReviewTrigger.QUALITY_MANUAL_REVIEW,
        findings=[
            {
                "failure_code": "DENSITY_IMBALANCE",
                "message": "Section 2 exceeds 0.85 scannability density target.",
                "severity": "MAJOR",
            }
        ],
    )
    reg.register_case(case)

    reviewer = ReviewerProfile(
        reviewer_id="rev_hand_01",
        name="Sarah Editorial",
        capabilities=(ReviewerCapability.PEDAGOGY, ReviewerCapability.DOCUMENT_LAYOUT),
        calibration_score=0.91,
    )
    ok_lease, leased_case, _ = reg.lease_case(case.case_id, reviewer.reviewer_id)

    # 2. Directive: REDUCE_COGNITIVE_LOAD
    directive = ReviewDirective(
        directive_type=DirectiveType.REDUCE_COGNITIVE_LOAD,
        category=DirectiveCategory.PEDAGOGICAL,
        parameters={"target_section": "section_2", "scannability_target": 0.70},
        rationale="Reduce dense paragraphs into bulleted takeaway summary.",
        reviewer_id=reviewer.reviewer_id,
    )
    decision = ReviewDecision(
        case_id=case.case_id,
        reviewer_id=reviewer.reviewer_id,
        decision_type=ExpertDecisionType.CONFIRM_DEFECT,
        rationale="Scannability compromised in dense explanatory block; needs restructuring.",
        directives=(directive,),
    )
    ok_dec, updated_case, _ = ReviewDecisionEngine.apply_decision(leased_case, decision)
    assert ok_dec

    hint = ReviewRepairBridge.translate_directive(directive, artifact_type="HANDOUT")
    assert hint.target_layer == "LEVEL_R3_ARTIFACT_STRUCTURE"
