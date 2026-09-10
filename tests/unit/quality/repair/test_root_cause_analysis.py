"""
Unit tests for deterministic root cause analysis and symptom vs cause separation.
"""

from app.quality.contracts.findings import FindingCluster, QualityFinding, SignalSeverity
from app.quality.repair.contracts import RepairMutationClass
from app.quality.repair.root_cause import DeterministicRootCauseAnalyzer, RootCauseType


def test_text_clipping_density_vs_padding():
    # 1. Overflow with high occupancy -> CONTENT_DENSITY
    f1 = QualityFinding(
        failure_code="TEXT_OVERFLOW",
        message="Text clipped on slide 3",
        severity=SignalSeverity.ERROR,
        affected_pages=(3,),
    )
    hyps_density = DeterministicRootCauseAnalyzer.analyze(
        [f1], metrics={"occupancy": 0.94}, artifact_type="PRESENTATION"
    )
    assert len(hyps_density) == 1
    assert hyps_density[0].cause_type == RootCauseType.CONTENT_DENSITY
    assert hyps_density[0].suggested_mutation_class == RepairMutationClass.CLASS_B_COMPOSITION

    # 2. Overflow with moderate occupancy -> PADDING_SPACING
    hyps_padding = DeterministicRootCauseAnalyzer.analyze(
        [f1], metrics={"occupancy": 0.70}, artifact_type="PRESENTATION"
    )
    assert len(hyps_padding) == 1
    assert hyps_padding[0].cause_type == RootCauseType.PADDING_SPACING
    assert hyps_padding[0].suggested_mutation_class == RepairMutationClass.CLASS_A_GEOMETRY


def test_tiny_text_in_dense_cluster_identifies_density_as_cause():
    f_tiny = QualityFinding(failure_code="FONT_TOO_SMALL", severity=SignalSeverity.WARNING, affected_pages=(1,))
    f_over = QualityFinding(failure_code="TEXT_OVERFLOW", severity=SignalSeverity.ERROR, affected_pages=(1,))

    cluster = FindingCluster(
        canonical_finding=f_over,
        correlated_findings=(f_tiny,),
        affected_pages=(1,),
    )

    hyps = DeterministicRootCauseAnalyzer.analyze(
        findings=[f_over, f_tiny],
        clusters=[cluster],
        metrics={"occupancy": 0.89},
        artifact_type="PRESENTATION",
    )
    assert len(hyps) == 1
    # Crucial architectural assertion: cause is density, not typography!
    assert hyps[0].cause_type == RootCauseType.CONTENT_DENSITY


def test_inquiry_arc_and_anti_spoiling_root_cause():
    f_spoil = QualityFinding(
        failure_code="ANTI_SPOILING_BREACH",
        message="Explanation leaked in prediction activity",
        severity=SignalSeverity.ERROR,
    )
    hyps = DeterministicRootCauseAnalyzer.analyze([f_spoil], artifact_type="WORKSHEET")
    assert len(hyps) == 1
    assert hyps[0].cause_type == RootCauseType.INQUIRY_STRUCTURE
    assert hyps[0].suggested_mutation_class == RepairMutationClass.CLASS_D_PEDAGOGICAL_STRUCTURE


def test_scientific_unsupported_claim_vs_contradiction():
    f_claim = QualityFinding(
        failure_code="UNSUPPORTED_SCIENTIFIC_CLAIM",
        message="Claim without verified empirical evidence",
        severity=SignalSeverity.ERROR,
    )
    hyps_claim = DeterministicRootCauseAnalyzer.analyze([f_claim], artifact_type="SCIENTIFIC_DOCUMENT")
    assert hyps_claim[0].cause_type == RootCauseType.EVIDENCE_MAPPING
    assert hyps_claim[0].repairability is True

    # Contradiction cannot be auto-repaired!
    f_conflict = QualityFinding(
        failure_code="SOURCE_CONTRADICTION",
        message="Conflicting source evidence detected",
        severity=SignalSeverity.BLOCKING,
    )
    hyps_conflict = DeterministicRootCauseAnalyzer.analyze([f_conflict], artifact_type="SCIENTIFIC_DOCUMENT")
    assert hyps_conflict[0].cause_type == RootCauseType.SOURCE_INSUFFICIENCY
    assert hyps_conflict[0].repairability is False
    assert hyps_conflict[0].suggested_mutation_class == RepairMutationClass.CLASS_F_NON_REPAIRABLE
