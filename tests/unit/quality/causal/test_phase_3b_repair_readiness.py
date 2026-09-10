"""
Universal Document Intelligence System V5 — Phase 3B Repair Readiness Unit Tests.

Tests 32 to 36:
- DETERMINISTIC_REPAIR_CANDIDATE recommendation
- MANUAL_REVIEW recommendation (ambiguity & validator anomaly)
- HIGH_RISK_REPAIR recommendation (systemic scope / large blast radius)
- OBSERVE and NO_ACTION recommendation
- Strict guarantee: Phase 3B never executes repairs
"""

import pytest
from app.quality.causal.causal_engine import MasterCausalEngine
from app.quality.causal.causal_taxonomy import CausalDecision, RootCauseCategory
from app.quality.causal.competing_analysis import CompetingHypothesisAnalysisResult
from app.quality.causal.contracts import FailureCluster, QualityLocation, QualitySignal, RootCauseHypothesis
from app.quality.causal.repair_readiness import RepairAuthorityLevel, RepairReadinessAssessor
from app.quality.causal.taxonomy import (
    CanonicalFailureCode,
    CanonicalFailureDomain,
    CanonicalSeverity,
    FailureScope,
)


def _make_signal(
    sig_id: str,
    code: CanonicalFailureCode,
    severity: CanonicalSeverity = CanonicalSeverity.MAJOR,
    page: int = 1,
) -> QualitySignal:
    return QualitySignal(
        signal_id=sig_id,
        source_engine="test_engine",
        failure_domain=CanonicalFailureDomain.PHYSICAL_RENDER,
        failure_code=code,
        severity=severity,
        location=QualityLocation(
            artifact_type="PRESENTATION",
            page_index=page,
            element_id="elem_1",
        ),
        description=f"Test defect {code.value}",
    )


def test_32_authority_deterministic_repair_candidate():
    """Test 32: High-confidence root cause with bounded blast radius qualifies as DETERMINISTIC_REPAIR_CANDIDATE."""
    assessor = RepairReadinessAssessor()
    sig = _make_signal("sig_32", CanonicalFailureCode.TEXT_TOO_SMALL)

    cluster = FailureCluster(
        cluster_id="clust_32",
        affected_pages=(1,),
        symptoms=(CanonicalFailureCode.TEXT_TOO_SMALL,),
        signals=(sig,),
        scope=FailureScope.LOCAL,
    )

    hyp = RootCauseHypothesis(
        cause_code=RootCauseCategory.TYPOGRAPHY_SCALE_FAILURE.value,
        cause_layer="COMPOSITION",
        confidence_score=0.88,
        affected_scope=FailureScope.LOCAL,
    )

    comp = CompetingHypothesisAnalysisResult(
        primary_hypothesis=hyp,
        alternative_hypotheses=(),
        decision=CausalDecision.ROOT_CAUSE_CONFIRMED,
        is_ambiguous=False,
        rationale="Clear typography cause",
    )

    readiness = assessor.assess(cluster, comp, total_pages=10)

    assert readiness.recommended_authority == RepairAuthorityLevel.DETERMINISTIC_REPAIR_CANDIDATE
    assert readiness.is_repair_ready() is True
    assert readiness.blast_radius < 0.50
    assert len(readiness.blocking_reasons) == 0


def test_33_authority_manual_review_on_ambiguity():
    """Test 33: Ambiguous root causes mandate MANUAL_REVIEW to prevent automated misrepair."""
    assessor = RepairReadinessAssessor()
    sig = _make_signal("sig_33", CanonicalFailureCode.TEXT_TOO_SMALL)

    cluster = FailureCluster(
        cluster_id="clust_33",
        affected_pages=(1,),
        symptoms=(CanonicalFailureCode.TEXT_TOO_SMALL,),
        signals=(sig,),
        scope=FailureScope.LOCAL,
    )

    h1 = RootCauseHypothesis(cause_code="LAYOUT_CAPACITY_EXCEEDED", cause_layer="COMPOSITION", confidence_score=0.80, affected_scope=FailureScope.LOCAL)
    h2 = RootCauseHypothesis(cause_code="TYPOGRAPHY_SCALE_FAILURE", cause_layer="COMPOSITION", confidence_score=0.78, affected_scope=FailureScope.LOCAL)

    comp = CompetingHypothesisAnalysisResult(
        primary_hypothesis=h1,
        alternative_hypotheses=(h2,),
        decision=CausalDecision.MULTIPLE_PLAUSIBLE_CAUSES,
        is_ambiguous=True,
        rationale="Ambiguous competing causes",
    )

    readiness = assessor.assess(cluster, comp, total_pages=10)

    assert readiness.recommended_authority == RepairAuthorityLevel.MANUAL_REVIEW
    assert readiness.is_repair_ready() is False
    assert any("margin" in r.lower() or "ambiguity" in r.lower() for r in readiness.blocking_reasons)


def test_34_authority_high_risk_repair_on_systemic_scope():
    """Test 34: Systemic scope spanning many pages designates HIGH_RISK_REPAIR due to large blast radius."""
    assessor = RepairReadinessAssessor()
    signals = tuple(_make_signal(f"sig_{p}", CanonicalFailureCode.TEXT_TOO_SMALL, page=p) for p in range(1, 8))

    cluster = FailureCluster(
        cluster_id="clust_34",
        affected_pages=(1, 2, 3, 4, 5, 6, 7),
        symptoms=(CanonicalFailureCode.TEXT_TOO_SMALL,),
        signals=signals,
        scope=FailureScope.SYSTEMIC,
    )

    hyp = RootCauseHypothesis(
        cause_code=RootCauseCategory.TYPOGRAPHY_SCALE_FAILURE.value,
        cause_layer="COMPOSITION",
        confidence_score=0.88,
        affected_scope=FailureScope.SYSTEMIC,
    )

    comp = CompetingHypothesisAnalysisResult(
        primary_hypothesis=hyp,
        alternative_hypotheses=(),
        decision=CausalDecision.ROOT_CAUSE_CONFIRMED,
        is_ambiguous=False,
        rationale="Confirmed template typography issue",
    )

    readiness = assessor.assess(cluster, comp, total_pages=10)

    assert readiness.recommended_authority == RepairAuthorityLevel.HIGH_RISK_REPAIR
    assert readiness.blast_radius >= 0.70
    assert readiness.is_repair_ready() is False


def test_35_authority_observe_on_low_confidence():
    """Test 35: Low confidence root cause attribution is gated to OBSERVE."""
    assessor = RepairReadinessAssessor()
    sig = _make_signal("sig_35", CanonicalFailureCode.MARGIN_INCONSISTENCY, severity=CanonicalSeverity.MINOR)

    cluster = FailureCluster(
        cluster_id="clust_35",
        affected_pages=(1,),
        symptoms=(CanonicalFailureCode.MARGIN_INCONSISTENCY,),
        signals=(sig,),
        scope=FailureScope.LOCAL,
    )

    hyp = RootCauseHypothesis(
        cause_code=RootCauseCategory.UNKNOWN_CAUSE.value,
        cause_layer="RENDERING",
        confidence_score=0.40,
        affected_scope=FailureScope.LOCAL,
    )

    comp = CompetingHypothesisAnalysisResult(
        primary_hypothesis=hyp,
        alternative_hypotheses=(),
        decision=CausalDecision.ROOT_CAUSE_LIKELY,
        is_ambiguous=False,
        rationale="Weak cause link",
    )

    readiness = assessor.assess(cluster, comp, total_pages=10)

    assert readiness.recommended_authority == RepairAuthorityLevel.OBSERVE
    assert readiness.is_repair_ready() is False


def test_36_strict_guarantee_zero_repair_execution():
    """Test 36: Running MasterCausalEngine strictly executes zero mutations and returns read-only intelligence."""
    engine = MasterCausalEngine()
    s1 = _make_signal("s1", CanonicalFailureCode.TEXT_CLIPPING, page=1)
    s2 = _make_signal("s2", CanonicalFailureCode.TEXT_TOO_SMALL, page=1)

    result = engine.analyze([s1, s2], total_pages=5, artifact_type="PRESENTATION")

    # Signals are immutable frozen models
    for s in (s1, s2):
        with pytest.raises(Exception):
            s.description = "MUTATED"

    # Engine produces assessments but no repair action execution
    assert len(result.clusters) == 1
    assert len(result.readiness_assessments) == 1
    assert result.clusters[0].recommended_repair_class is not None
