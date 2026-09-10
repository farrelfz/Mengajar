"""
Universal Document Intelligence System V5 — Phase 3B Validator Anomaly Unit Tests.

Tests 29 to 31:
- Conflicting inspector measurements generate VALIDATOR_FALSE_POSITIVE hypothesis
- Validator anomaly hypothesis competes fairly with physical hypotheses
- Validator anomaly suspends automated repair and mandates MANUAL_REVIEW
"""

import pytest
from app.quality.causal.causal_taxonomy import (
    CausalArchitecturalLayer,
    CausalDecision,
    RootCauseCategory,
)
from app.quality.causal.competing_analysis import CompetingHypothesisAnalyzer
from app.quality.causal.contracts import FailureCluster, QualityLocation, QualitySignal, RootCauseHypothesis
from app.quality.causal.repair_readiness import RepairAuthorityLevel, RepairReadinessAssessor
from app.quality.causal.taxonomy import (
    CanonicalFailureCode,
    CanonicalFailureDomain,
    CanonicalSeverity,
    FailureScope,
)
from app.quality.causal.validator_anomaly import ValidatorAnomalyDetector


def _make_contradictory_signal(sig_id: str = "sig_contra") -> QualitySignal:
    return QualitySignal(
        signal_id=sig_id,
        source_engine="geometry_inspector",
        failure_domain=CanonicalFailureDomain.PHYSICAL_RENDER,
        failure_code=CanonicalFailureCode.TEXT_TOO_SMALL,
        severity=CanonicalSeverity.MAJOR,
        location=QualityLocation(
            artifact_type="PRESENTATION",
            page_index=1,
            element_id="title_heading",
        ),
        raw_metadata={
            "conflicting_dom_size": True,
            "raster_legible_override": True,
            "dom_font_size": 24.0,
            "measured_font_size": 6.0,
        },
        description="Inspector measured 6pt font but DOM explicitly declares 24pt title scale.",
    )


def test_29_conflicting_inspector_evidence_generates_anomaly_hypothesis():
    """Test 29: Conflicting measurements between DOM and raster create a VALIDATOR_FALSE_POSITIVE candidate."""
    detector = ValidatorAnomalyDetector()
    sig = _make_contradictory_signal("sig_anomaly_1")

    cluster = FailureCluster(
        cluster_id="clust_anomaly",
        affected_pages=(1,),
        symptoms=(CanonicalFailureCode.TEXT_TOO_SMALL,),
        signals=(sig,),
        scope=FailureScope.LOCAL,
        dominant_failure_patterns=("TEXT_TOO_SMALL",),
        affected_locations=(sig.location,),
        correlation_strength=0.90,
    )

    hyp = detector.detect_anomaly_hypothesis(cluster)

    assert hyp is not None
    assert hyp.cause_code == RootCauseCategory.VALIDATOR_FALSE_POSITIVE.value
    assert hyp.cause_layer == CausalArchitecturalLayer.VALIDATION.value
    assert any("contradicted" in ev for ev in hyp.supporting_evidence)


def test_30_anomaly_candidate_competes_fairly():
    """Test 30: When validator anomaly has higher confidence than physical cause, it wins the competition."""
    analyzer = CompetingHypothesisAnalyzer()

    h_physical = RootCauseHypothesis(
        cause_code="TYPOGRAPHY_SCALE_FAILURE",
        cause_layer="COMPOSITION",
        confidence_score=0.50,
        affected_scope=FailureScope.LOCAL,
    )
    h_anomaly = RootCauseHypothesis(
        cause_code=RootCauseCategory.VALIDATOR_FALSE_POSITIVE.value,
        cause_layer=CausalArchitecturalLayer.VALIDATION.value,
        confidence_score=0.70,
        affected_scope=FailureScope.LOCAL,
    )

    comp_res = analyzer.analyze([h_physical, h_anomaly])

    assert comp_res.primary_hypothesis == h_anomaly
    assert comp_res.decision == CausalDecision.ROOT_CAUSE_LIKELY


def test_31_anomaly_detection_mandates_manual_review():
    """Test 31: Suspected validator false positive strictly blocks automatic repairs and recommends MANUAL_REVIEW."""
    assessor = RepairReadinessAssessor()
    analyzer = CompetingHypothesisAnalyzer()

    sig = _make_contradictory_signal("sig_31")
    cluster = FailureCluster(
        cluster_id="clust_31",
        affected_pages=(1,),
        symptoms=(CanonicalFailureCode.TEXT_TOO_SMALL,),
        signals=(sig,),
        scope=FailureScope.LOCAL,
    )

    h_anomaly = RootCauseHypothesis(
        cause_code=RootCauseCategory.VALIDATOR_FALSE_POSITIVE.value,
        cause_layer=CausalArchitecturalLayer.VALIDATION.value,
        confidence_score=0.75,
        affected_scope=FailureScope.LOCAL,
    )

    comp_res = analyzer.analyze([h_anomaly])
    # Set decision to VALIDATOR_ANOMALY_SUSPECTED explicitly
    comp_res.decision = CausalDecision.VALIDATOR_ANOMALY_SUSPECTED

    readiness = assessor.assess(cluster, comp_res, total_pages=5)

    assert readiness.recommended_authority == RepairAuthorityLevel.MANUAL_REVIEW
    assert readiness.is_repair_ready() is False
    assert any("validator" in r.lower() for r in readiness.blocking_reasons)
