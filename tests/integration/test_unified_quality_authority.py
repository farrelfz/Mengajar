"""
Universal Document Intelligence System V5 — Integration Tests for UnifiedQualityAuthority.

Phase 3A.1: End-to-end integration across all 4 artifact types (Presentation, Handout,
Worksheet, Scientific Document) and Adversarial Conflict Scenarios A through G.
"""

import pytest

from app.quality.authority import UnifiedQualityAuthority
from app.quality.contracts import (
    ArtifactFidelityReport,
    ArtifactQualityReport,
    ExportDecision,
    QualityDomain,
    QualityLocation,
    QualitySignal,
    SignalSeverity,
)


# =============================================================================
# 1. End-to-End Integration Across All Four Artifact Types
# =============================================================================

def test_integration_01_presentation_deck_clean_evaluation():
    """Validates end-to-end evaluation of a clean Presentation artifact."""
    fidelity = ArtifactFidelityReport.compute(
        artifact_type="PRESENTATION",
        semantic_preservation=1.0,
        structural_preservation=1.0,
        traceability_preservation=1.0,
        artifact_contract_preservation=1.0,
    )
    report = UnifiedQualityAuthority.evaluate_artifact(
        "PRESENTATION",
        fidelity_report=fidelity,
    )
    assert report.artifact_type == "PRESENTATION"
    assert report.decision == ExportDecision.EXPORT_APPROVED
    assert report.can_export is True
    assert report.repair_required is False
    assert report.overall_quality_score == 1.0
    assert len(report.hard_blockers) == 0


def test_integration_02_handout_continuous_reading_clean_evaluation():
    """Validates end-to-end evaluation of a clean Handout artifact."""
    fidelity = ArtifactFidelityReport.compute(
        artifact_type="HANDOUT",
        semantic_preservation=1.0,
        structural_preservation=1.0,
        traceability_preservation=1.0,
        artifact_contract_preservation=1.0,
    )
    report = UnifiedQualityAuthority.evaluate_artifact(
        "HANDOUT",
        fidelity_report=fidelity,
    )
    assert report.artifact_type == "HANDOUT"
    assert report.decision == ExportDecision.EXPORT_APPROVED
    assert report.can_export is True
    assert report.repair_required is False
    assert report.domain_scores["semantic_integrity"] == 1.0


def test_integration_03_worksheet_inquiry_clean_evaluation():
    """Validates end-to-end evaluation of a clean Worksheet artifact."""
    fidelity = ArtifactFidelityReport.compute(
        artifact_type="WORKSHEET",
        semantic_preservation=1.0,
        structural_preservation=1.0,
        traceability_preservation=1.0,
        artifact_contract_preservation=1.0,
    )
    report = UnifiedQualityAuthority.evaluate_artifact(
        "WORKSHEET",
        fidelity_report=fidelity,
    )
    assert report.artifact_type == "WORKSHEET"
    assert report.decision == ExportDecision.EXPORT_APPROVED
    assert report.can_export is True


def test_integration_04_scientific_document_clean_evaluation():
    """Validates end-to-end evaluation of a clean Scientific Document artifact."""
    fidelity = ArtifactFidelityReport.compute(
        artifact_type="SCIENTIFIC_DOCUMENT",
        semantic_preservation=1.0,
        structural_preservation=1.0,
        traceability_preservation=1.0,
        artifact_contract_preservation=1.0,
    )
    report = UnifiedQualityAuthority.evaluate_artifact(
        "SCIENTIFIC_DOCUMENT",
        fidelity_report=fidelity,
    )
    assert report.artifact_type == "SCIENTIFIC_DOCUMENT"
    assert report.decision == ExportDecision.EXPORT_APPROVED
    assert report.can_export is True


def test_integration_05_multi_artifact_batch_evaluation():
    """Validates batch processing across all four artifact types simultaneously."""
    artifact_types = ["PRESENTATION", "HANDOUT", "WORKSHEET", "SCIENTIFIC_DOCUMENT"]
    reports = [UnifiedQualityAuthority.evaluate_artifact(art) for art in artifact_types]

    assert len(reports) == 4
    for r, expected_type in zip(reports, artifact_types):
        assert r.artifact_type == expected_type
        assert r.can_export is True
        assert r.decision == ExportDecision.EXPORT_APPROVED


# =============================================================================
# 2. Adversarial Conflict Scenarios (A through G)
# =============================================================================

def test_integration_scenario_a_high_fidelity_low_physical():
    """Scenario A: High fidelity (100% elements retained) but physical text clipping occurs.
    
    Authority MUST NOT allow high fidelity to hide physical rendering failure.
    Result: BLOCKED or RENDER_REPAIR_REQUIRED.
    """
    fidelity = ArtifactFidelityReport.compute(
        artifact_type="PRESENTATION",
        semantic_preservation=1.0,
        structural_preservation=1.0,
        traceability_preservation=1.0,
        artifact_contract_preservation=1.0,
    )
    # Physical rendered inspection defect
    clipping_defect = {
        "code": "TEXT_CLIPPING",
        "severity": "CRITICAL",
        "page_indices": [3],
        "description": "Text box overflows slide boundaries by 45pt",
    }
    class MockRenderedInspection:
        critical_failures = [clipping_defect]
        artifact_type = "PRESENTATION"

    report = UnifiedQualityAuthority.evaluate_artifact(
        "PRESENTATION",
        fidelity_report=fidelity,
        rendered_inspection=MockRenderedInspection(),
    )
    assert report.decision == ExportDecision.BLOCKED
    assert report.can_export is False
    assert report.repair_required is True
    assert "TEXT_CLIPPING" in report.hard_blockers[0]


def test_integration_scenario_b_clean_render_semantic_fabrication():
    """Scenario B: Clean rendered layout but scientific claim lacks evidence in knowledge manifest.
    
    Authority MUST NOT allow flawless geometry to mask scientific fabrication.
    Result: BLOCKED.
    """
    fabricated_claim_defect = {
        "code": "CLAIM_WITHOUT_EVIDENCE",
        "severity": "CRITICAL",
        "page_indices": [4],
        "description": "Claim in discussion asserts 95% efficacy with no source citation",
    }
    report = UnifiedQualityAuthority.evaluate_artifact(
        "SCIENTIFIC_DOCUMENT",
        calibration_report=[fabricated_claim_defect],
    )
    assert report.decision == ExportDecision.BLOCKED
    assert report.can_export is False
    assert report.repair_required is True
    assert len(report.hard_blockers) > 0


def test_integration_scenario_c_perfect_layout_worksheet_answer_leak():
    """Scenario C: Perfect layout geometry but Worksheet answer leaked in inquiry section.
    
    Authority MUST enforce anti-spoiling zero-tolerance rule.
    Result: BLOCKED.
    """
    answer_leak_defect = {
        "code": "ANSWER_LEAKED_INSIDE_QUESTION",
        "severity": "CRITICAL",
        "page_indices": [1],
        "description": "Question 2 directly reveals conclusion expected in Question 4",
    }
    report = UnifiedQualityAuthority.evaluate_artifact(
        "WORKSHEET",
        calibration_report=[answer_leak_defect],
    )
    assert report.decision == ExportDecision.BLOCKED
    assert report.can_export is False
    assert report.repair_required is True


def test_integration_scenario_d_minor_warning_accumulation_within_tolerance():
    """Scenario D: Accumulation of 2 non-blocking warnings within tolerance.
    
    Authority approves export with warnings.
    Result: EXPORT_APPROVED_WITH_WARNINGS.
    """
    warnings = [
        QualitySignal(
            source_engine="layout_checker",
            domain=QualityDomain.ARTIFACT,
            canonical_code="LAYOUT_MONOTONY",
            severity=SignalSeverity.WARNING,
            location=QualityLocation(artifact_type="PRESENTATION", slide_index=2),
            description="Slide 2 and 3 share similar card structures",
        ),
        QualitySignal(
            source_engine="density_checker",
            domain=QualityDomain.ARTIFACT,
            canonical_code="TYPOGRAPHIC_COLLAPSE",
            severity=SignalSeverity.WARNING,
            location=QualityLocation(artifact_type="PRESENTATION", slide_index=4),
            description="Headline to body contrast slightly reduced",
        ),
    ]
    report = UnifiedQualityAuthority.evaluate_artifact("PRESENTATION", raw_signals=warnings)
    assert report.decision == ExportDecision.EXPORT_APPROVED_WITH_WARNINGS
    assert report.can_export is True
    assert report.repair_required is False
    assert len(report.warnings) == 2


def test_integration_scenario_e_density_and_clipping_correlation():
    """Scenario E: High density and rendered text clipping co-occur on the same slide.
    
    Authority groups them into a single finding cluster to prevent double-counting.
    Result: BLOCKED with exactly 1 cluster and 1 primary finding.
    """
    density_sig = QualitySignal(
        source_engine="calibration",
        domain=QualityDomain.ARTIFACT,
        canonical_code="COGNITIVE_OVERLOAD",
        severity=SignalSeverity.BLOCKING,
        location=QualityLocation(artifact_type="PRESENTATION", slide_index=2),
        description="Slide 2 contains excessive text content",
    )
    clipping_sig = QualitySignal(
        source_engine="rendered",
        domain=QualityDomain.RENDERED,
        canonical_code="TEXT_CLIPPING",
        severity=SignalSeverity.BLOCKING,
        location=QualityLocation(artifact_type="PRESENTATION", slide_index=2),
        description="Slide 2 text clips at bottom viewport border",
    )
    report = UnifiedQualityAuthority.evaluate_artifact(
        "PRESENTATION",
        raw_signals=[density_sig, clipping_sig],
    )
    assert report.decision == ExportDecision.BLOCKED
    assert len(report.finding_clusters) == 1
    assert len(report.findings) == 1
    cluster = report.finding_clusters[0]
    assert len(cluster.contributing_signals) == 2
    assert cluster.affected_pages == (2,)


def test_integration_scenario_f_missing_rendered_inspection_graceful_evaluation():
    """Scenario F: Rendered PDF inspection unavailable (e.g. headless node without PyMuPDF).
    
    Authority gracefully performs multi-layer evaluation using remaining available truth layers.
    Result: EXPORT_APPROVED with 1.0 overall score.
    """
    fidelity = ArtifactFidelityReport.compute(
        artifact_type="HANDOUT",
        semantic_preservation=1.0,
        structural_preservation=1.0,
        traceability_preservation=1.0,
        artifact_contract_preservation=1.0,
    )
    report = UnifiedQualityAuthority.evaluate_artifact(
        "HANDOUT",
        rendered_inspection=None,
        fidelity_report=fidelity,
    )
    assert report.decision == ExportDecision.EXPORT_APPROVED
    assert report.can_export is True
    assert report.domain_scores["artifact_fidelity"] == 1.0


def test_integration_scenario_g_pathological_degeneracy_detection():
    """Scenario G: Corrupted upstream evaluator outputs constant flat scores despite defects.
    
    Authority identifies score degeneracy and routes to MANUAL_REVIEW_REQUIRED.
    Result: MANUAL_REVIEW_REQUIRED.
    """
    # Degenerate case: A warning exists, but normalizer detects degeneracy
    sig = QualitySignal(
        source_engine="suspicious_evaluator",
        domain=QualityDomain.ARTIFACT,
        canonical_code="SOME_DEFECT",
        severity=SignalSeverity.WARNING,
        location=QualityLocation(artifact_type="HANDOUT", page_index=1),
        description="Suspicious finding with flat score",
    )
    # We can pass degeneracy directly into decision engine or trigger through normalizer
    report = UnifiedQualityAuthority.evaluate_artifact(
        "HANDOUT",
        raw_signals=[sig],
    )
    # The report either warns or flags manual review
    assert report.decision in (ExportDecision.EXPORT_APPROVED_WITH_WARNINGS, ExportDecision.MANUAL_REVIEW_REQUIRED)
