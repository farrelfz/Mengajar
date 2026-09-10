"""
Universal Document Intelligence System V5 — Phase 3B Causality Unit Tests.

Tests 19 to 28:
- Symptom vs cause classification
- Causal rule matching
- Multi-hypothesis generation
- Evidence scoring & explanatory coverage
- Lineage consistency validation
- Contradiction penalty enforcement
- Ambiguity detection (score delta <= 0.10)
- Authoritative CausalDecision states
- Explainable causal path formatting
- VERY_HIGH confidence invariants
"""

import pytest
from app.quality.causal.causal_path import CausalPath, CausalPathNode
from app.quality.causal.causal_taxonomy import (
    CausalArchitecturalLayer,
    CausalConfidenceLevel,
    CausalDecision,
    RootCauseCategory,
)
from app.quality.causal.competing_analysis import CompetingHypothesisAnalyzer
from app.quality.causal.contracts import FailureCluster, QualityLocation, QualitySignal, RootCauseHypothesis
from app.quality.causal.evidence_scorer import CausalEvidenceScorer
from app.quality.causal.rules import CausalRuleCatalog
from app.quality.causal.symptom_classifier import FailureRole, SymptomCauseClassifier
from app.quality.causal.taxonomy import (
    CanonicalFailureCode,
    CanonicalFailureDomain,
    CanonicalSeverity,
    FailureScope,
)


def _make_signal(
    sig_id: str,
    code: CanonicalFailureCode,
    domain: CanonicalFailureDomain = CanonicalFailureDomain.PHYSICAL_RENDER,
    page: int = 1,
) -> QualitySignal:
    return QualitySignal(
        signal_id=sig_id,
        source_engine="test_engine",
        failure_domain=domain,
        failure_code=code,
        severity=CanonicalSeverity.MAJOR,
        location=QualityLocation(
            artifact_type="PRESENTATION",
            page_index=page,
            element_id="elem_1",
        ),
        description=f"Test defect {code.value}",
    )


def _make_cluster(signals, symptoms=None, scope=FailureScope.LOCAL) -> FailureCluster:
    s = tuple(signals)
    syms = tuple(symptoms or [sig.failure_code for sig in signals])
    return FailureCluster(
        cluster_id="clust_test_1",
        affected_pages=(1,),
        symptoms=syms,
        signals=s,
        scope=scope,
        dominant_failure_patterns=tuple(c.value for c in syms),
        affected_locations=tuple(sig.location for sig in s),
        correlation_strength=0.85,
    )


def test_19_symptom_vs_cause_classification():
    """Test 19: Physical render defects are classified as PRIMARY_SYMPTOM; blueprint defects as ROOT_CAUSE_CANDIDATE."""
    s_sym = _make_signal("s_sym", CanonicalFailureCode.TEXT_CLIPPING, domain=CanonicalFailureDomain.PHYSICAL_RENDER)
    s_cause = _make_signal("s_cause", CanonicalFailureCode.BLUEPRINT_CAPACITY_MISMATCH, domain=CanonicalFailureDomain.BLUEPRINT_INTEGRITY)

    cluster = _make_cluster([s_sym, s_cause])
    roles = SymptomCauseClassifier.classify_cluster_signals(cluster)

    role_map = {r.signal_id: r.role for r in roles}
    assert role_map["s_sym"] == FailureRole.PRIMARY_SYMPTOM
    assert role_map["s_cause"] == FailureRole.ROOT_CAUSE_CANDIDATE


def test_20_causal_rule_matching():
    """Test 20: Causal rules match clusters based on required patterns and artifact constraints."""
    catalog = CausalRuleCatalog()

    s1 = _make_signal("s1", CanonicalFailureCode.TEXT_TOO_SMALL)
    s2 = _make_signal("s2", CanonicalFailureCode.DENSITY_OVERLOAD, domain=CanonicalFailureDomain.COGNITIVE_LOAD)

    cluster = _make_cluster([s1, s2])
    matches = catalog.match(cluster, artifact_type="PRESENTATION")

    assert len(matches) > 0
    top_match = matches[0]
    assert top_match.rule.candidate_root_cause == RootCauseCategory.LAYOUT_CAPACITY_EXCEEDED
    assert top_match.rule.architectural_layer == CausalArchitecturalLayer.COMPOSITION


def test_21_multi_hypothesis_generation():
    """Test 21: Ambiguous symptom patterns match multiple competing candidate rules."""
    catalog = CausalRuleCatalog()

    # TEXT_TOO_SMALL with no density overload could be typography or capacity
    s1 = _make_signal("s1", CanonicalFailureCode.TEXT_TOO_SMALL)
    cluster = _make_cluster([s1])

    matches = catalog.match(cluster, artifact_type="PRESENTATION")
    matched_causes = [m.rule.candidate_root_cause for m in matches]

    # Both typography scale failure and layout capacity are candidate hypotheses
    assert RootCauseCategory.TYPOGRAPHY_SCALE_FAILURE in matched_causes


def test_22_evidence_scoring_explanatory_coverage():
    """Test 22: Explanatory coverage heavily factors into the causal confidence score."""
    scorer = CausalEvidenceScorer()

    s1 = _make_signal("s1", CanonicalFailureCode.TEXT_CLIPPING)
    s2 = _make_signal("s2", CanonicalFailureCode.TEXT_TOO_SMALL)
    s3 = _make_signal("s3", CanonicalFailureCode.ELEMENT_COLLISION)
    cluster = _make_cluster([s1, s2, s3])

    score_full, _, bd_full, _ = scorer.score_hypothesis(
        cluster=cluster,
        candidate_layer=CausalArchitecturalLayer.COMPOSITION,
        explains_signal_count=3,
        base_match_score=0.85,
    )

    score_partial, _, bd_partial, _ = scorer.score_hypothesis(
        cluster=cluster,
        candidate_layer=CausalArchitecturalLayer.COMPOSITION,
        explains_signal_count=1,
        base_match_score=0.85,
    )

    assert bd_full.explanatory_coverage == 1.0
    assert bd_partial.explanatory_coverage == pytest.approx(1.0 / 3.0, abs=0.01)
    assert score_full > score_partial


def test_23_lineage_consistency_downstream_cannot_cause_upstream():
    """Test 23: Downstream layers cannot cause upstream flaws (lineage consistency penalty)."""
    scorer = CausalEvidenceScorer()

    # Upstream symptom in BLUEPRINT domain
    s_bp = _make_signal("s_bp", CanonicalFailureCode.BLUEPRINT_CAPACITY_MISMATCH, domain=CanonicalFailureDomain.BLUEPRINT_INTEGRITY)
    cluster = _make_cluster([s_bp])

    # Hypothesizing RENDERING (stage 7) as cause for BLUEPRINT (stage 4)
    score, _, bd, notes = scorer.score_hypothesis(
        cluster=cluster,
        candidate_layer=CausalArchitecturalLayer.RENDERING,
        explains_signal_count=1,
        base_match_score=0.80,
    )

    assert bd.lineage_consistency == 0.10
    assert any("Lineage violation" in n for n in notes)


def test_24_contradiction_penalty_enforcement():
    """Test 24: Explicit contradictory evidence drastically reduces confidence score."""
    scorer = CausalEvidenceScorer()

    s1 = _make_signal("s1", CanonicalFailureCode.TEXT_CLIPPING)
    cluster = _make_cluster([s1])

    score_clean, _, bd_clean, _ = scorer.score_hypothesis(
        cluster=cluster,
        candidate_layer=CausalArchitecturalLayer.COMPOSITION,
        explains_signal_count=1,
        base_match_score=0.85,
        has_contradiction=False,
    )

    score_contra, _, bd_contra, _ = scorer.score_hypothesis(
        cluster=cluster,
        candidate_layer=CausalArchitecturalLayer.COMPOSITION,
        explains_signal_count=1,
        base_match_score=0.85,
        has_contradiction=True,
        contradiction_details="Measurement contradictory",
    )

    assert bd_contra.contradiction_penalty == scorer.config.max_contradiction_penalty
    assert score_clean - score_contra >= scorer.config.max_contradiction_penalty - 0.05


def test_25_ambiguity_detection_within_margin():
    """Test 25: When top hypotheses differ by <= 0.10, CausalDecision is MULTIPLE_PLAUSIBLE_CAUSES."""
    analyzer = CompetingHypothesisAnalyzer()

    h1 = RootCauseHypothesis(
        cause_code="LAYOUT_CAPACITY_EXCEEDED",
        cause_layer="COMPOSITION",
        confidence_score=0.82,
        affected_scope=FailureScope.LOCAL,
    )
    h2 = RootCauseHypothesis(
        cause_code="TYPOGRAPHY_SCALE_FAILURE",
        cause_layer="COMPOSITION",
        confidence_score=0.78,  # delta = 0.04 <= 0.10
        affected_scope=FailureScope.LOCAL,
    )

    result = analyzer.analyze([h1, h2])

    assert result.decision == CausalDecision.MULTIPLE_PLAUSIBLE_CAUSES
    assert result.is_ambiguous is True
    assert result.top_hypotheses_delta == pytest.approx(0.04, abs=0.001)


def test_26_authoritative_causal_decision_states():
    """Test 26: Competing analyzer produces distinct authoritative decisions for confirmed, likely, and insufficient."""
    analyzer = CompetingHypothesisAnalyzer()

    # Confirmed (>= 0.85 and clear winner)
    h_conf = RootCauseHypothesis(cause_code="A", cause_layer="COMPOSITION", confidence_score=0.88, affected_scope=FailureScope.LOCAL)
    res_conf = analyzer.analyze([h_conf])
    assert res_conf.decision == CausalDecision.ROOT_CAUSE_CONFIRMED

    # Likely (0.75 <= score < 0.85)
    h_likely = RootCauseHypothesis(cause_code="B", cause_layer="COMPOSITION", confidence_score=0.76, affected_scope=FailureScope.LOCAL)
    res_likely = analyzer.analyze([h_likely])
    assert res_likely.decision == CausalDecision.ROOT_CAUSE_LIKELY

    # Insufficient (< 0.35)
    h_low = RootCauseHypothesis(cause_code="C", cause_layer="COMPOSITION", confidence_score=0.25, affected_scope=FailureScope.LOCAL)
    res_low = analyzer.analyze([h_low])
    assert res_low.decision == CausalDecision.INSUFFICIENT_EVIDENCE


def test_27_explainable_causal_path_generation():
    """Test 27: Causal paths format an ASCII lineage chain showing how upstream defect reaches physical output."""
    steps = (
        (CausalArchitecturalLayer.TRANSFORMATION, "Content density uncompressed"),
        (CausalArchitecturalLayer.COMPOSITION, "Card slot capacity overflow"),
        (CausalArchitecturalLayer.RENDERING, "Text clipped at bottom boundary"),
    )
    path = CausalPath.from_steps(steps)
    chain = path.format_chain()
    assert "[TRANSFORMATION]" in chain
    assert "[COMPOSITION]" in chain
    assert "[RENDERING]" in chain
    assert "-->" in chain


def test_28_very_high_confidence_requires_invariants():
    """Test 28: A hypothesis with high score cannot achieve VERY_HIGH confidence if explanatory coverage is low or contradiction exists."""
    scorer = CausalEvidenceScorer()

    s1 = _make_signal("s1", CanonicalFailureCode.TEXT_CLIPPING)
    s2 = _make_signal("s2", CanonicalFailureCode.TEXT_TOO_SMALL)
    s3 = _make_signal("s3", CanonicalFailureCode.ELEMENT_COLLISION)
    cluster = _make_cluster([s1, s2, s3])

    # Explanatory coverage is only 1/3 (0.33) which is < min_explanatory_coverage_for_high (0.60)
    score, conf_level, _, notes = scorer.score_hypothesis(
        cluster=cluster,
        candidate_layer=CausalArchitecturalLayer.COMPOSITION,
        explains_signal_count=1,
        base_match_score=1.0,
    )

    assert conf_level != CausalConfidenceLevel.VERY_HIGH
    assert score < scorer.config.confidence_thresholds.very_high
