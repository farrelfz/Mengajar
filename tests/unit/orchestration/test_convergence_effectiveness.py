"""
Phase 3D.1: Convergence Effectiveness & Failure Forensics Unit Tests.
25 mandatory adversarial scenarios verifying:
- Causal Defect Graph & Confidence Model
- Repair Candidate Portfolio & Pareto Dominance
- Expanded Strategies (Presentation, Worksheet, Scientific)
- Quality Vectors & Convergence Progress Vectors
- Failure Pattern Detection (TOKEN_CHURN, SCOPE_CHURN, SYMPTOM_LOOP, FALSE_PROGRESS)
- Budget Reservation Policy & Scope Escalation
- Deterministic Repair Outcome Memory & Penalties
- Convergence Failure Reporter 13 Sections
- Zero AI / Offline Determinism Invariant
"""

from pathlib import Path
import pytest
from app.intelligence.transformation.blueprints import (
    ConceptualBeat,
    LearningActivity,
    LearningActivityType,
    PresentationBlueprint,
    ScientificArgumentRole,
    ScientificArgumentUnit,
    ScientificDocumentBlueprint,
    WorksheetBlueprint,
)
from app.intelligence.transformation.intent import ArtifactType, get_default_intent
from app.orchestration.failure_reporter import ConvergenceFailureReporter
from app.orchestration.production_context import ArtifactProductionContext, ProductionState
from app.quality.contracts.authority import UnifiedQualityReport
from app.quality.contracts.decisions import ExportDecision
from app.quality.contracts.findings import QualityFinding
from app.quality.repair.causal_graph import (
    CausalDefectGraph,
    CausalEdge,
    CausalLevel,
    DefectNode,
    DeterministicConfidenceModel,
    RelationshipType,
)
from app.quality.repair.contracts import RepairTarget
from app.quality.repair.mutation_budget import MutationBudgetTracker, get_budget_for_artifact
from app.quality.repair.mutation_contract import RepairMutationScope
from app.quality.repair.outcome_registry import RepairOutcomeRegistry
from app.quality.repair.portfolio import RepairCandidatePortfolio
from app.quality.repair.root_cause import RootCauseHypothesis, RootCauseType
from app.quality.repair.strategies.presentation import (
    PresentationComponentReflowStrategy,
    PresentationLayoutRemapStrategy,
    PresentationPaddingAdjustmentStrategy,
)
from app.quality.repair.strategies.scientific import ScientificCitationLinkingStrategy
from app.quality.repair.strategies.worksheet import (
    WorksheetLayoutAlternationStrategy,
    WorksheetTypographyScaleStrategy,
)
from app.quality.repair.vector_convergence import (
    BudgetReservationPolicy,
    ConvergenceProgressVector,
    FailurePatternType,
    QualityVector,
    RepairFailurePatternDetector,
)


def make_presentation_bp(beats=()):
    return PresentationBlueprint(
        blueprint_id="test_pres_bp",
        artifact_type=ArtifactType.PRESENTATION,
        source_manifest_id="man_01",
        document_title="Test Presentation",
        intent=get_default_intent(ArtifactType.PRESENTATION),
        beats=tuple(beats),
    )


def make_worksheet_bp(activities=()):
    return WorksheetBlueprint(
        blueprint_id="test_ws_bp",
        artifact_type=ArtifactType.WORKSHEET,
        source_manifest_id="man_01",
        document_title="Test Worksheet",
        intent=get_default_intent(ArtifactType.WORKSHEET),
        activities=tuple(activities),
    )


def make_scientific_bp(arguments=()):
    return ScientificDocumentBlueprint(
        blueprint_id="test_sci_bp",
        artifact_type=ArtifactType.SCIENTIFIC_DOCUMENT,
        source_manifest_id="man_01",
        document_title="Test Scientific Document",
        intent=get_default_intent(ArtifactType.SCIENTIFIC_DOCUMENT),
        arguments=tuple(arguments),
    )


# ---------------------------------------------------------------------------
# 1. Causal Defect Graph Creation and Traversal
# ---------------------------------------------------------------------------
def test_causal_defect_graph_creation_and_topological_sort():
    graph = CausalDefectGraph()
    n0 = DefectNode(defect_id="d0", canonical_code="TEXT_COLLISION", severity="CRITICAL", artifact_type="PRESENTATION", causal_level=CausalLevel.LEVEL_0_SYMPTOM, description="Collision")
    n1 = DefectNode(defect_id="d1", canonical_code="GRID_OVERFLOW", severity="CRITICAL", artifact_type="PRESENTATION", causal_level=CausalLevel.LEVEL_1_LOCAL_CAUSE, description="Grid overflow")
    n2 = DefectNode(defect_id="d2", canonical_code="DENSE_LAYOUT", severity="WARNING", artifact_type="PRESENTATION", causal_level=CausalLevel.LEVEL_2_STRUCTURAL_CAUSE, description="Dense layout")

    graph.add_node(n0)
    graph.add_node(n1)
    graph.add_node(n2)
    graph.add_edge(CausalEdge(source_defect_id="d0", target_cause_id="d1", relationship_type=RelationshipType.CAUSES))
    graph.add_edge(CausalEdge(source_defect_id="d1", target_cause_id="d2", relationship_type=RelationshipType.CAUSES))

    causes = graph.get_causes_for("d0")
    assert len(causes) == 1
    assert causes[0].defect_id == "d1"

    ancestor = graph.find_lowest_causal_ancestor(["d0"])
    assert ancestor is not None
    assert ancestor.defect_id == "d2"


# ---------------------------------------------------------------------------
# 2. Confidence Model Deterministic Scoring and Monotonic Bounds
# ---------------------------------------------------------------------------
def test_confidence_model_deterministic_scoring():
    conf_1 = DeterministicConfidenceModel.calculate_confidence(
        measurement_evidence=0.9,
        spatial_correlation=0.9,
        cross_signal_agreement=0.9,
        historical_outcome=1.0,
        causal_specificity=0.9,
    )
    assert 0.05 <= conf_1 <= 1.0

    conf_2 = DeterministicConfidenceModel.calculate_confidence(
        measurement_evidence=0.5,
        spatial_correlation=0.5,
        cross_signal_agreement=0.5,
        historical_outcome=1.0,
        causal_specificity=0.9,
    )
    # Monotonic: lower evidence -> lower confidence
    assert conf_2 < conf_1


# ---------------------------------------------------------------------------
# 3. Causal Edge Inference
# ---------------------------------------------------------------------------
def test_causal_edge_inference():
    graph = CausalDefectGraph()
    graph.add_node(DefectNode(defect_id="A", canonical_code="A", severity="CRITICAL", artifact_type="PRESENTATION", causal_level=CausalLevel.LEVEL_3_SEMANTIC_CAUSE, description="Root"))
    graph.add_node(DefectNode(defect_id="B", canonical_code="B", severity="CRITICAL", artifact_type="PRESENTATION", causal_level=CausalLevel.LEVEL_0_SYMPTOM, description="Leaf"))
    graph.add_edge(CausalEdge(source_defect_id="B", target_cause_id="A", relationship_type=RelationshipType.AMPLIFIES))

    symptoms = graph.get_symptoms_for("A")
    assert len(symptoms) == 1
    assert symptoms[0].defect_id == "B"


# ---------------------------------------------------------------------------
# 4. Root Cause Ancestor Resolution
# ---------------------------------------------------------------------------
def test_root_cause_ancestor_resolution():
    graph = CausalDefectGraph()
    graph.add_node(DefectNode(defect_id="R", canonical_code="R", severity="CRITICAL", artifact_type="PRESENTATION", causal_level=CausalLevel.LEVEL_4_SOURCE_CAUSE, description="Root"))
    graph.add_node(DefectNode(defect_id="M", canonical_code="M", severity="CRITICAL", artifact_type="PRESENTATION", causal_level=CausalLevel.LEVEL_2_STRUCTURAL_CAUSE, description="Middle"))
    graph.add_node(DefectNode(defect_id="L", canonical_code="L", severity="CRITICAL", artifact_type="PRESENTATION", causal_level=CausalLevel.LEVEL_0_SYMPTOM, description="Leaf"))

    graph.add_edge(CausalEdge(source_defect_id="L", target_cause_id="M", relationship_type=RelationshipType.CAUSES))
    graph.add_edge(CausalEdge(source_defect_id="M", target_cause_id="R", relationship_type=RelationshipType.CAUSES))

    root = graph.find_lowest_causal_ancestor(["L"])
    assert root is not None
    assert root.defect_id == "R"


# ---------------------------------------------------------------------------
# 5. Repair Portfolio Generation across Multiple Hypotheses
# ---------------------------------------------------------------------------
def test_repair_portfolio_generation():
    budget = MutationBudgetTracker(get_budget_for_artifact("PRESENTATION"))
    target = RepairTarget(element_id="beat-1", slide_index=1, artifact_type="PRESENTATION")
    hyp1 = RootCauseHypothesis(
        cause_type=RootCauseType.GRID_GEOMETRY,
        confidence=0.85,
        affected_targets=(target,),
        rationale="Collision",
    )
    beat = ConceptualBeat(
        beat_id="beat-1",
        sequence_index=1,
        title="Beat 1",
        primary_concept_unit_id="c1",
        narrative_function="FOUNDATION",
        information_gain=0.8,
        cognitive_load_target=0.5,
        visual_priority="HIGH_DIAGRAM",
        selection_rationale="Rationale",
    )
    bp = make_presentation_bp([beat])

    strats = [PresentationComponentReflowStrategy(), PresentationPaddingAdjustmentStrategy()]
    cands = RepairCandidatePortfolio.evaluate_portfolio(
        strategies=strats,
        target=target,
        hypotheses=[hyp1],
        budget_tracker=budget,
        blueprint=bp,
        artifact_type="PRESENTATION",
    )
    assert len(cands) >= 1
    assert any(c.strategy_id == "presentation_component_reflow" for c in cands)


# ---------------------------------------------------------------------------
# 6. Cross-Defect Leverage Formula Verification
# ---------------------------------------------------------------------------
def test_cross_defect_leverage_formula():
    cov = 0.8
    gain = 0.25
    conf = 0.90
    min_score = 0.75
    risk = 0.10

    leverage = RepairCandidatePortfolio.calculate_leverage(
        cross_defect_coverage=cov,
        expected_gain=gain,
        root_cause_confidence=conf,
        minimality=min_score,
        regression_risk=risk,
    )
    expected = round((cov * gain * conf * min_score) / risk, 4)
    assert leverage == expected
    assert leverage > 0


# ---------------------------------------------------------------------------
# 7. Utility Ranking and Pareto Dominance Pruning
# ---------------------------------------------------------------------------
def test_utility_ranking_and_pareto_dominance():
    budget = MutationBudgetTracker(get_budget_for_artifact("PRESENTATION"))
    target = RepairTarget(element_id="beat-1", slide_index=1, artifact_type="PRESENTATION")
    hyp = RootCauseHypothesis(
        cause_type=RootCauseType.GRID_GEOMETRY,
        confidence=0.90,
        affected_targets=(target,),
        rationale="Collision",
    )
    beat = ConceptualBeat(
        beat_id="beat-1",
        sequence_index=1,
        title="Beat 1",
        primary_concept_unit_id="c1",
        narrative_function="FOUNDATION",
        information_gain=0.8,
        cognitive_load_target=0.5,
        visual_priority="HIGH_DIAGRAM",
        selection_rationale="Rationale",
    )
    bp = make_presentation_bp([beat])

    strats = [PresentationComponentReflowStrategy(), PresentationPaddingAdjustmentStrategy()]
    options = RepairCandidatePortfolio.evaluate_portfolio(
        strategies=strats,
        target=target,
        hypotheses=[hyp],
        budget_tracker=budget,
        blueprint=bp,
        artifact_type="PRESENTATION",
    )
    assert len(options) > 0
    if len(options) > 1:
        assert not options[0].is_pareto_dominated


# ---------------------------------------------------------------------------
# 8. Mutation Scope Boundary Enforcement (R0-R4)
# ---------------------------------------------------------------------------
def test_mutation_scope_boundary_enforcement():
    s1 = PresentationPaddingAdjustmentStrategy()
    s2 = PresentationComponentReflowStrategy()
    s3 = PresentationLayoutRemapStrategy()
    s4 = ScientificCitationLinkingStrategy()

    assert RepairCandidatePortfolio.map_strategy_to_scope(s1) == RepairMutationScope.LEVEL_1_LOCAL_TOKEN
    assert RepairCandidatePortfolio.map_strategy_to_scope(s2) == RepairMutationScope.LEVEL_2_COMPONENT_GEOMETRY
    assert RepairCandidatePortfolio.map_strategy_to_scope(s3) == RepairMutationScope.LEVEL_3_PAGE_COMPOSITION
    assert RepairCandidatePortfolio.map_strategy_to_scope(s4) == RepairMutationScope.LEVEL_4_BLUEPRINT_REGROUPING


# ---------------------------------------------------------------------------
# 9. Presentation Reflow Repair on Element Collision
# ---------------------------------------------------------------------------
def test_presentation_reflow_strategy():
    strat = PresentationComponentReflowStrategy()
    beat = ConceptualBeat(
        beat_id="beat-1",
        sequence_index=1,
        title="Formula Slide",
        primary_concept_unit_id="c1",
        narrative_function="CORE_MECHANISM",
        information_gain=0.8,
        cognitive_load_target=0.6,
        visual_priority="EQUATION_FOCUS",
        selection_rationale="Formula explainer",
    )
    bp = make_presentation_bp([beat])
    target = RepairTarget(element_id="beat-1", slide_index=1, artifact_type="PRESENTATION")
    hyp = RootCauseHypothesis(
        cause_type=RootCauseType.GRID_GEOMETRY,
        confidence=0.8,
        affected_targets=(target,),
        rationale="Collision",
    )

    assert strat.check_preconditions(bp, target, hyp) is True
    plan = strat.plan_repair(bp, target, hyp)
    mutated_bp, applied = strat.apply_repair(bp, plan)
    assert len(applied) == 1
    assert mutated_bp.beats[0].visual_priority == "CONCEPT_CARD"


# ---------------------------------------------------------------------------
# 10. Presentation Padding Strategy Preconditions
# ---------------------------------------------------------------------------
def test_presentation_padding_strategy_preconditions():
    strat = PresentationPaddingAdjustmentStrategy()
    bp_worksheet = make_worksheet_bp([])
    target = RepairTarget(element_id="w1", artifact_type="WORKSHEET")
    hyp = RootCauseHypothesis(cause_type=RootCauseType.TYPOGRAPHY, confidence=0.8, affected_targets=(target,), rationale="Text")
    
    assert strat.check_preconditions(bp_worksheet, target, hyp) is False


# ---------------------------------------------------------------------------
# 11. Presentation Layout Remap on Dense Components
# ---------------------------------------------------------------------------
def test_presentation_layout_remap_dense():
    strat = PresentationLayoutRemapStrategy()
    beat = ConceptualBeat(
        beat_id="beat-1",
        sequence_index=1,
        title="Dense Slide",
        primary_concept_unit_id="c1",
        narrative_function="CORE_MECHANISM",
        information_gain=0.9,
        cognitive_load_target=0.8,
        visual_priority="EQUATION_FOCUS",
        selection_rationale="Dense formula",
    )
    bp = make_presentation_bp([beat])
    target = RepairTarget(element_id="beat-1", slide_index=1, artifact_type="PRESENTATION")
    hyp = RootCauseHypothesis(cause_type=RootCauseType.GRID_GEOMETRY, confidence=0.8, affected_targets=(target,), rationale="Remap")

    assert strat.check_preconditions(bp, target, hyp) is True
    plan = strat.plan_repair(bp, target, hyp)
    mutated_bp, applied = strat.apply_repair(bp, plan)
    assert len(applied) == 1
    assert mutated_bp.beats[0].visual_priority == "COMPARISON_GRID"


# ---------------------------------------------------------------------------
# 12. Worksheet Typography Scaling on Small Input Text
# ---------------------------------------------------------------------------
def test_worksheet_typography_scale_strategy():
    strat = WorksheetTypographyScaleStrategy()
    act = LearningActivity(
        activity_id="a1",
        sequence_index=1,
        activity_type=LearningActivityType.INVESTIGATION,
        title="Activity",
        prompt_text="Prompt text",
        scaffolding_level="MINIMAL",
        expected_reasoning_type="GUIDED_ANALYSIS",
    )
    bp = make_worksheet_bp([act])
    target = RepairTarget(element_id="a1", artifact_type="WORKSHEET")
    hyp = RootCauseHypothesis(cause_type=RootCauseType.TYPOGRAPHY, confidence=0.85, affected_targets=(target,), rationale="Small text")

    assert strat.check_preconditions(bp, target, hyp) is True
    plan = strat.plan_repair(bp, target, hyp)
    mutated_bp, applied = strat.apply_repair(bp, plan)
    assert len(applied) == 1
    assert mutated_bp.activities[0].scaffolding_level == "DETAILED_PROMPTS"


# ---------------------------------------------------------------------------
# 13. Worksheet Layout Alternation on Repetition Streaks
# ---------------------------------------------------------------------------
def test_worksheet_layout_alternation_strategy():
    strat = WorksheetLayoutAlternationStrategy()
    act1 = LearningActivity(activity_id="a1", sequence_index=1, activity_type=LearningActivityType.QUESTION, title="A1", prompt_text="P1", scaffolding_level="MEDIUM", expected_reasoning_type="GUIDED_ANALYSIS")
    act2 = LearningActivity(activity_id="a2", sequence_index=2, activity_type=LearningActivityType.QUESTION, title="A2", prompt_text="P2", scaffolding_level="MEDIUM", expected_reasoning_type="GUIDED_ANALYSIS")
    bp = make_worksheet_bp([act1, act2])
    target = RepairTarget(element_id="w1", artifact_type="WORKSHEET")
    hyp = RootCauseHypothesis(cause_type=RootCauseType.CONTENT_DENSITY, confidence=0.9, affected_targets=(target,), rationale="Streak")

    assert strat.check_preconditions(bp, target, hyp) is True
    plan = strat.plan_repair(bp, target, hyp)
    mutated_bp, applied = strat.apply_repair(bp, plan)
    assert len(applied) == 1
    assert mutated_bp.activities[0].expected_reasoning_type != mutated_bp.activities[1].expected_reasoning_type


# ---------------------------------------------------------------------------
# 14. Scientific Citation Linking on Invisible Citation Defects
# ---------------------------------------------------------------------------
def test_scientific_citation_linking_strategy():
    strat = ScientificCitationLinkingStrategy()
    arg1 = ScientificArgumentUnit(
        argument_id="arg-1",
        sequence_index=1,
        claim_unit_id="c1",
        argument_role=ScientificArgumentRole.HYPOTHESIS,
        claim_statement="Oobleck behaves as a non-Newtonian shear-thickening fluid",
        confidence=0.95,
    )
    bp = make_scientific_bp([arg1])
    target = RepairTarget(element_id="arg-1", artifact_type="SCIENTIFIC_DOCUMENT")
    hyp = RootCauseHypothesis(cause_type=RootCauseType.EVIDENCE_MAPPING, confidence=0.9, affected_targets=(target,), rationale="Citations")

    assert strat.check_preconditions(bp, target, hyp) is True
    plan = strat.plan_repair(bp, target, hyp)
    mutated_bp, applied = strat.apply_repair(bp, plan)
    assert len(applied) == 1
    assert "[1]" in mutated_bp.arguments[0].claim_statement


# ---------------------------------------------------------------------------
# 15. QualityVector Dominance Logic Verification
# ---------------------------------------------------------------------------
def test_quality_vector_dominance():
    v1 = QualityVector(semantic_integrity=0.9, artifact_fidelity=0.9, artifact_quality=0.8, rendered_quality=0.8)
    v2 = QualityVector(semantic_integrity=0.9, artifact_fidelity=0.9, artifact_quality=0.85, rendered_quality=0.8)
    v3 = QualityVector(semantic_integrity=0.85, artifact_fidelity=0.95, artifact_quality=0.8, rendered_quality=0.8)

    assert v2.dominates(v1) is True
    assert v1.dominates(v2) is False
    assert v1.dominates(v1) is False
    assert v3.dominates(v1) is False


# ---------------------------------------------------------------------------
# 16. False Progress Detection
# ---------------------------------------------------------------------------
def test_false_progress_detection():
    v0 = ConvergenceProgressVector(
        iteration=0,
        hard_blocker_count=2,
        critical_finding_count=2,
        affected_element_count=2,
        root_cause_coverage=1.0,
        quality_vector=QualityVector(),
        overall_score=0.70,
    )
    v1 = ConvergenceProgressVector(
        iteration=1,
        hard_blocker_count=2,
        critical_finding_count=2,
        affected_element_count=2,
        root_cause_coverage=1.0,
        quality_vector=QualityVector(),
        overall_score=0.78,
    )
    pattern, rationale = RepairFailurePatternDetector.analyze_history([v0, v1])
    assert pattern == FailurePatternType.FALSE_PROGRESS
    assert "False Progress" in rationale


# ---------------------------------------------------------------------------
# 17. Token Churn Detection
# ---------------------------------------------------------------------------
def test_token_churn_detection():
    history = [
        ConvergenceProgressVector(
            iteration=i,
            hard_blocker_count=1,
            critical_finding_count=1,
            affected_element_count=1,
            root_cause_coverage=1.0,
            quality_vector=QualityVector(),
            overall_score=0.72,
            applied_scope=RepairMutationScope.LEVEL_1_LOCAL_TOKEN,
        )
        for i in range(4)
    ]
    pattern, rationale = RepairFailurePatternDetector.analyze_history(history)
    assert pattern == FailurePatternType.TOKEN_CHURN


# ---------------------------------------------------------------------------
# 18. Scope Churn Detection
# ---------------------------------------------------------------------------
def test_scope_churn_detection():
    history = [
        ConvergenceProgressVector(
            iteration=0,
            hard_blocker_count=2,
            critical_finding_count=2,
            affected_element_count=2,
            root_cause_coverage=1.0,
            quality_vector=QualityVector(),
            overall_score=0.70,
            applied_scope=RepairMutationScope.LEVEL_1_LOCAL_TOKEN,
        ),
        ConvergenceProgressVector(
            iteration=1,
            hard_blocker_count=2,
            critical_finding_count=2,
            affected_element_count=2,
            root_cause_coverage=1.0,
            quality_vector=QualityVector(),
            overall_score=0.70,
            applied_scope=RepairMutationScope.LEVEL_1_LOCAL_TOKEN,
        ),
    ]
    pattern, _ = RepairFailurePatternDetector.analyze_history(history)
    assert pattern in (FailurePatternType.SCOPE_CHURN, FailurePatternType.SYMPTOM_LOOP)


# ---------------------------------------------------------------------------
# 19. Symptom Loop Detection
# ---------------------------------------------------------------------------
def test_symptom_loop_detection():
    v0 = ConvergenceProgressVector(
        iteration=0,
        hard_blocker_count=1,
        critical_finding_count=1,
        affected_element_count=1,
        root_cause_coverage=1.0,
        quality_vector=QualityVector(),
        overall_score=0.75,
        applied_strategy_id="same_strat",
    )
    v1 = ConvergenceProgressVector(
        iteration=1,
        hard_blocker_count=1,
        critical_finding_count=1,
        affected_element_count=1,
        root_cause_coverage=1.0,
        quality_vector=QualityVector(),
        overall_score=0.75,
        applied_strategy_id="same_strat",
    )
    pattern, rationale = RepairFailurePatternDetector.analyze_history([v0, v1])
    assert pattern == FailurePatternType.SYMPTOM_LOOP
    assert "same_strat" in rationale


# ---------------------------------------------------------------------------
# 20. Budget Reservation Policy Scope Escalation
# ---------------------------------------------------------------------------
def test_budget_reservation_policy_escalation():
    scopes_iter1 = BudgetReservationPolicy.get_allowed_scopes_for_iteration(
        iteration=1, max_iterations=3, pattern=FailurePatternType.HEALTHY_PROGRESS
    )
    assert RepairMutationScope.LEVEL_1_LOCAL_TOKEN in scopes_iter1

    scopes_churn = BudgetReservationPolicy.get_allowed_scopes_for_iteration(
        iteration=2, max_iterations=3, pattern=FailurePatternType.TOKEN_CHURN
    )
    assert RepairMutationScope.LEVEL_1_LOCAL_TOKEN not in scopes_churn
    assert RepairMutationScope.LEVEL_2_COMPONENT_GEOMETRY in scopes_churn
    assert RepairMutationScope.LEVEL_3_PAGE_COMPOSITION in scopes_churn


# ---------------------------------------------------------------------------
# 21. Repair Outcome Registry Recording and Memory Retrieval
# ---------------------------------------------------------------------------
def test_repair_outcome_registry_recording_and_retrieval():
    reg = RepairOutcomeRegistry.get_instance()
    reg.clear()

    reg.record_outcome(
        artifact_type="PRESENTATION",
        defect_code="ELEMENT_COLLISION",
        root_cause_type="GRID_GEOMETRY",
        strategy_id="presentation_component_reflow",
        mutation_scope="LEVEL_2_COMPONENT_GEOMETRY",
        quality_delta=0.08,
        blocker_delta=-1,
        success=True,
    )
    mult = reg.get_strategy_multiplier("presentation_component_reflow", "ELEMENT_COLLISION", "PRESENTATION")
    assert mult >= 1.0


# ---------------------------------------------------------------------------
# 22. Strategy Penalty Application on Repeated Failures
# ---------------------------------------------------------------------------
def test_strategy_penalty_on_repeated_failure():
    reg = RepairOutcomeRegistry.get_instance()
    reg.clear()

    for _ in range(2):
        reg.record_outcome(
            artifact_type="WORKSHEET",
            defect_code="REPETITION_STREAK",
            root_cause_type="CONTENT_DENSITY",
            strategy_id="failing_strategy",
            mutation_scope="LEVEL_1_LOCAL_TOKEN",
            quality_delta=0.0,
            blocker_delta=0,
            success=False,
        )

    mult = reg.get_strategy_multiplier("failing_strategy", "REPETITION_STREAK", "WORKSHEET")
    assert mult == 0.35


# ---------------------------------------------------------------------------
# 23. Strategy Boost Application on Proven Blocker Reduction
# ---------------------------------------------------------------------------
def test_strategy_boost_on_proven_reduction():
    reg = RepairOutcomeRegistry.get_instance()
    reg.clear()

    for _ in range(2):
        reg.record_outcome(
            artifact_type="PRESENTATION",
            defect_code="ELEMENT_COLLISION",
            root_cause_type="GRID_GEOMETRY",
            strategy_id="proven_strategy",
            mutation_scope="LEVEL_2_COMPONENT_GEOMETRY",
            quality_delta=0.10,
            blocker_delta=-1,
            success=True,
        )

    mult = reg.get_strategy_multiplier("proven_strategy", "ELEMENT_COLLISION", "PRESENTATION")
    assert mult == 1.35


# ---------------------------------------------------------------------------
# 24. Convergence Failure Reporter Generating All 13 Sections
# ---------------------------------------------------------------------------
def test_convergence_failure_reporter_13_sections(tmp_path: Path):
    out_file = tmp_path / "convergence_failure_report.md"
    ctx = ArtifactProductionContext(
        job_id="test_job_13",
        artifact_type="PRESENTATION",
        source_input="test raw input content",
        output_dir=tmp_path,
    )
    ctx.state_machine._current_state = ProductionState.MANUAL_REVIEW_REQUIRED
    ctx.quality_authority_result = UnifiedQualityReport(
        artifact_type="PRESENTATION",
        decision=ExportDecision.MANUAL_REVIEW_REQUIRED,
        overall_quality_score=0.74,
        can_export=False,
        repair_required=True,
        hard_blockers=("ELEMENT_COLLISION",),
        findings=(
            QualityFinding(
                dimension="PHYSICAL_GEOMETRY",
                severity="CRITICAL",
                failure_code="ELEMENT_COLLISION",
                message="Bounding box overlap 689 sq pt",
            ),
        ),
    )

    md = ConvergenceFailureReporter.generate_report(
        context=ctx,
        output_path=out_file,
        progress_history=[],
        detected_pattern=FailurePatternType.TOKEN_CHURN,
        pattern_rationale="Repeated token mutations.",
        termination_cause="Hard blocker unresolved.",
    )

    assert out_file.exists()
    assert "# CONVERGENCE FAILURE EXPLANATION REPORT" in md
    for i in range(1, 14):
        assert f"## {i}." in md


# ---------------------------------------------------------------------------
# 25. Zero AI API Call Invariant (Offline Determinism)
# ---------------------------------------------------------------------------
def test_zero_ai_api_call_invariant(monkeypatch):
    def unauthorized_api_call(*args, **kwargs):
        raise RuntimeError("CRITICAL INVARIANT VIOLATION: AI API call attempted in deterministic repair engine!")

    for mod_name in ("requests", "urllib.request", "httpx"):
        try:
            mod = __import__(mod_name)
            if hasattr(mod, "post"):
                monkeypatch.setattr(mod, "post", unauthorized_api_call)
            if hasattr(mod, "get"):
                monkeypatch.setattr(mod, "get", unauthorized_api_call)
        except ImportError:
            pass

    budget = MutationBudgetTracker(get_budget_for_artifact("PRESENTATION"))
    target = RepairTarget(element_id="beat-1", slide_index=1, artifact_type="PRESENTATION")
    hyp = RootCauseHypothesis(
        cause_type=RootCauseType.GRID_GEOMETRY,
        confidence=0.9,
        affected_targets=(target,),
        rationale="Collision",
    )
    beat = ConceptualBeat(
        beat_id="beat-1",
        sequence_index=1,
        title="Beat 1",
        primary_concept_unit_id="c1",
        narrative_function="FOUNDATION",
        information_gain=0.8,
        cognitive_load_target=0.5,
        visual_priority="HIGH_DIAGRAM",
        selection_rationale="Rationale",
    )
    bp = make_presentation_bp([beat])
    strats = [PresentationComponentReflowStrategy()]

    opts = RepairCandidatePortfolio.evaluate_portfolio(
        strategies=strats,
        target=target,
        hypotheses=[hyp],
        budget_tracker=budget,
        blueprint=bp,
        artifact_type="PRESENTATION",
    )
    assert len(opts) > 0
