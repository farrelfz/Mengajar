"""
Integration test suite for the Root-Cause-Aware Targeted Repair & Convergence Engine.

Validates end-to-end self-correcting repair pipelines across all 4 artifact types:
1. PRESENTATION: Density overflow split -> Re-evaluation -> Export Approval.
2. HANDOUT: Accidental page consolidation -> Re-evaluation -> Export Approval.
3. WORKSHEET: Anti-spoiling enforcement & Inquiry arc restore -> Export Approval.
4. SCIENTIFIC_DOCUMENT: Evidence remapping / Certainty downgrade -> Export Approval.
5. Non-repairable source contradiction escalation to MANUAL_REVIEW_REQUIRED.
6. Automatic rollback upon regression.
7. Provenance report generation.
"""

from app.intelligence.markdown_tree_parser import ContentBlock, SemanticBlockType
from app.intelligence.transformation.blueprints import (
    ExplanatorySection,
    HandoutBlueprint,
    LearningActivity,
    LearningActivityType,
    ScientificArgumentRole,
    ScientificArgumentUnit,
    ScientificDocumentBlueprint,
    WorksheetBlueprint,
)
from app.intelligence.transformation.intent import ArtifactType, get_default_intent
from app.presentation.slide_architect import PlannedSlide, SlidePlan
from app.quality.contracts.decisions import ExportDecision, UnifiedQualityDecision
from app.quality.contracts.findings import QualityFinding, SignalSeverity
from app.quality.repair import (
    ConvergenceState,
    RepairMutationClass,
    TargetedRepairEngine,
)


# ============================================================================
# 1. PRESENTATION END-TO-END REPAIR
# ============================================================================

def test_presentation_e2e_targeted_repair():
    slide = PlannedSlide(
        slide_id="slide-1",
        slide_number=1,
        act_name="Intro",
        title="Oobleck Viscosity Principles",
        layout="concept_card",
        key_blocks=[
            ContentBlock(id=f"b_{i}", type=SemanticBlockType.PARAGRAPH, content=f"Point {i}: shear thickening details")
            for i in range(1, 6)
        ],
        source_refs=["ku_1", "ku_2"],
    )
    initial_plan = SlidePlan(
        deck_title="Oobleck", theme="clean_slate", total_slides=1, learning_objectives=["Viscosity"], slides=[slide]
    )

    init_decision = UnifiedQualityDecision(
        decision=ExportDecision.RENDER_REPAIR_REQUIRED,
        can_export=False,
        repair_required=True,
        hard_blockers=("TEXT_OVERFLOW: Slide 1 exceeds viewport height",),
        rationale="Text overflow on slide 1.",
    )
    finding = QualityFinding(
        failure_code="TEXT_OVERFLOW",
        message="Text overflow on slide 1",
        severity=SignalSeverity.ERROR,
        affected_pages=(1,),
    )

    def mock_evaluator(mutated_bp):
        # Once split into 2 slides with <= 3 blocks, export is approved!
        if len(mutated_bp.slides) == 2:
            return (
                UnifiedQualityDecision(
                    decision=ExportDecision.EXPORT_APPROVED,
                    can_export=True,
                    repair_required=False,
                    hard_blockers=(),
                    rationale="Split resolved density without font degradation.",
                ),
                0.92,
                [],
            )
        return (init_decision, 0.70, [finding])

    engine = TargetedRepairEngine(max_iterations=3)
    repaired_bp, result, provenance = engine.execute_repair(
        blueprint=initial_plan,
        initial_decision=init_decision,
        findings=[finding],
        metrics={"occupancy": 0.93},
        artifact_type="PRESENTATION",
        evaluator_fn=mock_evaluator,
    )

    assert result.success is True
    assert result.convergence_state == ConvergenceState.CONVERGED
    assert len(repaired_bp.slides) == 2
    assert result.post_authority.can_export is True
    assert len(result.actions_applied) == 1
    assert result.actions_applied[0].mutation_class == RepairMutationClass.CLASS_B_COMPOSITION


# ============================================================================
# 2. HANDOUT END-TO-END REPAIR
# ============================================================================

def test_handout_e2e_targeted_repair():
    s1 = ExplanatorySection(section_id="s1", sequence_index=1, topic="Section 1", heading_level=1, core_unit_ids=("ku_1",), reading_depth="deep")
    s2 = ExplanatorySection(section_id="s2", sequence_index=2, topic="Trailing orphan", heading_level=2, core_unit_ids=("ku_2",), reading_depth="brief")
    initial_bp = HandoutBlueprint(
        blueprint_id="bp_h", artifact_type=ArtifactType.HANDOUT,
        source_manifest_id="sm", document_title="Handout",
        intent=get_default_intent(ArtifactType.HANDOUT), sections=(s1, s2)
    )

    init_decision = UnifiedQualityDecision(
        decision=ExportDecision.RENDER_REPAIR_REQUIRED,
        can_export=False,
        repair_required=True,
        hard_blockers=("ACCIDENTAL_PAGE: Page 2 contains < 10% content",),
        rationale="Accidental orphan page.",
    )
    finding = QualityFinding(failure_code="ACCIDENTAL_PAGE", severity=SignalSeverity.ERROR, affected_pages=(2,))

    def mock_evaluator(mutated_bp):
        if len(mutated_bp.sections) == 1:
            return (
                UnifiedQualityDecision(
                    decision=ExportDecision.EXPORT_APPROVED,
                    can_export=True,
                    repair_required=False,
                    hard_blockers=(),
                    rationale="Sections consolidated cleanly.",
                ),
                0.90,
                [],
            )
        return (init_decision, 0.68, [finding])

    engine = TargetedRepairEngine(max_iterations=3)
    repaired_bp, result, provenance = engine.execute_repair(
        blueprint=initial_bp,
        initial_decision=init_decision,
        findings=[finding],
        artifact_type="HANDOUT",
        evaluator_fn=mock_evaluator,
    )

    assert result.success is True
    assert len(repaired_bp.sections) == 1
    assert "ku_1" in repaired_bp.sections[0].core_unit_ids
    assert "ku_2" in repaired_bp.sections[0].core_unit_ids


# ============================================================================
# 3. WORKSHEET END-TO-END REPAIR
# ============================================================================

def test_worksheet_e2e_targeted_repair():
    a1 = LearningActivity(
        activity_id="a1", sequence_index=1, activity_type=LearningActivityType.PREDICTION,
        title="Prediksi", prompt_text="Prediksikan reaksi, karena partikel saling mengunci saat ditekan.",
        scaffolding_level="MEDIUM", withhold_explanation=False, expected_reasoning_type="PRED"
    )
    initial_bp = WorksheetBlueprint(
        blueprint_id="bp_w", artifact_type=ArtifactType.WORKSHEET,
        source_manifest_id="sm", document_title="LKS",
        intent=get_default_intent(ArtifactType.WORKSHEET), activities=(a1,)
    )

    init_decision = UnifiedQualityDecision(
        decision=ExportDecision.SEMANTIC_REPAIR_REQUIRED,
        can_export=False,
        repair_required=True,
        hard_blockers=("ANTI_SPOILING_BREACH: Explanation leaked before prediction",),
        rationale="Anti-spoiling breach.",
    )
    finding = QualityFinding(failure_code="ANTI_SPOILING_BREACH", severity=SignalSeverity.BLOCKING)

    def mock_evaluator(mutated_bp):
        if mutated_bp.activities[0].withhold_explanation is True:
            return (
                UnifiedQualityDecision(
                    decision=ExportDecision.EXPORT_APPROVED,
                    can_export=True,
                    repair_required=False,
                    hard_blockers=(),
                    rationale="Anti-spoiling enforced.",
                ),
                0.95,
                [],
            )
        return (init_decision, 0.65, [finding])

    engine = TargetedRepairEngine(max_iterations=3)
    repaired_bp, result, provenance = engine.execute_repair(
        blueprint=initial_bp,
        initial_decision=init_decision,
        findings=[finding],
        artifact_type="WORKSHEET",
        evaluator_fn=mock_evaluator,
    )

    assert result.success is True
    assert repaired_bp.activities[0].withhold_explanation is True
    assert "karena partikel saling mengunci" not in repaired_bp.activities[0].prompt_text


# ============================================================================
# 4. SCIENTIFIC DOCUMENT END-TO-END REPAIR
# ============================================================================

def test_scientific_document_e2e_targeted_repair():
    arg = ScientificArgumentUnit(
        argument_id="arg_1", sequence_index=1, claim_unit_id="c_1",
        argument_role=ScientificArgumentRole.BACKGROUND_CLAIM,
        claim_statement="Secara mutlak membuktikan bahwa hukum kontinuitas fluida batal.",
        supporting_evidence_unit_ids=(),
        confidence=1.0,
    )
    initial_bp = ScientificDocumentBlueprint(
        blueprint_id="bp_sci", artifact_type=ArtifactType.SCIENTIFIC_DOCUMENT,
        source_manifest_id="sm", document_title="KTI",
        intent=get_default_intent(ArtifactType.SCIENTIFIC_DOCUMENT), arguments=(arg,)
    )

    init_decision = UnifiedQualityDecision(
        decision=ExportDecision.SEMANTIC_REPAIR_REQUIRED,
        can_export=False,
        repair_required=True,
        hard_blockers=("UNSUPPORTED_SCIENTIFIC_CLAIM: Absolute claim lacks empirical citation",),
        rationale="Unsupported claim.",
    )
    finding = QualityFinding(failure_code="UNSUPPORTED_SCIENTIFIC_CLAIM", severity=SignalSeverity.ERROR, element_id="c_1")

    def mock_evaluator(mutated_bp):
        if mutated_bp.arguments[0].argument_role == ScientificArgumentRole.HYPOTHESIS:
            return (
                UnifiedQualityDecision(
                    decision=ExportDecision.EXPORT_APPROVED,
                    can_export=True,
                    repair_required=False,
                    hard_blockers=(),
                    rationale="Claim softened to hypothesis with zero fabrication.",
                ),
                0.91,
                [],
            )
        return (init_decision, 0.70, [finding])

    engine = TargetedRepairEngine(max_iterations=3)
    repaired_bp, result, provenance = engine.execute_repair(
        blueprint=initial_bp,
        initial_decision=init_decision,
        findings=[finding],
        artifact_type="SCIENTIFIC_DOCUMENT",
        evaluator_fn=mock_evaluator,
    )

    assert result.success is True
    assert repaired_bp.arguments[0].argument_role == ScientificArgumentRole.HYPOTHESIS
    repaired_arg = repaired_bp.arguments[0]
    assert len(repaired_arg.supporting_evidence_unit_ids) == 0  # Zero fabrication!


# ============================================================================
# 5. NON-REPAIRABLE SOURCE CONTRADICTION ESCALATION
# ============================================================================

def test_non_repairable_escalation():
    initial_bp = HandoutBlueprint(
        blueprint_id="bp_h", artifact_type=ArtifactType.HANDOUT,
        source_manifest_id="sm", document_title="Handout",
        intent=get_default_intent(ArtifactType.HANDOUT), sections=()
    )
    init_decision = UnifiedQualityDecision(
        decision=ExportDecision.BLOCKED,
        can_export=False,
        repair_required=True,
        hard_blockers=("SOURCE_CONTRADICTION: Mutually exclusive statements in source",),
        rationale="Source contradiction.",
    )
    finding = QualityFinding(failure_code="SOURCE_CONTRADICTION", severity=SignalSeverity.BLOCKING)

    engine = TargetedRepairEngine(max_iterations=3)
    repaired_bp, result, provenance = engine.execute_repair(
        blueprint=initial_bp,
        initial_decision=init_decision,
        findings=[finding],
        artifact_type="HANDOUT",
    )

    assert result.success is False
    assert result.convergence_state == ConvergenceState.ESCALATED
    assert result.post_authority.decision == ExportDecision.MANUAL_REVIEW_REQUIRED
    assert result.post_authority.manual_review_required is True


# ============================================================================
# 6. ROLLBACK ON REGRESSION
# ============================================================================

def test_rollback_on_introduced_hard_blocker():
    slide = PlannedSlide(
        slide_id="slide-1", slide_number=1, act_name="Intro",
        title="Title", layout="concept_card", key_blocks=[], source_refs=["ku_1"]
    )
    initial_plan = SlidePlan(
        deck_title="Deck", theme="clean_slate", total_slides=1, learning_objectives=[], slides=[slide]
    )
    init_decision = UnifiedQualityDecision(
        decision=ExportDecision.RENDER_REPAIR_REQUIRED,
        can_export=False,
        repair_required=True,
        hard_blockers=("MARGIN_VIOLATION: Breach on slide 1",),
        rationale="Margin breach.",
    )
    finding = QualityFinding(failure_code="MARGIN_VIOLATION", severity=SignalSeverity.ERROR, affected_pages=(1,))

    def hostile_evaluator(mutated_bp):
        # Hostile evaluator simulates a bad repair that introduces FONT_TOO_SMALL hard blocker
        return (
            UnifiedQualityDecision(
                decision=ExportDecision.BLOCKED,
                can_export=False,
                repair_required=True,
                hard_blockers=("FONT_TOO_SMALL: Font reduced below 10pt",),
                rationale="Bad mutation.",
            ),
            0.60,
            [],
        )

    engine = TargetedRepairEngine(max_iterations=2)
    repaired_bp, result, provenance = engine.execute_repair(
        blueprint=initial_plan,
        initial_decision=init_decision,
        findings=[finding],
        artifact_type="PRESENTATION",
        evaluator_fn=hostile_evaluator,
    )

    # Must reject and rollback
    assert result.success is False
    assert len(provenance.history) == 1
    assert provenance.history[0].authority_decision_after == "ROLLED_BACK"


# ============================================================================
# 7. PROVENANCE REPORT GENERATION
# ============================================================================

def test_provenance_markdown_and_json_reports():
    initial_bp = HandoutBlueprint(
        blueprint_id="bp_h", artifact_type=ArtifactType.HANDOUT,
        source_manifest_id="sm", document_title="Handout",
        intent=get_default_intent(ArtifactType.HANDOUT),
        sections=(
            ExplanatorySection(section_id="s1", sequence_index=1, topic="T1", heading_level=1, reading_depth="standard"),
            ExplanatorySection(section_id="s2", sequence_index=2, topic="T2", heading_level=2, reading_depth="standard"),
        )
    )
    init_decision = UnifiedQualityDecision(
        decision=ExportDecision.RENDER_REPAIR_REQUIRED,
        can_export=False,
        repair_required=True,
        hard_blockers=(),
        rationale="Orphan page.",
    )
    finding = QualityFinding(failure_code="ACCIDENTAL_PAGE", severity=SignalSeverity.ERROR, affected_pages=(2,))

    def evaluator(mutated_bp):
        return (
            UnifiedQualityDecision(
                decision=ExportDecision.EXPORT_APPROVED,
                can_export=True,
                repair_required=False,
                hard_blockers=(),
                rationale="Clean",
            ),
            0.90,
            [],
        )

    engine = TargetedRepairEngine(max_iterations=2)
    repaired_bp, result, provenance = engine.execute_repair(
        blueprint=initial_bp,
        initial_decision=init_decision,
        findings=[finding],
        artifact_type="HANDOUT",
        evaluator_fn=evaluator,
    )

    json_str = provenance.export_json()
    assert "ACCIDENTAL_PAGE" in json_str or "PAGE_BREAK" in json_str

    md_str = provenance.generate_markdown_report(
        artifact_type="HANDOUT",
        initial_decision=init_decision,
        final_decision=result.post_authority,
        convergence_state=result.convergence_state,
    )
    assert "# Repair Execution Report" in md_str
    assert "HANDOUT" in md_str
    assert "EXPORT_APPROVED" in md_str
