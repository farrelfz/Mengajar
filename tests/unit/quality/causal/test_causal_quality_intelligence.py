"""
Comprehensive Unit & Adversarial Test Suite for Quality Authority Consolidation & Causal Attribution.

Phase 3A.1 Test Matrix:
A. Authority Consolidation (Tests 1-4)
B. Symptom vs Root Cause Separation (Tests 5-8)
C. Failure Correlation & Clustering (Tests 9-11)
D. Scope Analysis (Tests 12-15)
E. Decision Policy & Gating (Tests 16-19)
F. Presentation Progression vs Monotony (Tests 20-22)
G. Worksheet Pedagogical Causal Attribution (Tests 23-25)
H. Scientific Document Academic Causal Attribution (Tests 26-27)
I. Cross-Phase Consolidation & Reporting (Tests 28-31)
"""

import pytest
from pathlib import Path

from app.quality.causal.contracts import (
    CanonicalFailure,
    FailureCluster,
    QualitySignal,
    RootCauseHypothesis,
    CanonicalQualityAssessment,
)
from app.quality.causal.taxonomy import (
    ArchitectureLayer,
    CanonicalFailureCategory,
    CanonicalFailureCode,
    CanonicalFailureSeverity,
    CanonicalRepairClass,
    CausalConfidenceLevel,
    FailureScope,
    UnifiedDecisionStatus,
)
from app.quality.causal.signal_normalizer import QualitySignalNormalizer
from app.quality.causal.failure_normalizer import FailureNormalizer
from app.quality.causal.evidence_collector import (
    CausalEvidenceCollector,
    MultiLayerEvidence,
)
from app.quality.causal.cause_catalog import CausalDefectCatalog
from app.quality.causal.confidence import CausalConfidenceEstimator
from app.quality.causal.scope_analyzer import ScopeAnalyzer
from app.quality.causal.failure_correlation import FailureCorrelationEngine
from app.quality.causal.repetition_analyzer import ProgressionAwareRepetitionAnalyzer
from app.quality.causal.repair_authority import RepairAuthorityMatrix
from app.quality.causal.artifact_causes import ArtifactCausalRules
from app.quality.causal.attribution_engine import CausalAttributionEngine
from app.quality.causal.quality_authority import UnifiedQualityAuthority
from app.quality.causal.reporter import CausalQualityReporter


# ============================================================================
# A. AUTHORITY CONSOLIDATION (Tests 1-4)
# ============================================================================

def test_01_duplicate_failure_codes_normalize_to_single_canonical_code():
    # Raw signals with different naming conventions representing the same defect
    sig1 = QualitySignal(
        source_engine="rendered_inspector",
        source_phase="PHASE_3A",
        artifact_type="PRESENTATION",
        page_indices=(2,),
        dimension="readability",
        metric_name="TEXT_TOO_SMALL",
        metric_value=7.5,
        severity=CanonicalFailureSeverity.MAJOR,
        description="Text span size 7.5pt below threshold",
    )
    sig2 = QualitySignal(
        source_engine="phase_2c_calibration",
        source_phase="PHASE_2C",
        artifact_type="PRESENTATION",
        page_indices=(2,),
        dimension="readability",
        metric_name="FONT_READABILITY_FAILURE",
        metric_value=7.5,
        severity=CanonicalFailureSeverity.MAJOR,
        description="Text font too small for slide",
    )

    failures = FailureNormalizer.normalize_signals([sig1, sig2], total_pages=10)
    assert len(failures) == 1
    assert failures[0].failure_code == CanonicalFailureCode.TEXT_TOO_SMALL
    assert failures[0].affected_pages == (2,)


def test_02_multiple_engines_produce_one_canonical_failure():
    sig_geom = QualitySignal(
        source_engine="pdf_geometry_inspector",
        source_phase="PHASE_3A",
        artifact_type="HANDOUT",
        page_indices=(1,),
        dimension="visual_geometry",
        metric_name="ELEMENT_COLLISION",
        metric_value=45.0,
        severity=CanonicalFailureSeverity.MAJOR,
        description="Collision of text elements",
    )
    sig_dom = QualitySignal(
        source_engine="legacy_dom_inspector",
        source_phase="LEGACY_GATE",
        artifact_type="HANDOUT",
        page_indices=(1,),
        dimension="layout",
        metric_name="ELEMENT_COLLISION",
        metric_value=45.0,
        severity=CanonicalFailureSeverity.MAJOR,
        description="DOM collision detected",
    )

    failures = FailureNormalizer.normalize_signals([sig_geom, sig_dom], total_pages=5)
    assert len(failures) == 1
    assert failures[0].failure_code == CanonicalFailureCode.ELEMENT_COLLISION
    assert len(failures[0].evidence_signals) == 2


def test_03_single_decision_authority_unifies_disparate_signals():
    # Pass both Phase 2C style signals and Phase 3A signals to UnifiedQualityAuthority
    assessment = UnifiedQualityAuthority.evaluate_artifact(
        artifact_type="HANDOUT",
        rendered_inspection=None,
        phase_2c_report=None,
        source_metadata=None,
    )
    assert assessment.decision == UnifiedDecisionStatus.PASS
    assert assessment.can_export is True
    assert isinstance(assessment, CanonicalQualityAssessment)


def test_04_conflicting_severities_resolved_deterministically():
    # If one engine flags MINOR and another flags CRITICAL for same failure code, CRITICAL wins
    sig_minor = QualitySignal(
        source_engine="engine_a",
        source_phase="PHASE_2C",
        artifact_type="PRESENTATION",
        page_indices=(3,),
        dimension="readability",
        metric_name="TEXT_TOO_SMALL",
        metric_value=9.0,
        severity=CanonicalFailureSeverity.MINOR,
        description="Slightly small text",
    )
    sig_crit = QualitySignal(
        source_engine="engine_b",
        source_phase="PHASE_3A",
        artifact_type="PRESENTATION",
        page_indices=(3,),
        dimension="readability",
        metric_name="TEXT_TOO_SMALL",
        metric_value=6.0,
        severity=CanonicalFailureSeverity.CRITICAL,
        description="Illegible micro text",
    )

    failures = FailureNormalizer.normalize_signals([sig_minor, sig_crit], total_pages=10)
    assert len(failures) == 1
    assert failures[0].severity == CanonicalFailureSeverity.CRITICAL


# ============================================================================
# B. SYMPTOM VS ROOT CAUSE SEPARATION (Tests 5-8)
# ============================================================================

def test_05_text_too_small_does_not_blindly_imply_typography_cause():
    # TEXT_TOO_SMALL is a physical symptom. If caused by 8 items crammed onto slide,
    # the root cause is BLUEPRINT_CAPACITY_MISMATCH, not typography!
    evidence = MultiLayerEvidence(
        artifact_type="PRESENTATION",
        total_pages=10,
        mean_blocks_per_page=6.5,
        max_blocks_per_page=8,
        blueprint_capacity_exceeded=True,
        is_font_isolated_to_dense_pages=True,
        is_font_globally_small=False,
    )
    failure = CanonicalFailure(
        failure_code=CanonicalFailureCode.TEXT_TOO_SMALL,
        category=CanonicalFailureCategory.RENDER,
        artifact_type="PRESENTATION",
        affected_pages=(4,),
        severity=CanonicalFailureSeverity.CRITICAL,
        symptom="Font size 7.0pt on slide 4",
        quality_dimension="readability",
        scope=FailureScope.LOCAL,
    )

    hyps, _ = CausalAttributionEngine.attribute([failure], evidence)
    assert len(hyps) >= 1
    assert hyps[0].cause_code == "BLUEPRINT_CAPACITY_MISMATCH"
    assert hyps[0].cause_layer == ArchitectureLayer.BLUEPRINT
    assert CanonicalRepairClass.CLASS_D_BLUEPRINT_REGROUPING in hyps[0].allowed_repair_classes
    assert "GLOBAL_FONT_SHRINK" in hyps[0].forbidden_repairs


def test_06_dense_blueprint_plus_tiny_text_attributes_to_blueprint_capacity():
    evidence = MultiLayerEvidence(
        artifact_type="PRESENTATION",
        total_pages=5,
        max_blocks_per_page=9,
        blueprint_capacity_exceeded=True,
        is_font_isolated_to_dense_pages=True,
    )
    failure = CanonicalFailure(
        failure_code=CanonicalFailureCode.TEXT_TOO_SMALL,
        category=CanonicalFailureCategory.RENDER,
        artifact_type="PRESENTATION",
        affected_pages=(2,),
        severity=CanonicalFailureSeverity.MAJOR,
        symptom="Font reduction on dense slide 2",
        quality_dimension="readability",
    )
    hyps, _ = CausalAttributionEngine.attribute([failure], evidence)
    assert hyps[0].cause_layer == ArchitectureLayer.BLUEPRINT
    assert hyps[0].confidence_level == CausalConfidenceLevel.HIGH


def test_07_normal_blueprint_plus_globally_tiny_font_attributes_to_typography():
    # When all pages have tiny font despite normal, sparse content,
    # it is a global CSS typography configuration defect!
    evidence = MultiLayerEvidence(
        artifact_type="PRESENTATION",
        total_pages=10,
        max_blocks_per_page=2,
        blueprint_capacity_exceeded=False,
        is_font_globally_small=True,
        is_font_isolated_to_dense_pages=False,
    )
    failure = CanonicalFailure(
        failure_code=CanonicalFailureCode.TEXT_TOO_SMALL,
        category=CanonicalFailureCategory.RENDER,
        artifact_type="PRESENTATION",
        affected_pages=tuple(range(1, 11)),
        severity=CanonicalFailureSeverity.MAJOR,
        symptom="Small font across all 10 slides",
        quality_dimension="readability",
        scope=FailureScope.SYSTEMIC,
    )
    hyps, _ = CausalAttributionEngine.attribute([failure], evidence)
    assert hyps[0].cause_code == "TYPOGRAPHY_CONFIGURATION_FAILURE"
    assert hyps[0].cause_layer == ArchitectureLayer.TYPOGRAPHY
    assert CanonicalRepairClass.CLASS_B_TYPOGRAPHY in hyps[0].allowed_repair_classes


def test_08_ambiguous_cause_forbids_automatic_repair():
    # If evidence does not clearly indicate blueprint or typography
    evidence = MultiLayerEvidence(
        artifact_type="PRESENTATION",
        total_pages=10,
        max_blocks_per_page=3,
        blueprint_capacity_exceeded=False,
        is_font_globally_small=False,
        is_font_isolated_to_dense_pages=False,
    )
    failure = CanonicalFailure(
        failure_code=CanonicalFailureCode.TEXT_TOO_SMALL,
        category=CanonicalFailureCategory.RENDER,
        artifact_type="PRESENTATION",
        affected_pages=(3,),
        severity=CanonicalFailureSeverity.MAJOR,
        symptom="Font reduction on slide 3 with normal content",
        quality_dimension="readability",
        scope=FailureScope.LOCAL,
    )
    hyps, _ = CausalAttributionEngine.attribute([failure], evidence)
    assert hyps[0].confidence_level in (CausalConfidenceLevel.LOW, CausalConfidenceLevel.AMBIGUOUS)
    # Prohibits automatic repair
    policy = RepairAuthorityMatrix.get_repair_policy(hyps[0].cause_code, hyps[0].confidence_level)
    assert policy.requires_manual_review is True
    assert CanonicalRepairClass.CLASS_G_MANUAL_REVIEW in policy.allowed_repair_classes
    assert not RepairAuthorityMatrix.is_repair_allowed(
        hyps[0].cause_code, CanonicalRepairClass.CLASS_A_GEOMETRY, hyps[0].confidence_level
    )


# ============================================================================
# C. FAILURE CORRELATION & CLUSTERING (Tests 9-11)
# ============================================================================

def test_09_three_correlated_symptoms_cluster_into_single_defect():
    # Slide 5 exhibits tiny text, element collision, and density overload
    f1 = CanonicalFailure(
        failure_code=CanonicalFailureCode.TEXT_TOO_SMALL,
        category=CanonicalFailureCategory.RENDER,
        artifact_type="PRESENTATION",
        affected_pages=(5,),
        severity=CanonicalFailureSeverity.CRITICAL,
        symptom="Tiny text",
        quality_dimension="readability",
    )
    f2 = CanonicalFailure(
        failure_code=CanonicalFailureCode.ELEMENT_COLLISION,
        category=CanonicalFailureCategory.RENDER,
        artifact_type="PRESENTATION",
        affected_pages=(5,),
        severity=CanonicalFailureSeverity.CRITICAL,
        symptom="Colliding blocks",
        quality_dimension="geometry",
    )
    f3 = CanonicalFailure(
        failure_code=CanonicalFailureCode.DENSITY_OVERLOAD,
        category=CanonicalFailureCategory.DENSITY,
        artifact_type="PRESENTATION",
        affected_pages=(5,),
        severity=CanonicalFailureSeverity.MAJOR,
        symptom="Overloaded slide",
        quality_dimension="density",
    )
    evidence = MultiLayerEvidence(
        artifact_type="PRESENTATION",
        total_pages=10,
        max_blocks_per_page=8,
        blueprint_capacity_exceeded=True,
    )

    clusters = FailureCorrelationEngine.cluster_failures([f1, f2, f3], evidence)
    assert len(clusters) == 1
    assert clusters[0].affected_pages == (5,)
    assert set(clusters[0].symptoms) == {
        CanonicalFailureCode.TEXT_TOO_SMALL,
        CanonicalFailureCode.ELEMENT_COLLISION,
        CanonicalFailureCode.DENSITY_OVERLOAD,
    }
    assert clusters[0].primary_root_cause.cause_code == "BLUEPRINT_CAPACITY_MISMATCH"


def test_10_unrelated_failures_on_distinct_pages_remain_separate_clusters():
    # Page 2 has collision; Page 8 has duplicate composition
    f_p2 = CanonicalFailure(
        failure_code=CanonicalFailureCode.ELEMENT_COLLISION,
        category=CanonicalFailureCategory.RENDER,
        artifact_type="PRESENTATION",
        affected_pages=(2,),
        severity=CanonicalFailureSeverity.MAJOR,
        symptom="Collision on slide 2",
        quality_dimension="geometry",
    )
    f_p8 = CanonicalFailure(
        failure_code=CanonicalFailureCode.DUPLICATE_COMPOSITION,
        category=CanonicalFailureCategory.LAYOUT,
        artifact_type="PRESENTATION",
        affected_pages=(8, 9),
        severity=CanonicalFailureSeverity.MAJOR,
        symptom="Duplicate slides 8-9",
        quality_dimension="rhythm",
    )
    evidence = MultiLayerEvidence(artifact_type="PRESENTATION", total_pages=10)

    clusters = FailureCorrelationEngine.cluster_failures([f_p2, f_p8], evidence)
    assert len(clusters) == 2


def test_11_common_affected_pages_bridge_failures_into_shared_cluster():
    # Failure A on pages (2, 3), Failure B on pages (3, 4) -> connected component (2, 3, 4)
    fa = CanonicalFailure(
        failure_code=CanonicalFailureCode.TEXT_TOO_SMALL,
        category=CanonicalFailureCategory.RENDER,
        artifact_type="PRESENTATION",
        affected_pages=(2, 3),
        severity=CanonicalFailureSeverity.MAJOR,
        symptom="Tiny text on 2-3",
        quality_dimension="readability",
    )
    fb = CanonicalFailure(
        failure_code=CanonicalFailureCode.CARD_OVERLOAD,
        category=CanonicalFailureCategory.LAYOUT,
        artifact_type="PRESENTATION",
        affected_pages=(3, 4),
        severity=CanonicalFailureSeverity.MAJOR,
        symptom="Card overload on 3-4",
        quality_dimension="layout",
    )
    evidence = MultiLayerEvidence(artifact_type="PRESENTATION", total_pages=10)

    clusters = FailureCorrelationEngine.cluster_failures([fa, fb], evidence)
    assert len(clusters) == 1
    assert clusters[0].affected_pages == (2, 3, 4)


# ============================================================================
# D. SCOPE ANALYSIS (Tests 12-15)
# ============================================================================

def test_12_single_page_issue_is_local_scope():
    scope = ScopeAnalyzer.analyze_scope(affected_pages=(4,), total_pages=20)
    assert scope == FailureScope.LOCAL


def test_13_consecutive_page_streak_is_cluster_scope():
    # 3 consecutive pages in a 15-page document
    scope = ScopeAnalyzer.analyze_scope(affected_pages=(4, 5, 6), total_pages=15)
    assert scope == FailureScope.CLUSTER


def test_14_majority_pages_affected_is_systemic_scope():
    # 8 out of 10 pages affected (> 50%)
    scope = ScopeAnalyzer.analyze_scope(affected_pages=tuple(range(1, 9)), total_pages=10)
    assert scope == FailureScope.SYSTEMIC


def test_15_inherent_document_defect_is_artifact_wide_scope():
    scope = ScopeAnalyzer.analyze_scope(
        affected_pages=tuple(range(1, 11)),
        total_pages=10,
        failure_code=CanonicalFailureCode.SCIENTIFIC_CITATION_INVISIBLE,
    )
    assert scope == FailureScope.ARTIFACT_WIDE


# ============================================================================
# E. DECISION POLICY & GATING (Tests 16-19)
# ============================================================================

def test_16_major_local_issue_does_not_block_multi_page_document():
    # 1 minor/major local issue on 1 page of a 20-page handout -> PASS_WITH_WARNINGS
    f = CanonicalFailure(
        failure_code=CanonicalFailureCode.ORPHAN_HEADING,
        category=CanonicalFailureCategory.ARTIFACT_SPECIFIC,
        artifact_type="HANDOUT",
        affected_pages=(3,),
        severity=CanonicalFailureSeverity.MAJOR,
        symptom="Orphan heading at bottom of page 3",
        quality_dimension="reading_flow",
        scope=FailureScope.LOCAL,
    )
    decision, can_export, repair_req, _, _ = UnifiedQualityAuthority._arbitrate_decision(
        failures=[f],
        clusters=[],
        hypotheses=[],
        critical_count=0,
        major_count=1,
        minor_count=0,
        overall_score=0.92,
        total_pages=20,
    )
    assert decision == UnifiedDecisionStatus.PASS_WITH_WARNINGS
    assert can_export is True
    assert repair_req is False


def test_17_major_systemic_issue_requires_repair():
    # Systemic major issue affecting majority of pages
    f = CanonicalFailure(
        failure_code=CanonicalFailureCode.TEXT_TOO_SMALL,
        category=CanonicalFailureCategory.RENDER,
        artifact_type="PRESENTATION",
        affected_pages=tuple(range(1, 9)),
        severity=CanonicalFailureSeverity.MAJOR,
        symptom="Tiny text across 8 slides",
        quality_dimension="readability",
        scope=FailureScope.SYSTEMIC,
    )
    decision, can_export, repair_req, _, _ = UnifiedQualityAuthority._arbitrate_decision(
        failures=[f],
        clusters=[],
        hypotheses=[],
        critical_count=0,
        major_count=1,
        minor_count=0,
        overall_score=0.82,
        total_pages=10,
    )
    assert decision == UnifiedDecisionStatus.NEEDS_REPAIR
    assert can_export is False
    assert repair_req is True


def test_18_critical_failure_unconditionally_blocks_export():
    # Even with high composite score (0.95), CRITICAL failure forces BLOCKED
    f = CanonicalFailure(
        failure_code=CanonicalFailureCode.TEXT_CLIPPING,
        category=CanonicalFailureCategory.RENDER,
        artifact_type="PRESENTATION",
        affected_pages=(1,),
        severity=CanonicalFailureSeverity.CRITICAL,
        symptom="Content pushed past right edge",
        quality_dimension="geometry",
        scope=FailureScope.LOCAL,
    )
    decision, can_export, repair_req, _, _ = UnifiedQualityAuthority._arbitrate_decision(
        failures=[f],
        clusters=[],
        hypotheses=[],
        critical_count=1,
        major_count=0,
        minor_count=0,
        overall_score=0.95,
        total_pages=10,
    )
    assert decision == UnifiedDecisionStatus.BLOCKED
    assert can_export is False
    assert repair_req is True


def test_19_high_score_cannot_hide_critical_failure():
    # Demonstrates mathematical gatekeeping override
    sig_crit = QualitySignal(
        source_engine="rendered_inspector",
        source_phase="PHASE_3A",
        artifact_type="PRESENTATION",
        page_indices=(5,),
        dimension="geometry",
        metric_name="ELEMENT_COLLISION",
        metric_value=500.0,
        severity=CanonicalFailureSeverity.CRITICAL,
        description="Massive overlapping collision",
    )
    failures = FailureNormalizer.normalize_signals([sig_crit], total_pages=14)
    assessment = UnifiedQualityAuthority.evaluate_artifact(
        artifact_type="PRESENTATION",
        rendered_inspection=None,
    )
    # When critical failure is present, assessment is BLOCKED
    crit_assessment = CanonicalQualityAssessment(
        artifact_type="PRESENTATION",
        page_count=14,
        overall_quality_score=0.98,  # Fake high score
        failures=tuple(failures),
        critical_failures_count=1,
        decision=UnifiedDecisionStatus.BLOCKED,
        can_export=False,
        repair_required=True,
        manual_review_required=False,
        rationale="Blocked by critical collision",
    )
    assert crit_assessment.can_export is False
    assert crit_assessment.decision == UnifiedDecisionStatus.BLOCKED


# ============================================================================
# F. PRESENTATION PROGRESSION VS MONOTONY (Tests 20-22)
# ============================================================================

def test_20_progressive_reveal_does_not_trigger_repetition_penalty():
    # Slide 1 defines problem; Slide 2 builds on it by adding the mathematical formula
    text_s1 = "Dinamika Fluida: Eksperimen Oobleck. Karakteristik fluida non-Newtonian."
    text_s2 = "Dinamika Fluida: Eksperimen Oobleck. Karakteristik fluida non-Newtonian. Rumus laju geser: gamma = dv/dy."

    res = ProgressionAwareRepetitionAnalyzer.evaluate_pair(
        page_a=1,
        page_b=2,
        text_a=text_s1,
        text_b=text_s2,
        visual_similarity=0.92,
        is_marked_progressive=True,
    )
    assert res.is_progressive_reveal is True
    assert res.is_intentional_continuity is True
    assert res.is_layout_monotony is False
    assert res.penalty_score == 0.0


def test_21_high_visual_similarity_with_low_information_gain_triggers_monotony():
    # Two slides with essentially identical text and identical layout
    text_a = "Karakteristik fluida non-newtonian dengan pengamatan visual sederhana."
    text_b = "Karakteristik fluida non-newtonian dengan pengamatan visual sederhana."

    res = ProgressionAwareRepetitionAnalyzer.evaluate_pair(
        page_a=3,
        page_b=4,
        text_a=text_a,
        text_b=text_b,
        visual_similarity=0.95,
        is_marked_progressive=False,
    )
    assert res.is_intentional_continuity is False
    assert res.is_layout_monotony is True
    assert res.penalty_score > 0.0


def test_22_presentation_handout_collapse_maps_to_transformation():
    failure = CanonicalFailure(
        failure_code=CanonicalFailureCode.PRESENTATION_HANDOUT_COLLAPSE,
        category=CanonicalFailureCategory.ARTIFACT_SPECIFIC,
        artifact_type="PRESENTATION",
        affected_pages=(2,),
        severity=CanonicalFailureSeverity.MAJOR,
        symptom="1400 characters on single slide",
        quality_dimension="density",
    )
    evidence = MultiLayerEvidence(artifact_type="PRESENTATION", total_pages=5)
    hyp = ArtifactCausalRules.evaluate_presentation_cause(failure, evidence)

    assert hyp is not None
    assert hyp.cause_code == "COMPRESSION_FAILURE"
    assert hyp.cause_layer == ArchitectureLayer.TRANSFORMATION
    assert CanonicalRepairClass.CLASS_E_TRANSFORMATION_STRATEGY in hyp.allowed_repair_classes
    assert "TINY_FONT_SHRINK" in hyp.forbidden_repairs


# ============================================================================
# G. WORKSHEET PEDAGOGICAL CAUSAL ATTRIBUTION (Tests 23-25)
# ============================================================================

def test_23_worksheet_quiz_collapse_maps_to_transformation_strategy():
    failure = CanonicalFailure(
        failure_code=CanonicalFailureCode.WORKSHEET_QUIZ_COLLAPSE,
        category=CanonicalFailureCategory.ARTIFACT_SPECIFIC,
        artifact_type="WORKSHEET",
        affected_pages=(1, 2, 3),
        severity=CanonicalFailureSeverity.MAJOR,
        symptom="12 multiple choice questions without inquiry phases",
        quality_dimension="pedagogy",
    )
    evidence = MultiLayerEvidence(artifact_type="WORKSHEET", total_pages=3)
    hyp = ArtifactCausalRules.evaluate_worksheet_cause(failure, evidence)

    assert hyp.cause_code == "TRANSFORMATION_SELECTION_FAILURE"
    assert hyp.cause_layer == ArchitectureLayer.TRANSFORMATION
    assert hyp.repair_authority == ArchitectureLayer.TRANSFORMATION
    assert "LAYOUT_CSS_PATCH" in hyp.forbidden_repairs


def test_24_insufficient_workspace_maps_to_blueprint_and_geometry():
    failure = CanonicalFailure(
        failure_code=CanonicalFailureCode.WORKSHEET_WORKSPACE_INSUFFICIENT,
        category=CanonicalFailureCategory.ARTIFACT_SPECIFIC,
        artifact_type="WORKSHEET",
        affected_pages=(2,),
        severity=CanonicalFailureSeverity.MAJOR,
        symptom="Questions lack student writing response boxes",
        quality_dimension="pedagogy",
    )
    evidence = MultiLayerEvidence(artifact_type="WORKSHEET", total_pages=3)
    hyp = ArtifactCausalRules.evaluate_worksheet_cause(failure, evidence)

    assert hyp.cause_code == "WORKSPACE_ALLOCATION_FAILURE"
    assert hyp.cause_layer == ArchitectureLayer.BLUEPRINT
    assert CanonicalRepairClass.CLASS_A_GEOMETRY in hyp.allowed_repair_classes


def test_25_worksheet_spoiling_failure_maps_to_artifact_policy():
    failure = CanonicalFailure(
        failure_code=CanonicalFailureCode.WORKSHEET_SPOILING_FAILURE,
        category=CanonicalFailureCategory.ARTIFACT_SPECIFIC,
        artifact_type="WORKSHEET",
        affected_pages=(1,),
        severity=CanonicalFailureSeverity.CRITICAL,
        symptom="Kunci jawaban exposed on page 1",
        quality_dimension="pedagogy",
    )
    evidence = MultiLayerEvidence(artifact_type="WORKSHEET", total_pages=3)
    hyp = ArtifactCausalRules.evaluate_worksheet_cause(failure, evidence)

    assert hyp.cause_code == "ANTI_SPOILING_POLICY_BREACH"
    assert hyp.cause_layer == ArchitectureLayer.ARTIFACT_POLICY
    assert hyp.confidence_score >= 0.95
    assert "CSS_OPACITY_ZERO" in hyp.forbidden_repairs


# ============================================================================
# H. SCIENTIFIC DOCUMENT ACADEMIC CAUSAL ATTRIBUTION (Tests 26-27)
# ============================================================================

def test_26_scientific_invisible_citation_distinguishes_semantic_vs_render_cause():
    # Case 1: Source has citations, but rendered body text is missing citations -> CITATION_RENDER_SUPPRESSION (COMPOSITION layer)
    f = CanonicalFailure(
        failure_code=CanonicalFailureCode.SCIENTIFIC_CITATION_INVISIBLE,
        category=CanonicalFailureCategory.ARTIFACT_SPECIFIC,
        artifact_type="SCIENTIFIC_DOCUMENT",
        affected_pages=tuple(range(1, 11)),
        severity=CanonicalFailureSeverity.MAJOR,
        symptom="Zero citations in 10-page paper",
        quality_dimension="academic_rigor",
    )
    ev_render_bug = MultiLayerEvidence(
        artifact_type="SCIENTIFIC_DOCUMENT",
        total_pages=10,
        raw_metadata={"source_citations_count": 5},
    )
    hyp_render = ArtifactCausalRules.evaluate_scientific_cause(f, ev_render_bug)
    assert hyp_render.cause_code == "CITATION_RENDER_SUPPRESSION"
    assert hyp_render.cause_layer == ArchitectureLayer.COMPOSITION
    assert "REWRITE_SOURCE_CLAIMS" in hyp_render.forbidden_repairs

    # Case 2: Source itself has zero citations -> EVIDENCE_DISCIPLINE_FAILURE (SOURCE layer)
    ev_source_bug = MultiLayerEvidence(
        artifact_type="SCIENTIFIC_DOCUMENT",
        total_pages=10,
        raw_metadata={"source_citations_count": 0},
    )
    hyp_source = ArtifactCausalRules.evaluate_scientific_cause(f, ev_source_bug)
    assert hyp_source.cause_code == "EVIDENCE_DISCIPLINE_FAILURE"
    assert hyp_source.cause_layer == ArchitectureLayer.SOURCE


def test_27_scientific_bab_inversion_maps_to_transformation_sequencing():
    failure = CanonicalFailure(
        failure_code=CanonicalFailureCode.SCIENTIFIC_HIERARCHY_FAILURE,
        category=CanonicalFailureCategory.ARTIFACT_SPECIFIC,
        artifact_type="SCIENTIFIC_DOCUMENT",
        affected_pages=(1, 2),
        severity=CanonicalFailureSeverity.CRITICAL,
        symptom="BAB II placed before BAB I",
        quality_dimension="academic_rigor",
    )
    evidence = MultiLayerEvidence(artifact_type="SCIENTIFIC_DOCUMENT", total_pages=5)
    hyp = ArtifactCausalRules.evaluate_scientific_cause(failure, evidence)

    assert hyp.cause_code == "SEQUENCING_FAILURE"
    assert hyp.cause_layer == ArchitectureLayer.TRANSFORMATION
    assert CanonicalRepairClass.CLASS_E_TRANSFORMATION_STRATEGY in hyp.allowed_repair_classes


# ============================================================================
# I. CROSS-PHASE CONSOLIDATION & REPORTING (Tests 28-31)
# ============================================================================

def test_28_cross_phase_signal_consolidation(tmp_path: Path):
    # Consolidate signals from Phase 2B, Phase 2C, and Phase 3A
    sig_2b = QualitySignal(
        source_engine="unified_fidelity_validator",
        source_phase="PHASE_2B",
        artifact_type="PRESENTATION",
        dimension="contract_fidelity",
        metric_name="fidelity_violation",
        metric_value=False,
        severity=CanonicalFailureSeverity.CRITICAL,
        description="Dropped 2 source entities",
    )
    sig_3a = QualitySignal(
        source_engine="rendered_geometry_inspector",
        source_phase="PHASE_3A",
        artifact_type="PRESENTATION",
        page_indices=(5,),
        dimension="geometry",
        metric_name="ELEMENT_COLLISION",
        metric_value=250.0,
        severity=CanonicalFailureSeverity.CRITICAL,
        description="Collision on slide 5",
    )

    failures = FailureNormalizer.normalize_signals([sig_2b, sig_3a], total_pages=14)
    assert len(failures) == 2
    assert any(f.failure_code == CanonicalFailureCode.ELEMENT_COLLISION for f in failures)


def test_29_causal_quality_report_generation(tmp_path: Path):
    f = CanonicalFailure(
        failure_code=CanonicalFailureCode.ELEMENT_COLLISION,
        category=CanonicalFailureCategory.RENDER,
        artifact_type="PRESENTATION",
        affected_pages=(5,),
        severity=CanonicalFailureSeverity.CRITICAL,
        symptom="Overlapping element collision",
        quality_dimension="geometry",
    )
    hyp = RootCauseHypothesis(
        cause_code="BLUEPRINT_CAPACITY_MISMATCH",
        cause_layer=ArchitectureLayer.BLUEPRINT,
        confidence_score=0.88,
        confidence_level=CausalConfidenceLevel.HIGH,
        supporting_evidence=("Slide contains 8 items exceeding 5-item threshold",),
        affected_scope=FailureScope.LOCAL,
        repair_authority=ArchitectureLayer.BLUEPRINT,
        allowed_repair_classes=(CanonicalRepairClass.CLASS_D_BLUEPRINT_REGROUPING,),
        forbidden_repairs=("GLOBAL_FONT_SHRINK",),
    )
    cluster = FailureCluster(
        affected_pages=(5,),
        symptoms=(CanonicalFailureCode.ELEMENT_COLLISION,),
        failures=(f,),
        primary_root_cause=hyp,
        recommended_repair_class=CanonicalRepairClass.CLASS_D_BLUEPRINT_REGROUPING,
        rationale="Overload on slide 5",
    )
    assessment = CanonicalQualityAssessment(
        artifact_type="PRESENTATION",
        rendered_pdf_path="/path/to/test.pdf",
        page_count=10,
        overall_quality_score=0.65,
        failures=(f,),
        failure_clusters=(cluster,),
        root_cause_hypotheses=(hyp,),
        critical_failures_count=1,
        decision=UnifiedDecisionStatus.BLOCKED,
        can_export=False,
        repair_required=True,
        manual_review_required=False,
        rationale="Export blocked due to critical collision on slide 5",
    )

    md_p, json_p = CausalQualityReporter.save_reports(assessment, tmp_path)
    assert md_p.exists() and md_p.stat().st_size > 200
    assert json_p.exists() and json_p.stat().st_size > 200

    content = md_p.read_text(encoding="utf-8")
    assert "BLUEPRINT_CAPACITY_MISMATCH" in content
    assert "CLASS_D_BLUEPRINT_REGROUPING" in content
    assert "GLOBAL_FONT_SHRINK" in content


def test_30_repair_authority_matrix_validates_allowed_and_forbidden_actions():
    # Verify matrix contract
    policy = RepairAuthorityMatrix.get_repair_policy("BLUEPRINT_CAPACITY_MISMATCH", CausalConfidenceLevel.HIGH)
    assert policy.owning_layer == ArchitectureLayer.BLUEPRINT
    assert CanonicalRepairClass.CLASS_D_BLUEPRINT_REGROUPING in policy.allowed_repair_classes
    assert "GLOBAL_FONT_SHRINK" in policy.forbidden_repairs


def test_31_zero_defect_clean_artifact_passes_with_no_repairs_required():
    assessment = UnifiedQualityAuthority.evaluate_artifact(
        artifact_type="HANDOUT",
        rendered_inspection=None,
    )
    assert assessment.decision == UnifiedDecisionStatus.PASS
    assert assessment.can_export is True
    assert assessment.repair_required is False
    assert assessment.manual_review_required is False
    assert len(assessment.failures) == 0
    assert len(assessment.failure_clusters) == 0
