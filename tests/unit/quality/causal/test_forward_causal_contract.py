"""
Universal Document Intelligence System V5 — Forward Causal Contract Tests.

Phase 3A.2 Tests 33–36:
- Test 33: Forward-compatible RootCauseHypothesis schema
- Test 34: Forward-compatible FailureCluster schema
- Test 35: Clear contract boundary between detection signal and causal attribution
- Test 36: Backward compatibility with Phase 3A.1 UnifiedQualityAuthority and CanonicalFailure
"""

import pytest

from app.quality.causal.contracts import (
    CanonicalFailure,
    CanonicalQualityAssessment,
    FailureCluster,
    QualityLocation,
    QualitySignal,
    RootCauseHypothesis,
)
from app.quality.causal.provenance import (
    EvidenceReference,
    EvidenceSourceType,
)
from app.quality.causal.taxonomy import (
    ArchitectureLayer,
    CanonicalFailureCode,
    CanonicalFailureDomain,
    CanonicalRepairClass,
    CanonicalSeverity,
    CausalConfidence,
    FailureScope,
    UnifiedDecisionStatus,
)
from app.quality.causal.quality_authority import UnifiedQualityAuthority


def test_33_forward_compatible_root_cause_hypothesis_schema():
    """Test 33: RootCauseHypothesis schema validates attribution layer and repair bounds."""
    hyp = RootCauseHypothesis(
        cause_code="BLUEPRINT_CAPACITY_OVERLOAD",
        cause_layer=ArchitectureLayer.BLUEPRINT,
        confidence_score=0.92,
        confidence_level=CausalConfidence.HIGH,
        supporting_evidence=("High token count in beat 3", "2 clipped text blocks"),
        contradicting_evidence=(),
        affected_scope=FailureScope.LOCAL,
        repair_authority=ArchitectureLayer.BLUEPRINT,
        allowed_repair_classes=(CanonicalRepairClass.CLASS_D_BLUEPRINT_REGROUPING,),
        forbidden_repairs=("CLASS_A_GEOMETRY",),
    )

    assert hyp.hypothesis_id.startswith("hyp_")
    assert hyp.cause_layer == ArchitectureLayer.BLUEPRINT
    assert hyp.confidence_level == CausalConfidence.HIGH
    assert CanonicalRepairClass.CLASS_D_BLUEPRINT_REGROUPING in hyp.allowed_repair_classes
    assert "CLASS_A_GEOMETRY" in hyp.forbidden_repairs


def test_34_forward_compatible_failure_cluster_schema():
    """Test 34: FailureCluster schema groups co-occurring failures with root cause."""
    hyp = RootCauseHypothesis(
        cause_code="BLUEPRINT_CAPACITY_OVERLOAD",
        cause_layer=ArchitectureLayer.BLUEPRINT,
        confidence_score=0.85,
        confidence_level=CausalConfidence.HIGH,
        affected_scope=FailureScope.CLUSTER,
        repair_authority=ArchitectureLayer.BLUEPRINT,
    )

    cluster = FailureCluster(
        affected_pages=(2, 3),
        symptoms=(CanonicalFailureCode.TEXT_CLIPPING, CanonicalFailureCode.ELEMENT_COLLISION),
        primary_root_cause=hyp,
        recommended_repair_class=CanonicalRepairClass.CLASS_D_BLUEPRINT_REGROUPING,
        rationale="Shared blueprint beat causes multi-slide geometry overflow",
    )

    assert cluster.cluster_id.startswith("clust_")
    assert cluster.affected_pages == (2, 3)
    assert CanonicalFailureCode.TEXT_CLIPPING in cluster.symptoms
    assert cluster.primary_root_cause == hyp
    assert cluster.is_ambiguous is False


def test_35_clear_contract_boundary_separation():
    """Test 35: QualitySignal is pure detection; causal interpretation resides in hypothesis/cluster."""
    ev = EvidenceReference(
        source_type=EvidenceSourceType.PYMUPDF_GEOMETRY,
        description="Font size measured at 6.5pt",
        measurement="font_size_pt",
        raw_value=6.5,
        threshold=8.0,
        comparison_operator="<",
    )
    sig = QualitySignal(
        source_engine="geometry_inspector",
        failure_domain=CanonicalFailureDomain.PHYSICAL_RENDER,
        failure_code=CanonicalFailureCode.TEXT_TOO_SMALL,
        severity=CanonicalSeverity.MAJOR,
        location=QualityLocation(artifact_type="PRESENTATION", slide_index=1),
        evidence=(ev,),
    )

    # The signal purely states what is observed:
    assert sig.failure_domain == CanonicalFailureDomain.PHYSICAL_RENDER
    assert sig.failure_code == CanonicalFailureCode.TEXT_TOO_SMALL
    # It contains NO hypothesis:
    assert not hasattr(sig, "cause_layer")
    assert not hasattr(sig, "root_cause")

    # Hypothesis layer uses the signal as evidence:
    hyp = RootCauseHypothesis(
        cause_code="TYPOGRAPHY_SCALE_DEFICIT",
        cause_layer=ArchitectureLayer.TYPOGRAPHY,
        confidence_score=0.88,
        confidence_level=CausalConfidence.HIGH,
        supporting_evidence=(f"Signal {sig.signal_id}: {sig.description}",),
        affected_scope=FailureScope.LOCAL,
        repair_authority=ArchitectureLayer.TYPOGRAPHY,
    )
    assert hyp.cause_layer == ArchitectureLayer.TYPOGRAPHY
    assert sig.signal_id in hyp.supporting_evidence[0]


def test_36_backward_compatibility_with_phase_3a_1_quality_authority():
    """Test 36: UnifiedQualityAuthority works seamlessly with CanonicalFailure and CanonicalQualityAssessment."""
    ev = EvidenceReference(
        source_type=EvidenceSourceType.PYMUPDF_GEOMETRY,
        description="Text clipping 10pt",
        measurement="overflow_pt",
        raw_value=10.0,
    )
    sig = QualitySignal(
        source_engine="rendered_engine",
        failure_domain=CanonicalFailureDomain.PHYSICAL_RENDER,
        failure_code=CanonicalFailureCode.TEXT_CLIPPING,
        severity=CanonicalSeverity.MAJOR,
        location=QualityLocation(artifact_type="PRESENTATION", slide_index=2),
        evidence=(ev,),
    )

    cf = CanonicalFailure(
        failure_code=CanonicalFailureCode.TEXT_CLIPPING,
        artifact_type="PRESENTATION",
        affected_pages=(2,),
        severity=CanonicalSeverity.MAJOR,
        symptom="Text clipped outside bounding box",
        evidence_signals=(sig,),
        quality_dimension="PHYSICAL_RENDER",
        scope=FailureScope.LOCAL,
    )

    assessment = CanonicalQualityAssessment(
        artifact_type="PRESENTATION",
        page_count=5,
        overall_quality_score=0.85,
        failures=(cf,),
        decision=UnifiedDecisionStatus.PASS_WITH_WARNINGS,
        can_export=True,
        repair_required=False,
        manual_review_required=False,
        rationale="Local minor warning only",
    )

    assert assessment.decision == UnifiedDecisionStatus.PASS_WITH_WARNINGS
    assert len(assessment.failures) == 1
    assert assessment.failures[0].failure_code == CanonicalFailureCode.TEXT_CLIPPING
