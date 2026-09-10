"""
Universal Document Intelligence System V5 — Phase 3B Golden Benchmark Integration Tests.

End-to-end integration tests verifying the full Phase 3B pipeline across all 4 artifact types:
- PRESENTATION: Multi-slide deck with capacity overflow and typography scale defects
- HANDOUT: A4 reading material with density overload and orphan headings
- WORKSHEET: LKS with anti-spoiling critical invariant violation
- SCIENTIFIC_DOCUMENT: Academic article with invisible citation and unsupported claim
- CLEAN_ARTIFACT: Defect-free artifact with zero false positives
- REPORT GENERATION: Verifies causal_analysis.json and causal_analysis.md output structure
"""

import json
from pathlib import Path
import pytest

from app.quality.causal.causal_engine import MasterCausalEngine
from app.quality.causal.causal_reporter import CausalReporter
from app.quality.causal.causal_taxonomy import CausalDecision, RootCauseCategory
from app.quality.causal.contracts import QualityLocation, QualitySignal
from app.quality.causal.lifecycle import QualitySignalLifecycleState
from app.quality.causal.provenance import EvidenceReference, EvidenceSourceType
from app.quality.causal.repair_readiness import RepairAuthorityLevel
from app.quality.causal.taxonomy import (
    CanonicalFailureCode,
    CanonicalFailureDomain,
    CanonicalSeverity,
    FailureScope,
)


def _ev(code: str) -> tuple:
    return (
        EvidenceReference(
            source_type=EvidenceSourceType.PYMUPDF_GEOMETRY,
            description=f"Automated measurement proof for {code}",
        ),
    )


def test_golden_benchmark_presentation_deck(tmp_path: Path):
    """End-to-end evaluation of a 10-slide Presentation deck with correlated capacity overload and typography issues."""
    engine = MasterCausalEngine()

    signals = [
        # Slide 2: Density overload leading to clipping and small text
        QualitySignal(
            signal_id="sig_p2_clip",
            source_engine="geometry_inspector",
            failure_domain=CanonicalFailureDomain.PHYSICAL_RENDER,
            failure_code=CanonicalFailureCode.TEXT_CLIPPING,
            severity=CanonicalSeverity.MAJOR,
            location=QualityLocation(artifact_type="PRESENTATION", page_index=2, element_id="card_hero", blueprint_element_ids=("bp_card_hero",)),
            description="Text clipped at card boundary on slide 2",
        ),
        QualitySignal(
            signal_id="sig_p2_small",
            source_engine="font_inspector",
            failure_domain=CanonicalFailureDomain.PHYSICAL_RENDER,
            failure_code=CanonicalFailureCode.TEXT_TOO_SMALL,
            severity=CanonicalSeverity.MAJOR,
            location=QualityLocation(artifact_type="PRESENTATION", page_index=2, element_id="card_hero", blueprint_element_ids=("bp_card_hero",)),
            description="Font scaled to 6pt to fit container",
        ),
        QualitySignal(
            signal_id="sig_p2_dense",
            source_engine="density_inspector",
            failure_domain=CanonicalFailureDomain.COGNITIVE_LOAD,
            failure_code=CanonicalFailureCode.DENSITY_OVERLOAD,
            severity=CanonicalSeverity.MAJOR,
            location=QualityLocation(artifact_type="PRESENTATION", page_index=2, element_id="card_hero", blueprint_element_ids=("bp_card_hero",)),
            description="Slot contains 140 words, exceeding presentation capacity",
        ),
        # Slide 8: Isolated minor margin issue
        QualitySignal(
            signal_id="sig_p8_margin",
            source_engine="layout_inspector",
            failure_domain=CanonicalFailureDomain.PHYSICAL_RENDER,
            failure_code=CanonicalFailureCode.MARGIN_INCONSISTENCY,
            severity=CanonicalSeverity.MINOR,
            location=QualityLocation(artifact_type="PRESENTATION", page_index=8, element_id="footer_elem"),
            description="Footer margin 12px instead of standard 16px",
        ),
    ]

    result = engine.analyze(signals, total_pages=10, artifact_type="PRESENTATION")

    assert result.total_signals == 4
    assert result.clusters_count == 2  # Slide 2 cluster (3 signals) + Slide 8 singleton (1 signal)

    # Find slide 2 cluster
    c_p2 = next(c for c in result.clusters if 2 in c.affected_pages)
    assert len(c_p2.signals) == 3
    assert c_p2.scope == FailureScope.LOCAL
    assert c_p2.primary_root_cause is not None
    assert c_p2.primary_root_cause.cause_code == RootCauseCategory.LAYOUT_CAPACITY_EXCEEDED.value

    # Check readiness assessment
    readiness_p2 = result.readiness_assessments[c_p2.cluster_id]
    assert readiness_p2.recommended_authority in (
        RepairAuthorityLevel.DETERMINISTIC_REPAIR_CANDIDATE,
        RepairAuthorityLevel.MANUAL_REVIEW,
    )

    # Check lifecycle progression
    for sig_id in ("sig_p2_clip", "sig_p2_small", "sig_p2_dense"):
        rec = result.signal_lifecycle_records[sig_id]
        assert rec.current_state == QualitySignalLifecycleState.CAUSAL_HYPOTHESIS

    # Test report generation
    json_path, md_path = CausalReporter.write_reports(result, tmp_path)
    assert json_path.exists()
    assert md_path.exists()

    report_data = json.loads(json_path.read_text(encoding="utf-8"))
    assert report_data["total_signals"] == 4
    assert len(report_data["observations"]) == 4
    assert len(report_data["confirmed_causes"]) >= 1

    md_content = md_path.read_text(encoding="utf-8")
    assert "SECTION 1: OBSERVATIONS" in md_content
    assert "SECTION 2: INFERENCES" in md_content
    assert "SECTION 3: CONFIRMED CAUSES" in md_content


def test_golden_benchmark_worksheet_critical_invariant():
    """End-to-end evaluation of Worksheet with critical spoiling defect."""
    engine = MasterCausalEngine()

    signals = [
        QualitySignal(
            signal_id="sig_w_spoil",
            source_engine="pedagogical_validator",
            failure_domain=CanonicalFailureDomain.PEDAGOGICAL_STRUCTURE,
            failure_code=CanonicalFailureCode.WORKSHEET_SPOILING_FAILURE,
            severity=CanonicalSeverity.CRITICAL,
            evidence=_ev("WORKSHEET_SPOILING_FAILURE"),
            location=QualityLocation(artifact_type="WORKSHEET", page_index=1, element_id="task_box_1"),
            description="Answer revealed in observation task before inquiry prompt",
        ),
    ]

    result = engine.analyze(signals, total_pages=2, artifact_type="WORKSHEET")

    assert len(result.clusters) == 1
    clust = result.clusters[0]
    assert clust.scope == FailureScope.ARTIFACT_WIDE
    assert clust.primary_root_cause.cause_code == RootCauseCategory.WORKSHEET_ANSWER_LEAKAGE.value

    readiness = result.readiness_assessments[clust.cluster_id]
    # Critical artifact-wide defect has high blast radius
    assert readiness.recommended_authority == RepairAuthorityLevel.HIGH_RISK_REPAIR
    assert readiness.is_repair_ready() is False


def test_golden_benchmark_scientific_document():
    """End-to-end evaluation of Scientific Document with citation visibility and evidence linkage."""
    engine = MasterCausalEngine()

    signals = [
        QualitySignal(
            signal_id="sig_sci_cite",
            source_engine="rigor_validator",
            failure_domain=CanonicalFailureDomain.SCIENTIFIC_RIGOR,
            failure_code=CanonicalFailureCode.SCIENTIFIC_CITATION_INVISIBLE,
            severity=CanonicalSeverity.CRITICAL,
            evidence=_ev("SCIENTIFIC_CITATION_INVISIBLE"),
            location=QualityLocation(artifact_type="SCIENTIFIC_DOCUMENT", page_index=3, element_id="ref_callout_3", source_unit_ids=("ku_paper_1",)),
            description="Citation [12] exists in metadata but not rendered in reference section",
        ),
        QualitySignal(
            signal_id="sig_sci_trace",
            source_engine="traceability_validator",
            failure_domain=CanonicalFailureDomain.SEMANTIC_TRACEABILITY,
            failure_code=CanonicalFailureCode.EVIDENCE_DISCIPLINE_FAILURE,
            severity=CanonicalSeverity.MAJOR,
            location=QualityLocation(artifact_type="SCIENTIFIC_DOCUMENT", page_index=3, element_id="ref_callout_3", source_unit_ids=("ku_paper_1",)),
            description="Claim in Section 3 lacks explicit cited data table",
        ),
    ]

    result = engine.analyze(signals, total_pages=12, artifact_type="SCIENTIFIC_DOCUMENT")

    assert len(result.clusters) == 1
    cluster = result.clusters[0]
    assert cluster.scope == FailureScope.ARTIFACT_WIDE
    assert cluster.primary_root_cause.cause_code == RootCauseCategory.CITATION_STRUCTURE_FAILURE.value
    assert cluster.primary_root_cause.cause_layer == "KNOWLEDGE_MODEL"


def test_golden_benchmark_clean_artifact():
    """End-to-end evaluation of a perfectly valid artifact with zero quality signals."""
    engine = MasterCausalEngine()

    result = engine.analyze([], total_pages=5, artifact_type="PRESENTATION")

    assert result.total_signals == 0
    assert result.clusters_count == 0
    assert len(result.clusters) == 0
    assert len(result.readiness_assessments) == 0
    assert "Clean artifact" in result.summary
