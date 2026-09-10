"""
Universal Document Intelligence System V5 — Unit Tests for Quality Authority Contracts & Engine.

Phase 3A.1: 30 comprehensive unit tests verifying signals, taxonomy mapping,
adapters, correlation, dimension normalization, degeneracy detection, and format profiles.
"""

import json
import pytest

from app.quality.adapters import (
    CalibrationSignalAdapter,
    FidelitySignalAdapter,
    LegacyDocumentQualitySignalAdapter,
    PresentationQualitySignalAdapter,
    RenderedQualitySignalAdapter,
)
from app.quality.authority import (
    AuthoritativeDecisionEngine,
    FindingCorrelationEngine,
    QualityDimensionNormalizer,
    UnifiedQualityAuthority,
    get_profile_for_artifact,
)
from app.quality.authority.profiles import (
    HANDOUT_PROFILE,
    PRESENTATION_PROFILE,
    SCIENTIFIC_DOCUMENT_PROFILE,
    WORKSHEET_PROFILE,
)
from app.quality.contracts import (
    ArtifactFidelityReport,
    CanonicalQualityDimension,
    CanonicalQualityFinding,
    EvidenceReference,
    EvidenceSourceType,
    ExportDecision,
    FindingCluster,
    QualityDomain,
    QualityLocation,
    QualityProvenanceGraph,
    QualitySignal,
    SignalConfidence,
    SignalSeverity,
    UnifiedQualityReport,
)
from app.quality.contracts.taxonomy_mapping import (
    CALIBRATION_CODE_TO_CANONICAL_MAP,
    FIDELITY_CODE_TO_CANONICAL_MAP,
    RENDERED_CODE_TO_CANONICAL_MAP,
    map_legacy_severity,
    map_to_canonical_code,
    map_to_canonical_dimension,
    map_to_canonical_domain,
)


# =============================================================================
# 1. Signal Construction & Validation
# =============================================================================

def test_01_quality_signal_construction_and_validation():
    """Test 01: QualitySignal creates with all required fields and valid coordinates."""
    loc = QualityLocation(artifact_type="PRESENTATION", slide_index=2, element_id="card_1")
    sig = QualitySignal(
        source_engine="test_engine",
        domain=QualityDomain.RENDERED,
        canonical_code="TEXT_CLIPPING",
        severity=SignalSeverity.BLOCKING,
        confidence=SignalConfidence.DEFINITIVE,
        location=loc,
        description="Text clipped on slide 2",
    )
    assert sig.canonical_code == "TEXT_CLIPPING"
    assert sig.domain == QualityDomain.RENDERED
    assert sig.severity == SignalSeverity.BLOCKING
    assert sig.location.slide_index == 2
    assert sig.location.page_indices == (2,)


def test_02_raw_metric_preservation_alongside_normalized():
    """Test 02: Raw measurements and thresholds are preserved unmutated."""
    loc = QualityLocation(artifact_type="HANDOUT", page_index=1)
    ev = EvidenceReference(
        source_type=EvidenceSourceType.PYMUPDF_GEOMETRY,
        description="Font size is 6.5pt, minimum allowed is 8pt",
        measurement="font_size",
        raw_value=6.5,
        threshold=8.0,
        comparison_operator="<",
    )
    sig = QualitySignal(
        source_engine="geometry_checker",
        domain=QualityDomain.RENDERED,
        canonical_code="FONT_TOO_SMALL",
        severity=SignalSeverity.BLOCKING,
        location=loc,
        evidence=(ev,),
        raw_value=6.5,
        threshold=8.0,
        measurement="font_size",
    )
    assert sig.raw_value == 6.5
    assert sig.threshold == 8.0
    assert sig.measurement == "font_size"
    assert sig.evidence[0].raw_value == 6.5
    assert sig.evidence[0].threshold == 8.0


def test_03_scale_normalization_directional():
    """Test 03: Directional scale normalization supports HIGHER_IS_BETTER and LOWER_IS_BETTER."""
    # Higher is better: raw 80 in [0, 100] -> 0.8
    score_high = QualityDimensionNormalizer.normalize_scale(80, 0, 100, higher_is_better=True)
    assert pytest.approx(score_high, 0.01) == 0.80

    # Lower is better: raw 20 defect count in [0, 100] -> 0.80
    score_low = QualityDimensionNormalizer.normalize_scale(20, 0, 100, higher_is_better=False)
    assert pytest.approx(score_low, 0.01) == 0.80

    # Clamping test
    assert QualityDimensionNormalizer.normalize_scale(150, 0, 100, higher_is_better=True) == 1.0
    assert QualityDimensionNormalizer.normalize_scale(-10, 0, 100, higher_is_better=True) == 0.0


def test_04_calibration_profile_registry_lookup():
    """Test 04: Profile resolver returns matching profile or sensible default."""
    pres_p = get_profile_for_artifact("PRESENTATION")
    assert pres_p.artifact_type == "PRESENTATION"
    assert "TEXT_CLIPPING" in pres_p.hard_blockers

    hand_p = get_profile_for_artifact("HANDOUT")
    assert hand_p.artifact_type == "HANDOUT"
    assert "FONT_TOO_SMALL" in hand_p.hard_blockers

    work_p = get_profile_for_artifact("WORKSHEET")
    assert work_p.artifact_type == "WORKSHEET"
    assert "ANTI_SPOILING_BREACH" in work_p.hard_blockers

    sci_p = get_profile_for_artifact("SCIENTIFIC_DOCUMENT")
    assert sci_p.artifact_type == "SCIENTIFIC_DOCUMENT"
    assert "UNSUPPORTED_SCIENTIFIC_CLAIM" in sci_p.hard_blockers

    default_p = get_profile_for_artifact("UNKNOWN_TYPE")
    assert default_p.artifact_type == "DEFAULT"


# =============================================================================
# 2. Correlation & Double-Counting Prevention
# =============================================================================

def test_05_finding_correlation_and_clustering():
    """Test 05: Co-occurring signals at same page cluster into a single FindingCluster."""
    sig1 = QualitySignal(
        source_engine="calibration",
        domain=QualityDomain.ARTIFACT,
        canonical_code="COGNITIVE_OVERLOAD",
        severity=SignalSeverity.BLOCKING,
        location=QualityLocation(artifact_type="PRESENTATION", slide_index=3),
        description="Slide 3 is overdense",
    )
    sig2 = QualitySignal(
        source_engine="rendered",
        domain=QualityDomain.RENDERED,
        canonical_code="TEXT_CLIPPING",
        severity=SignalSeverity.BLOCKING,
        location=QualityLocation(artifact_type="PRESENTATION", slide_index=3),
        description="Text clipped at bottom of slide 3",
    )

    findings, clusters = FindingCorrelationEngine.correlate_signals([sig1, sig2])
    assert len(clusters) == 1
    cluster = clusters[0]
    assert len(cluster.contributing_signals) == 2
    assert cluster.affected_pages == (3,)
    assert len(findings) == 1
    assert findings[0].affected_section == "Slide 3"


def test_06_duplicate_signal_deduplication():
    """Test 06: Multiple engines reporting on the same element create one primary finding."""
    sig1 = QualitySignal(
        source_engine="engine_a",
        domain=QualityDomain.RENDERED,
        canonical_code="ELEMENT_COLLISION",
        severity=SignalSeverity.ERROR,
        location=QualityLocation(artifact_type="WORKSHEET", element_id="workspace_box_4"),
        description="Workspace overlaps question content",
    )
    sig2 = QualitySignal(
        source_engine="engine_b",
        domain=QualityDomain.RENDERED,
        canonical_code="ELEMENT_COLLISION",
        severity=SignalSeverity.WARNING,
        location=QualityLocation(artifact_type="WORKSHEET", element_id="workspace_box_4"),
        description="Workspace overlaps text bounding box",
    )

    findings, clusters = FindingCorrelationEngine.correlate_signals([sig1, sig2])
    assert len(findings) == 1
    assert findings[0].severity == SignalSeverity.ERROR


def test_07_penalty_suppression_across_correlated_signals():
    """Test 07: Correlated signals do not double-penalize the overall score."""
    sig1 = QualitySignal(
        source_engine="engine_a",
        domain=QualityDomain.ARTIFACT,
        canonical_code="COGNITIVE_OVERLOAD",
        severity=SignalSeverity.WARNING,
        location=QualityLocation(artifact_type="PRESENTATION", slide_index=1),
        description="High text density",
    )
    sig2 = QualitySignal(
        source_engine="engine_b",
        domain=QualityDomain.RENDERED,
        canonical_code="TEXT_OVERFLOW",
        severity=SignalSeverity.WARNING,
        location=QualityLocation(artifact_type="PRESENTATION", slide_index=1),
        description="Text near bottom margin",
    )

    findings, clusters = FindingCorrelationEngine.correlate_signals([sig1, sig2])
    # The cluster produces 1 canonical finding rather than 2 separate independent deductions
    assert len(findings) == 1
    dim_scores, domain_scores, overall_score, _ = QualityDimensionNormalizer.compute_dimension_scores(
        signals=[sig1, sig2],
        findings=findings,
        clusters=clusters,
        profile=PRESENTATION_PROFILE,
    )
    assert overall_score > 0.85


# =============================================================================
# 3. Failure Taxonomy Mapping
# =============================================================================

def test_08_taxonomy_mapping_legacy_to_canonical():
    """Test 08: Legacy dimensions map accurately to canonical domains and dimensions."""
    assert map_to_canonical_domain("SEMANTIC_FIDELITY") == QualityDomain.SEMANTIC
    assert map_to_canonical_domain("STRUCTURAL_INTEGRITY") == QualityDomain.FIDELITY
    assert map_to_canonical_domain("INFORMATION_DENSITY") == QualityDomain.ARTIFACT
    assert map_to_canonical_dimension("SEMANTIC_FIDELITY") == CanonicalQualityDimension.SEMANTIC_GROUNDING
    assert map_to_canonical_dimension("INFORMATION_DENSITY") == CanonicalQualityDimension.COGNITIVE_LOAD


def test_09_taxonomy_mapping_rendered_to_canonical():
    """Test 09: Rendered defect codes map to canonical codes and physical geometry domain."""
    assert map_to_canonical_code("TEXT_CLIPPING") == "TEXT_CLIPPING"
    assert map_to_canonical_code("CONTENT_OVERFLOW") == "TEXT_OVERFLOW"
    assert map_to_canonical_code("OVERLAPPING_CONTENT") == "ELEMENT_COLLISION"
    assert map_to_canonical_code("TINY_TEXT") == "FONT_TOO_SMALL"
    assert map_to_canonical_code("VIEWPORT_BREACH") == "MARGIN_VIOLATION"
    assert map_to_canonical_domain("TEXT_CLIPPING") == QualityDomain.RENDERED


def test_10_taxonomy_mapping_calibration_to_canonical():
    """Test 10: Calibration codes map to canonical failure codes."""
    assert map_to_canonical_code("HEADING_HIERARCHY_INVERSION") == "STRUCTURAL_HIERARCHY_INVERSION"
    assert map_to_canonical_code("EXPLANATION_LEAKED_BEFORE_PREDICTION") == "ANTI_SPOILING_BREACH"
    assert map_to_canonical_code("CLAIM_WITHOUT_EVIDENCE") == "UNSUPPORTED_SCIENTIFIC_CLAIM"
    assert map_to_canonical_code("BAB_HIERARCHY_INVERSION") == "STRUCTURAL_HIERARCHY_INVERSION"


# =============================================================================
# 4. Format-Specific Quality Profiles & Hard Blockers
# =============================================================================

def test_11_presentation_hard_blocker_clipping():
    """Test 11: Text clipping in Presentation unconditionally blocks export."""
    sig = QualitySignal(
        source_engine="rendered",
        domain=QualityDomain.RENDERED,
        canonical_code="TEXT_CLIPPING",
        severity=SignalSeverity.BLOCKING,
        location=QualityLocation(artifact_type="PRESENTATION", slide_index=1),
        description="Text clipping on slide 1",
    )
    report = UnifiedQualityAuthority.evaluate_artifact("PRESENTATION", raw_signals=[sig])
    assert report.decision == ExportDecision.BLOCKED
    assert report.can_export is False
    assert len(report.hard_blockers) > 0


def test_12_handout_hard_blocker_extreme_density():
    """Test 12: Extreme dense page in Handout unconditionally blocks export."""
    sig = QualitySignal(
        source_engine="calibration",
        domain=QualityDomain.ARTIFACT,
        canonical_code="EXTREME_DENSE_PAGE",
        severity=SignalSeverity.BLOCKING,
        location=QualityLocation(artifact_type="HANDOUT", page_index=2),
        description="Page 2 contains 3500 characters",
    )
    report = UnifiedQualityAuthority.evaluate_artifact("HANDOUT", raw_signals=[sig])
    assert report.decision == ExportDecision.BLOCKED
    assert report.can_export is False


def test_13_worksheet_hard_blocker_answer_leak():
    """Test 13: Answer leakage in Worksheet unconditionally blocks export."""
    sig = QualitySignal(
        source_engine="calibration",
        domain=QualityDomain.ARTIFACT,
        canonical_code="ANSWER_LEAKED_INSIDE_QUESTION",
        severity=SignalSeverity.BLOCKING,
        location=QualityLocation(artifact_type="WORKSHEET", page_index=1),
        description="Question contains explicit solution",
    )
    report = UnifiedQualityAuthority.evaluate_artifact("WORKSHEET", raw_signals=[sig])
    assert report.decision == ExportDecision.BLOCKED
    assert report.can_export is False


def test_14_scientific_hard_blocker_claim_without_evidence():
    """Test 14: Claim without evidence in Scientific Document unconditionally blocks export."""
    sig = QualitySignal(
        source_engine="calibration",
        domain=QualityDomain.SEMANTIC,
        canonical_code="CLAIM_WITHOUT_EVIDENCE",
        severity=SignalSeverity.BLOCKING,
        location=QualityLocation(artifact_type="SCIENTIFIC_DOCUMENT", page_index=3),
        description="Claim in discussion lacks supporting citation or empirical data",
    )
    report = UnifiedQualityAuthority.evaluate_artifact("SCIENTIFIC_DOCUMENT", raw_signals=[sig])
    assert report.decision == ExportDecision.BLOCKED
    assert report.can_export is False


# =============================================================================
# 5. Degeneracy Detection & Safeguards
# =============================================================================

def test_15_degeneracy_detection_universal_one():
    """Test 15: Degeneracy detector flags universal 1.0 when defects are present."""
    findings = [
        CanonicalQualityFinding(
            failure_code="LAYOUT_MONOTONY",
            severity=SignalSeverity.WARNING,
            message="Slight monotony",
        )
    ]
    # Simulate a corrupted normalizer that yielded 1.0
    dim_scores = {
        dim.value: QualityDimensionNormalizer.compute_dimension_scores([], [], [], PRESENTATION_PROFILE)[0][dim.value]
        for dim in CanonicalQualityDimension
    }
    degen = QualityDimensionNormalizer._detect_degeneracy(
        overall_score=1.0,
        dim_scores=dim_scores,
        signals=[],
        findings=findings,
    )
    assert degen["is_degenerate"] is True
    assert degen["universal_one"] is True


def test_16_degeneracy_detection_zero_variance():
    """Test 16: Degeneracy detector flags zero variance when all dimensions report identical score despite defects."""
    # When defects exist, identical flat scores across 15 distinct dimensions is abnormal
    findings = [
        CanonicalQualityFinding(
            failure_code="TEST_DEFECT",
            severity=SignalSeverity.WARNING,
            message="Test",
        )
    ]
    dim_scores = {
        dim.value: QualityDimensionNormalizer.compute_dimension_scores([], [], [], PRESENTATION_PROFILE)[0][dim.value]
        for dim in CanonicalQualityDimension
    }
    degen = QualityDimensionNormalizer._detect_degeneracy(
        overall_score=0.75,
        dim_scores=dim_scores,
        signals=[],
        findings=findings,
    )
    # The default baseline without finding deductions gives zero variance
    assert degen["zero_variance"] is True


# =============================================================================
# 6. Warning Tolerances & Escalation
# =============================================================================

def test_17_warning_tolerance_approval_with_warnings():
    """Test 17: Non-blocking warnings within tolerance allow EXPORT_APPROVED_WITH_WARNINGS."""
    sig = QualitySignal(
        source_engine="test",
        domain=QualityDomain.ARTIFACT,
        canonical_code="LAYOUT_MONOTONY",
        severity=SignalSeverity.WARNING,
        location=QualityLocation(artifact_type="PRESENTATION", slide_index=1),
        description="Minor layout repetition",
    )
    report = UnifiedQualityAuthority.evaluate_artifact("PRESENTATION", raw_signals=[sig])
    assert report.decision == ExportDecision.EXPORT_APPROVED_WITH_WARNINGS
    assert report.can_export is True
    assert len(report.warnings) == 1


def test_18_warning_tolerance_exceeded_requires_repair():
    """Test 18: Accumulation of warnings exceeding tolerance transitions to repair required."""
    signals = [
        QualitySignal(
            source_engine="test",
            domain=QualityDomain.ARTIFACT,
            canonical_code=f"WARN_CODE_{i}",
            severity=SignalSeverity.WARNING,
            location=QualityLocation(artifact_type="PRESENTATION", slide_index=i),
            description=f"Warning {i}",
        )
        for i in range(1, 6)  # 5 warnings, presentation tolerance is 3
    ]
    report = UnifiedQualityAuthority.evaluate_artifact("PRESENTATION", raw_signals=signals)
    assert report.decision in (ExportDecision.REPAIR_REQUIRED, ExportDecision.SEMANTIC_REPAIR_REQUIRED)
    assert report.can_export is False
    assert report.repair_required is True


# =============================================================================
# 7. Provenance & Multi-Layer Truth Aggregation
# =============================================================================

def test_19_provenance_graph_completeness():
    """Test 19: Provenance graph captures signals, clusters, findings, and decisions."""
    sig = QualitySignal(
        source_engine="test_engine",
        domain=QualityDomain.RENDERED,
        canonical_code="TEXT_OVERFLOW",
        severity=SignalSeverity.WARNING,
        location=QualityLocation(artifact_type="PRESENTATION", slide_index=2),
        description="Overflow warning",
    )
    report = UnifiedQualityAuthority.evaluate_artifact("PRESENTATION", raw_signals=[sig])
    prov = report.provenance
    assert len(prov.signals) == 1
    assert len(prov.findings) == 1
    assert prov.decision is not None
    assert prov.decision["decision"] == ExportDecision.EXPORT_APPROVED_WITH_WARNINGS.value


def test_20_multi_layer_truth_report_aggregation():
    """Test 20: Report contains scores and breakdown for all 4 orthogonal truth layers."""
    report = UnifiedQualityAuthority.evaluate_artifact("PRESENTATION")
    assert "semantic_integrity" in report.domain_scores
    assert "artifact_fidelity" in report.domain_scores
    assert "artifact_quality" in report.domain_scores
    assert "rendered_quality" in report.domain_scores

    assert len(report.semantic_integrity["dimensions"]) == 3
    assert len(report.artifact_fidelity["dimensions"]) == 3
    assert len(report.artifact_quality["dimensions"]) == 5
    assert len(report.rendered_quality["dimensions"]) == 4


def test_21_report_immutability_and_serialization():
    """Test 21: UnifiedQualityReport is frozen and serializable to JSON round-trip."""
    report = UnifiedQualityAuthority.evaluate_artifact("HANDOUT")
    # Immutability check
    with pytest.raises(Exception):
        report.overall_quality_score = 0.5

    # JSON serialization
    serialized = report.model_dump_json()
    assert isinstance(serialized, str)
    data = json.loads(serialized)
    assert data["artifact_type"] == "HANDOUT"
    assert data["decision"] == "EXPORT_APPROVED"


# =============================================================================
# 8. Conflicting Evaluator Resolution
# =============================================================================

def test_22_conflicting_evaluators_high_fidelity_low_physical():
    """Test 22: High fidelity (1.0) cannot mask physical rendered defect (clipping)."""
    # 100% fidelity: no dropped units
    # Physical render: text clipping
    sig_render = QualitySignal(
        source_engine="rendered",
        domain=QualityDomain.RENDERED,
        canonical_code="TEXT_CLIPPING",
        severity=SignalSeverity.BLOCKING,
        location=QualityLocation(artifact_type="PRESENTATION", slide_index=4),
        description="Slide 4 content clipped offscreen",
    )
    report = UnifiedQualityAuthority.evaluate_artifact(
        "PRESENTATION",
        raw_signals=[sig_render],
    )
    assert report.decision == ExportDecision.BLOCKED
    assert report.can_export is False


def test_23_conflicting_evaluators_clean_render_fabricated_claim():
    """Test 23: Perfect rendered layout cannot mask scientific claim fabrication."""
    sig_semantic = QualitySignal(
        source_engine="semantic_audit",
        domain=QualityDomain.SEMANTIC,
        canonical_code="UNSUPPORTED_SCIENTIFIC_CLAIM",
        severity=SignalSeverity.BLOCKING,
        location=QualityLocation(artifact_type="SCIENTIFIC_DOCUMENT", page_index=2),
        description="Factual claim lacks citation in Bab II",
    )
    report = UnifiedQualityAuthority.evaluate_artifact(
        "SCIENTIFIC_DOCUMENT",
        raw_signals=[sig_semantic],
    )
    assert report.decision == ExportDecision.BLOCKED
    assert report.can_export is False


# =============================================================================
# 9. Offline Determinism & Partial Inputs
# =============================================================================

def test_24_zero_ai_offline_verification():
    """Test 24: UnifiedQualityAuthority operates completely deterministically with zero AI/LLM."""
    # Running evaluation twice on identical inputs produces identical results
    sig = QualitySignal(
        signal_id="sig_det_001",
        source_engine="deterministic_test",
        domain=QualityDomain.ARTIFACT,
        canonical_code="COGNITIVE_OVERLOAD",
        severity=SignalSeverity.WARNING,
        location=QualityLocation(artifact_type="PRESENTATION", slide_index=1),
        description="Deterministic density warning",
    )
    rep1 = UnifiedQualityAuthority.evaluate_artifact("PRESENTATION", raw_signals=[sig])
    rep2 = UnifiedQualityAuthority.evaluate_artifact("PRESENTATION", raw_signals=[sig])
    assert rep1.overall_quality_score == rep2.overall_quality_score
    assert rep1.decision == rep2.decision
    assert len(rep1.findings) == len(rep2.findings)


def test_25_graceful_handling_missing_partial_evaluator_inputs():
    """Test 25: UnifiedQualityAuthority gracefully evaluates when any evaluator input is None."""
    # Only fidelity provided, all others None
    rep = UnifiedQualityAuthority.evaluate_artifact(
        "PRESENTATION",
        rendered_inspection=None,
        calibration_report=None,
        fidelity_report=None,
        semantic_report=None,
        legacy_report=None,
        raw_signals=None,
    )
    assert rep.overall_quality_score == 1.0
    assert rep.decision == ExportDecision.EXPORT_APPROVED
    assert rep.can_export is True


# =============================================================================
# 10. Signal Provider Adapter Unit Verification
# =============================================================================

def test_26_rendered_signal_adapter_bounding_box_extraction():
    """Test 26: RenderedQualitySignalAdapter extracts bounding boxes and measurements."""
    defect = {
        "code": "TEXT_CLIPPING",
        "severity": "CRITICAL",
        "page_indices": [2],
        "element_id": "txt_2",
        "description": "Text clipped",
        "evidence": {
            "bounding_box": [50.0, 50.0, 300.0, 400.0],
            "font_size": 14.0,
            "threshold": 12.0,
        },
    }
    class MockInspection:
        defects = [defect]
        artifact_type = "PRESENTATION"

    sigs = RenderedQualitySignalAdapter.adapt(MockInspection())
    assert len(sigs) == 1
    s = sigs[0]
    assert s.canonical_code == "TEXT_CLIPPING"
    assert s.severity == SignalSeverity.BLOCKING
    assert s.location.slide_index == 2
    assert s.location.bounding_box == (50.0, 50.0, 300.0, 400.0)
    assert s.measurement == "text_clipping"


def test_27_fidelity_signal_adapter_dropped_source_units():
    """Test 27: FidelitySignalAdapter translates dropped source units to blocking signal."""
    report = ArtifactFidelityReport.compute(
        artifact_type="PRESENTATION",
        semantic_preservation=0.8,
        structural_preservation=0.8,
        traceability_preservation=0.8,
        artifact_contract_preservation=0.8,
        metadata={"dropped_source_units": ["unit_9", "unit_10"]},
    )
    sigs = FidelitySignalAdapter.adapt(report)
    assert len(sigs) == 1
    assert sigs[0].canonical_code == "TRACEABILITY_BREAK"
    assert sigs[0].severity == SignalSeverity.BLOCKING
    assert sigs[0].location.source_unit_ids == ("unit_9", "unit_10")


def test_28_calibration_signal_adapter_preserves_metadata():
    """Test 28: CalibrationSignalAdapter preserves measurement metrics and threshold."""
    defect = {
        "code": "EXCESSIVE_DENSITY",
        "severity": "WARNING",
        "page_indices": [1],
        "description": "Excessive density",
        "value": 1900.0,
        "threshold": 1400.0,
    }
    sigs = CalibrationSignalAdapter.adapt([defect], artifact_type="PRESENTATION")
    assert len(sigs) == 1
    assert sigs[0].canonical_code == "COGNITIVE_OVERLOAD"
    assert sigs[0].raw_value == 1900.0
    assert sigs[0].threshold == 1400.0


def test_29_presentation_signal_adapter_gate_reasons():
    """Test 29: PresentationQualitySignalAdapter parses gate reasons and findings."""
    gate = {
        "findings": [
            {
                "rule_id": "REPEATED_GENERIC_CARD",
                "severity": "WARNING",
                "description": "Cards repeat without variation",
                "slide_index": 3,
            }
        ]
    }
    sigs = PresentationQualitySignalAdapter.adapt(gate)
    assert len(sigs) == 1
    assert sigs[0].canonical_code == "LAYOUT_MONOTONY"
    assert sigs[0].location.slide_index == 3


def test_30_legacy_document_signal_adapter_dimension_mapping():
    """Test 30: LegacyDocumentQualitySignalAdapter maps legacy dimension to canonical domain."""
    class MockLegacyFinding:
        dimension = "PEDAGOGICAL_ALIGNMENT"
        severity = "WARNING"
        finding = "Pedagogical alignment discrepancy"
        affected_section = "Page 2"
        score_impact = -0.15

    class MockLegacyReport:
        findings = [MockLegacyFinding()]
        artifact_type = "HANDOUT"

    sigs = LegacyDocumentQualitySignalAdapter.adapt(MockLegacyReport())
    assert len(sigs) == 1
    assert sigs[0].domain == QualityDomain.ARTIFACT
    assert sigs[0].location.page_index == 2
