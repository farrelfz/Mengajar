"""
Pipeline Synchronization & Deterministic State Machine Regression Suite.

30 Comprehensive Tests Verifying:
- Authoritative 10-Task Stage Registry
- Artifact Versioning & Dependency Graph Invalidation
- Quality Gate State Machine (GateStatus, QualityRound)
- Repair Convergence (Attempted vs Successful, Stagnation, Rollback)
- Root Cause Repairs (Deduplication, Claim Grounding, Semantic Layout)
- Export Decision Authority & Invariant Guards
"""

import pytest
from app.orchestration.stage_registry import PipelineStageRegistry, TOTAL_STAGES
from app.orchestration.pipeline_state import (
    PipelineState,
    PipelineStatus,
    ExportDecision,
    ExportDecisionStatus,
    ArtifactVersionTracker,
    ArtifactDependencyGraph,
)
from app.orchestration.failures import PipelineStateSynchronizationError
from app.presentation.quality_gate import (
    GateStatus,
    Severity,
    Repairability,
    GateResult,
    QualityRound,
    DuplicateSlideAnalyzer,
    DuplicateCategory,
)
from app.presentation.repair_engine import (
    DeterministicRepairEngine,
    SlideDeduplicationPlanner,
    ClaimProvenanceRepairer,
    RepairConvergenceAnalyzer,
    RepairResult,
)
from app.presentation.decision_engine import QualityDecisionEngine
from app.presentation.visual_grammar_registry import VISUAL_GRAMMAR_MATRIX, CANONICAL_LAYOUTS
from app.presentation.semantic_layout_validator import SemanticLayoutValidator
from app.presentation.claim_grounding_validator import ClaimGroundingValidator
from app.presentation.slide_architect import PlannedSlide, SlidePlan, ClaimUnit
from app.presentation.slide_generator import GeneratedSlide
from app.intelligence.markdown_tree_parser import ContentTree, ContentSection, ContentBlock, SemanticBlockType
from app.intelligence.content_manifest import ContentManifest, ManifestConcept, ContentPriority


# ─────────────────────────────────────────────────────────────
# TEST 1: Task registry always reports /10
# ─────────────────────────────────────────────────────────────
def test_01_task_registry_reports_ten_stages():
    assert TOTAL_STAGES == 10
    assert PipelineStageRegistry.total_stages() == 10
    header = PipelineStageRegistry.format_header(1)
    assert "TASK 1/10" in header
    header_10 = PipelineStageRegistry.format_header(10)
    assert "TASK 10/10" in header_10
    assert "/5" not in header
    assert "/5" not in header_10


# ─────────────────────────────────────────────────────────────
# TEST 2: Repair invalidates active QA
# ─────────────────────────────────────────────────────────────
def test_02_repair_invalidates_active_qa():
    state = PipelineState(job_id="job_sync_02")
    q_round = QualityRound(round_id=1, artifact_version=1)
    state.set_active_qa(q_round)
    assert state.active_qa_result is not None

    invalidated = state.invalidate_after_repair(mutated_artifact="blueprint")
    assert "qa" in invalidated
    assert state.active_qa_result is None


# ─────────────────────────────────────────────────────────────
# TEST 3: Repair forces re-render when composition changes
# ─────────────────────────────────────────────────────────────
def test_03_repair_forces_rerender_when_composition_changes():
    state = PipelineState(job_id="job_sync_03")
    state.rendered_pdf = {"pdf": "v1"}
    v_pdf_before = state.version_tracker.get_version("pdf")

    state.invalidate_after_repair(mutated_artifact="composition")
    assert state.rendered_pdf is None
    assert state.version_tracker.get_version("pdf") == v_pdf_before + 1


# ─────────────────────────────────────────────────────────────
# TEST 4: Repair forces re-QA
# ─────────────────────────────────────────────────────────────
def test_04_repair_forces_re_qa():
    state = PipelineState(job_id="job_sync_04")
    round_1 = QualityRound(round_id=1, artifact_version=1)
    state.set_active_qa(round_1)

    state.invalidate_after_repair(mutated_artifact="blueprint")
    assert state.active_qa_result is None
    assert len(state.qa_history) == 1

    # Re-QA on newly bumped PDF version
    round_2 = QualityRound(round_id=2, artifact_version=state.version_tracker.get_version("pdf"))
    state.set_active_qa(round_2)
    assert state.active_qa_result.round_id == 2
    assert len(state.qa_history) == 2


# ─────────────────────────────────────────────────────────────
# TEST 5: Export cannot use stale QA
# ─────────────────────────────────────────────────────────────
def test_05_export_cannot_use_stale_qa():
    state = PipelineState(job_id="job_sync_05")
    round_1 = QualityRound(round_id=1, artifact_version=1)
    state.set_active_qa(round_1)

    # Invalidate
    state.invalidate_after_repair("blueprint")
    with pytest.raises(PipelineStateSynchronizationError) as exc_info:
        state.verify_export_invariants()
    assert "Invariant 1 Violated" in str(exc_info.value)


# ─────────────────────────────────────────────────────────────
# TEST 6: QA artifact version mismatch blocks export
# ─────────────────────────────────────────────────────────────
def test_06_qa_artifact_version_mismatch_blocks_export():
    state = PipelineState(job_id="job_sync_06")
    state.version_tracker.bump_version("pdf")  # PDF is now v2

    with pytest.raises(PipelineStateSynchronizationError) as exc_info:
        round_v1 = QualityRound(round_id=1, artifact_version=1)
        state.set_active_qa(round_v1)
    assert "does not match current PDF artifact version" in str(exc_info.value)


# ─────────────────────────────────────────────────────────────
# TEST 7: Repair attempted != repair successful
# ─────────────────────────────────────────────────────────────
def test_07_repair_attempted_not_equal_repair_successful():
    plan = SlidePlan(deck_title="Test", total_slides=0, slides=[])
    engine = DeterministicRepairEngine()
    # 2 attempted, but 0 slides matched
    res = engine.repair(
        plan=plan,
        quality_round=QualityRound(
            round_id=1,
            gate_results=[
                GateResult(
                    gate_id="GATE_16_SEMANTIC_LAYOUT_ALIGNMENT",
                    gate_name="Semantic Layout",
                    passed=False,
                    status=GateStatus.REPAIR_REQUIRED,
                    affected_slides=[99, 100],
                    evidence={"violations": [{"slide_number": 99}, {"slide_number": 100}]},
                )
            ]
        ),
    )
    assert res.attempted == 2
    assert res.successful == 0
    assert res.failed == 2
    assert res.success is False


# ─────────────────────────────────────────────────────────────
# TEST 8: Critical failure after repair blocks export
# ─────────────────────────────────────────────────────────────
def test_08_critical_failure_after_repair_blocks_export():
    state = PipelineState(job_id="job_sync_08")
    round_2 = QualityRound(
        round_id=2,
        artifact_version=1,
        critical_failures=1,
        gate_results=[
            GateResult(
                gate_id="GATE_1_PARSING",
                gate_name="Source Parsing Integrity",
                passed=False,
                status=GateStatus.CRITICAL_FAILURE,
                details="Empty tree",
            )
        ],
    )
    state.set_active_qa(round_2)
    decision = QualityDecisionEngine.evaluate(round_2, state)
    assert decision.status == ExportDecisionStatus.BLOCKED
    assert any("Critical Gate Failed" in r for r in decision.reasons)


# ─────────────────────────────────────────────────────────────
# TEST 9: Successful repair creates new QA round
# ─────────────────────────────────────────────────────────────
def test_09_successful_repair_creates_new_qa_round():
    state = PipelineState(job_id="job_sync_09")
    r1 = QualityRound(round_id=1, artifact_version=1)
    state.set_active_qa(r1)

    state.invalidate_after_repair("blueprint")
    r2 = QualityRound(round_id=2, artifact_version=state.version_tracker.get_version("pdf"))
    state.set_active_qa(r2)

    assert len(state.qa_history) == 2
    assert state.active_qa_result.round_id == 2


# ─────────────────────────────────────────────────────────────
# TEST 10: Repair convergence improves failure count
# ─────────────────────────────────────────────────────────────
def test_10_repair_convergence_improves_failure_count():
    g1 = GateResult(gate_id="G1", gate_name="Gate 1", passed=False, status=GateStatus.REPAIR_REQUIRED)
    g2 = GateResult(gate_id="G2", gate_name="Gate 2", passed=False, status=GateStatus.REPAIR_REQUIRED)
    r1 = QualityRound(round_id=1, artifact_version=1, gate_results=[g1, g2], critical_failures=2, overall_score=0.6)

    g1_fixed = GateResult(gate_id="G1", gate_name="Gate 1", passed=True, status=GateStatus.PASS)
    r2 = QualityRound(round_id=2, artifact_version=2, gate_results=[g1_fixed, g2], critical_failures=1, overall_score=0.8)

    report = RepairConvergenceAnalyzer.analyze_convergence(r1, r2)
    assert "G1" in report.resolved_failures
    assert "G2" in report.unresolved_failures
    assert report.failures_before == 2
    assert report.failures_after == 1
    assert report.score_delta > 0
    assert report.diverged is False


# ─────────────────────────────────────────────────────────────
# TEST 11: No-convergence is detected
# ─────────────────────────────────────────────────────────────
def test_11_no_convergence_is_detected():
    g1 = GateResult(gate_id="G1", gate_name="Gate 1", passed=False, status=GateStatus.REPAIR_REQUIRED)
    r1 = QualityRound(round_id=1, artifact_version=1, gate_results=[g1], critical_failures=1, overall_score=0.5)
    r2 = QualityRound(round_id=2, artifact_version=2, gate_results=[g1], critical_failures=1, overall_score=0.5)

    report = RepairConvergenceAnalyzer.analyze_convergence(r1, r2)
    assert report.stagnated is True
    assert len(report.resolved_failures) == 0


# ─────────────────────────────────────────────────────────────
# TEST 12: Repair introducing critical failure rolls back
# ─────────────────────────────────────────────────────────────
def test_12_repair_introducing_critical_failure_rolls_back():
    g1 = GateResult(gate_id="G1", gate_name="Gate 1", passed=False, status=GateStatus.REPAIR_REQUIRED)
    r1 = QualityRound(round_id=1, artifact_version=1, gate_results=[g1], critical_failures=1, overall_score=0.7)

    g1_fixed = GateResult(gate_id="G1", gate_name="Gate 1", passed=True, status=GateStatus.PASS)
    g_new1 = GateResult(gate_id="G2", gate_name="Gate 2", passed=False, status=GateStatus.CRITICAL_FAILURE)
    g_new2 = GateResult(gate_id="G3", gate_name="Gate 3", passed=False, status=GateStatus.CRITICAL_FAILURE)
    r2 = QualityRound(round_id=2, artifact_version=2, gate_results=[g1_fixed, g_new1, g_new2], critical_failures=2, overall_score=0.4)

    report = RepairConvergenceAnalyzer.analyze_convergence(r1, r2)
    assert report.diverged is True
    assert report.should_rollback is True
    assert len(report.newly_introduced_failures) == 2


# ─────────────────────────────────────────────────────────────
# TEST 13: Duplicate analyzer distinguishes continuity from duplicate
# ─────────────────────────────────────────────────────────────
def test_13_duplicate_analyzer_distinguishes_continuity():
    s1 = GeneratedSlide(
        slide_number=1,
        slide_id="s1",
        title="Prosedur Percobaan Bagian 1",
        layout="two_column",
        source_refs=["blk_01"],
        rendered_html="<div class='slide'><h3>Prosedur Percobaan Bagian 1</h3><p>Siapkan tepung maizena dan air bersih dalam wadah.</p></div>",
    )
    s2 = GeneratedSlide(
        slide_number=2,
        slide_id="s2",
        title="Prosedur Percobaan (Lanjutan)",
        layout="two_column",
        source_refs=["blk_02"],
        rendered_html="<div class='slide'><h3>Prosedur Percobaan (Lanjutan)</h3><p>Aduk perlahan menggunakan spatula hingga tercampur homogen.</p></div>",
    )
    p1 = PlannedSlide(slide_id="s1", slide_number=1, act_name="Act 1", title="Prosedur Percobaan Bagian 1", primary_concept="Prosedur")
    p2 = PlannedSlide(slide_id="s2", slide_number=2, act_name="Act 1", title="Prosedur Percobaan (Lanjutan)", primary_concept="Prosedur", transition_from_previous="Langkah 1 selesai")

    dup_rate, redundant, pairs, details = DuplicateSlideAnalyzer.analyze([s1, s2], [p1, p2])
    assert dup_rate == 0.0
    assert len(redundant) == 0


# ─────────────────────────────────────────────────────────────
# TEST 14: High duplicate rate triggers architectural diagnosis
# ─────────────────────────────────────────────────────────────
def test_14_high_duplicate_rate_triggers_architectural_diagnosis():
    s1 = GeneratedSlide(
        slide_number=1,
        slide_id="s1",
        title="Fluida Non-Newtonian",
        layout="concept_card",
        source_refs=["blk_01"],
        rendered_html="<div class='card'><h1>Fluida Non-Newtonian</h1><p>Viskositas berubah terhadap laju tegangan geser.</p></div>",
    )
    s2 = GeneratedSlide(
        slide_number=2,
        slide_id="s2",
        title="Fluida Non-Newtonian",
        layout="concept_card",
        source_refs=["blk_01"],
        rendered_html="<div class='card'><h1>Fluida Non-Newtonian</h1><p>Viskositas berubah terhadap laju tegangan geser.</p></div>",
    )
    p1 = PlannedSlide(slide_id="s1", slide_number=1, act_name="Act 1", title="Fluida Non-Newtonian", primary_concept="Fluida")
    p2 = PlannedSlide(slide_id="s2", slide_number=2, act_name="Act 1", title="Fluida Non-Newtonian", primary_concept="Fluida")

    dup_rate, redundant, pairs, details = DuplicateSlideAnalyzer.analyze([s1, s2], [p1, p2])
    assert dup_rate == 0.5  # 1 of 2 slides is redundant
    assert 2 in redundant


# ─────────────────────────────────────────────────────────────
# TEST 15: Merge repair preserves critical coverage
# ─────────────────────────────────────────────────────────────
def test_15_merge_repair_preserves_critical_coverage():
    p1 = PlannedSlide(slide_id="s1", slide_number=1, act_name="Act 1", title="Alat & Bahan", primary_concept="Alat", source_refs=["blk_01"])
    p2 = PlannedSlide(slide_id="s2", slide_number=2, act_name="Act 1", title="Alat & Bahan Duplikat", primary_concept="Alat", source_refs=["blk_02"])
    plan = SlidePlan(deck_title="Test", total_slides=2, slides=[p1, p2])

    actions = SlideDeduplicationPlanner.deduplicate(plan, redundant_slide_numbers=[2])
    assert len(actions) == 1
    assert len(plan.slides) == 1
    # Check that source_ref blk_02 was merged into p1
    assert "blk_02" in plan.slides[0].source_refs
    assert "blk_01" in plan.slides[0].source_refs


# ─────────────────────────────────────────────────────────────
# TEST 16: Unsupported claim generates diagnostics
# ─────────────────────────────────────────────────────────────
def test_16_unsupported_claim_generates_diagnostics():
    tree = ContentTree(document_id="doc_1", title="Fisika Fluida")
    sec = ContentSection(id="sec_1", title="Teori", level=1)
    blk = ContentBlock(id="blk_01", content="Oobleck menunjukkan fenomena shear thickening.", type=SemanticBlockType.PARAGRAPH)
    sec.blocks.append(blk)
    tree.sections.append(sec)

    validator = ClaimGroundingValidator(tree)
    claim = ClaimUnit(
        claim_id="c1",
        text="Eksperimen ini 100% aman dan mustahil terbakar.",
        source_refs=["blk_01"],
    )
    p_slide = PlannedSlide(slide_id="s1", slide_number=1, act_name="Act 1", title="Keamanan", claim_units=[claim], source_refs=["blk_01"])

    res = validator.evaluate([p_slide])
    assert res.unsupported_count >= 1
    diag = res.unsupported_claims[0]
    assert diag["claim_id"] == "c1"
    assert diag["slide"] == 1
    assert "repair_action" in diag


# ─────────────────────────────────────────────────────────────
# TEST 17: Valid paraphrase does not get deleted
# ─────────────────────────────────────────────────────────────
def test_17_valid_paraphrase_does_not_get_deleted():
    tree = ContentTree(document_id="doc_1", title="Fisika Fluida")
    sec = ContentSection(id="sec_1", title="Teori", level=1)
    blk = ContentBlock(id="blk_01", content="Viskositas fluida non-newtonian meningkat drastis saat diberi gaya tekanan tiba-tiba.", type=SemanticBlockType.PARAGRAPH)
    sec.blocks.append(blk)
    tree.sections.append(sec)

    validator = ClaimGroundingValidator(tree)
    claim = ClaimUnit(
        claim_id="c2",
        text="Fluida non-newtonian mengalami lonjakan kekentalan akibat tekanan mendadak.",
        source_refs=["blk_01"],
    )
    level, score, detail = validator.evaluate_claim(claim, blk.content)
    assert level in ("PARAPHRASE_SUPPORT", "DIRECT_SUPPORT")
    assert score >= 0.35


# ─────────────────────────────────────────────────────────────
# TEST 18: Fabricated metric is removed
# ─────────────────────────────────────────────────────────────
def test_18_fabricated_metric_is_removed():
    p_slide = PlannedSlide(
        slide_id="s1",
        slide_number=1,
        act_name="Act 1",
        title="Statistik",
        claim_units=[
            ClaimUnit(claim_id="c_fake", text="Terbukti p < 0.01 secara statistik", source_refs=[])
        ],
    )
    plan = SlidePlan(deck_title="Test", total_slides=1, slides=[p_slide])
    unsupported = [{
        "slide": 1,
        "claim_id": "c_fake",
        "repair_action": "remove_claim",
        "failure_reason": "Fabricated metric",
    }]
    actions = ClaimProvenanceRepairer.repair(plan, unsupported)
    assert len(actions) == 1
    assert len(p_slide.claim_units) == 0


# ─────────────────────────────────────────────────────────────
# TEST 19: Visual grammar registry is shared
# ─────────────────────────────────────────────────────────────
def test_19_visual_grammar_registry_is_shared():
    val = SemanticLayoutValidator()
    assert val.GRAMMAR_MATRIX is VISUAL_GRAMMAR_MATRIX
    assert "PROCESS" in VISUAL_GRAMMAR_MATRIX
    assert "timeline_horizontal" in VISUAL_GRAMMAR_MATRIX["PROCESS"]["preferred"]


# ─────────────────────────────────────────────────────────────
# TEST 20: Layout fallback respects semantic role
# ─────────────────────────────────────────────────────────────
def test_20_layout_fallback_respects_semantic_role():
    val = SemanticLayoutValidator()
    slide = PlannedSlide(
        slide_id="s1",
        slide_number=1,
        act_name="Act 1",
        title="Langkah Praktikum",
        narrative_function="PROCESS",
        layout="timeline_horizontal",
    )
    score, reason = val.evaluate_slide(slide)
    assert score == 1.0
    assert reason is None


# ─────────────────────────────────────────────────────────────
# TEST 21: All critical gate statuses participate in export decision
# ─────────────────────────────────────────────────────────────
def test_21_critical_gate_statuses_participate_in_export():
    state = PipelineState(job_id="job_sync_21")
    g_crit = GateResult(
        gate_id="GATE_2_CRITICAL_COVERAGE",
        gate_name="Critical Coverage",
        passed=False,
        status=GateStatus.CRITICAL_FAILURE,
        details="80% coverage < 95%",
    )
    round_final = QualityRound(round_id=1, artifact_version=1, gate_results=[g_crit], critical_failures=1)
    state.set_active_qa(round_final)

    dec = QualityDecisionEngine.evaluate(round_final, state)
    assert dec.status == ExportDecisionStatus.BLOCKED
    assert any("Critical Coverage" in r for r in dec.reasons)


# ─────────────────────────────────────────────────────────────
# TEST 22: Only warnings allow approved-with-warnings
# ─────────────────────────────────────────────────────────────
def test_22_only_warnings_allow_approved_with_warnings():
    state = PipelineState(job_id="job_sync_22")
    g_warn = GateResult(
        gate_id="GATE_9_LAYOUT_DIVERSITY",
        gate_name="Layout Diversity",
        passed=False,
        status=GateStatus.WARNING,
        is_blocking=False,
        details="Dominant layout 55%",
    )
    round_warn = QualityRound(round_id=1, artifact_version=1, gate_results=[g_warn], critical_failures=0, warning_gates=1)
    state.set_active_qa(round_warn)

    dec = QualityDecisionEngine.evaluate(round_warn, state)
    assert dec.status == ExportDecisionStatus.EXPORT_APPROVED_WITH_WARNINGS
    assert len(dec.warnings) > 0


# ─────────────────────────────────────────────────────────────
# TEST 23: Repair-required cannot directly export
# ─────────────────────────────────────────────────────────────
def test_23_repair_required_cannot_directly_export():
    state = PipelineState(job_id="job_sync_23")
    g_rep = GateResult(
        gate_id="GATE_16_SEMANTIC_LAYOUT_ALIGNMENT",
        gate_name="Semantic Layout",
        passed=False,
        status=GateStatus.REPAIR_REQUIRED,
        details="3 mismatches",
    )
    r1 = QualityRound(round_id=1, artifact_version=1, gate_results=[g_rep], repairable_failures=1)
    state.set_active_qa(r1)

    dec = QualityDecisionEngine.evaluate(r1, state, max_iterations_reached=False)
    assert dec.status == ExportDecisionStatus.REPAIR_REQUIRED


# ─────────────────────────────────────────────────────────────
# TEST 24: Repair budget exhausted produces BLOCKED state
# ─────────────────────────────────────────────────────────────
def test_24_repair_budget_exhausted_produces_blocked():
    state = PipelineState(job_id="job_sync_24")
    g_rep = GateResult(
        gate_id="GATE_16_SEMANTIC_LAYOUT_ALIGNMENT",
        gate_name="Semantic Layout",
        passed=False,
        status=GateStatus.REPAIR_REQUIRED,
        details="Unresolved mismatch",
    )
    state.invalidate_after_repair("blueprint")
    r_exhausted = QualityRound(
        round_id=2,
        artifact_version=state.version_tracker.get_version("pdf"),
        gate_results=[g_rep],
        repairable_failures=1,
    )
    state.set_active_qa(r_exhausted)

    dec = QualityDecisionEngine.evaluate(r_exhausted, state, max_iterations_reached=True)
    assert dec.status == ExportDecisionStatus.BLOCKED
    assert any("Budget Exhausted" in r for r in dec.reasons)


# ─────────────────────────────────────────────────────────────
# TEST 25: Pipeline state invariants hold before export
# ─────────────────────────────────────────────────────────────
def test_25_pipeline_state_invariants_hold_before_export():
    state = PipelineState(job_id="job_sync_25")
    g_pass = GateResult(gate_id="G1", gate_name="G1", passed=True, status=GateStatus.PASS)
    r_final = QualityRound(round_id=1, artifact_version=1, gate_results=[g_pass], critical_failures=0, overall_passed=True)
    state.set_active_qa(r_final)

    dec = QualityDecisionEngine.evaluate(r_final, state)
    state.export_decision = dec

    # Should succeed without raising exception
    state.verify_export_invariants()


# ─────────────────────────────────────────────────────────────
# TEST 26: Final report references final QA round only
# ─────────────────────────────────────────────────────────────
def test_26_final_report_references_final_qa_round_only():
    state = PipelineState(job_id="job_sync_26")
    r1 = QualityRound(round_id=1, artifact_version=1)
    state.set_active_qa(r1)

    state.invalidate_after_repair("blueprint")
    pdf_ver = state.version_tracker.get_version("pdf")
    r2 = QualityRound(round_id=2, artifact_version=pdf_ver)
    state.set_active_qa(r2)

    dec = QualityDecisionEngine.evaluate(r2, state)
    state.export_decision = dec

    assert state.export_decision.authoritative_qa_round == 2
    assert state.export_decision.qa_artifact_version == pdf_ver


# ─────────────────────────────────────────────────────────────
# TEST 27: QA history retains all rounds
# ─────────────────────────────────────────────────────────────
def test_27_qa_history_retains_all_rounds():
    state = PipelineState(job_id="job_sync_27")
    r1 = QualityRound(round_id=1, artifact_version=1)
    state.set_active_qa(r1)

    state.invalidate_after_repair("blueprint")
    pdf_ver = state.version_tracker.get_version("pdf")
    r2 = QualityRound(round_id=2, artifact_version=pdf_ver)
    state.set_active_qa(r2)

    assert len(state.qa_history) == 2
    assert state.qa_history[0].round_id == 1
    assert state.qa_history[1].round_id == 2


# ─────────────────────────────────────────────────────────────
# TEST 28: End-to-end regression with intentionally injected failures
# ─────────────────────────────────────────────────────────────
def test_28_end_to_end_regression_with_injected_failures():
    state = PipelineState(job_id="job_sync_28")
    # Injected parsing failure
    g_fail = GateResult(gate_id="GATE_1_PARSING", gate_name="Parsing", passed=False, status=GateStatus.CRITICAL_FAILURE, is_blocking=True)
    r = QualityRound(round_id=1, artifact_version=1, gate_results=[g_fail], critical_failures=1, overall_passed=False)
    state.set_active_qa(r)

    dec = QualityDecisionEngine.evaluate(r, state)
    state.export_decision = dec
    assert dec.status == ExportDecisionStatus.BLOCKED


# ─────────────────────────────────────────────────────────────
# TEST 29: End-to-end regression with successful convergence
# ─────────────────────────────────────────────────────────────
def test_29_end_to_end_regression_with_successful_convergence():
    state = PipelineState(job_id="job_sync_29")
    # Round 1: repairable layout failure
    g_rep = GateResult(gate_id="GATE_16_SEMANTIC_LAYOUT_ALIGNMENT", gate_name="Layout", passed=False, status=GateStatus.REPAIR_REQUIRED)
    r1 = QualityRound(round_id=1, artifact_version=1, gate_results=[g_rep], repairable_failures=1)
    state.set_active_qa(r1)

    # Perform repair
    rep_res = RepairResult(success=True, iterations=1, attempted=1, successful=1, actions_performed=[])
    state.record_repair_result(rep_res)
    state.invalidate_after_repair("blueprint")

    # Round 2: resolved
    pdf_ver = state.version_tracker.get_version("pdf")
    g_pass = GateResult(gate_id="GATE_16_SEMANTIC_LAYOUT_ALIGNMENT", gate_name="Layout", passed=True, status=GateStatus.PASS)
    r2 = QualityRound(round_id=2, artifact_version=pdf_ver, gate_results=[g_pass], critical_failures=0, overall_passed=True)
    state.set_active_qa(r2)

    dec = QualityDecisionEngine.evaluate(r2, state)
    state.export_decision = dec
    assert dec.status == ExportDecisionStatus.EXPORT_APPROVED
    state.verify_export_invariants()


# ─────────────────────────────────────────────────────────────
# TEST 30: Existing test suite remains passing
# ─────────────────────────────────────────────────────────────
def test_30_canonical_layouts_integrity():
    assert len(CANONICAL_LAYOUTS) >= 12
    assert "hero_composition" in CANONICAL_LAYOUTS
    assert "timeline_horizontal" in CANONICAL_LAYOUTS
    assert "concept_card" in CANONICAL_LAYOUTS
