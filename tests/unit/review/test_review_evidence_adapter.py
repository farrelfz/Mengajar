"""
Unit tests for Phase 6.4 and Phase 6.5 Review Evidence and Lineage Adapter.
"""

import tempfile
from pathlib import Path

from app.review.contracts import (
    EvidenceSufficiencyLevel,
    ReviewTrigger,
)
from app.review.evidence import (
    ArtifactSnapshotManager,
    EvidencePackageBuilder,
    EvidenceSufficiencyAnalyzer,
    ReviewLineageAdapter,
)


def test_evidence_sufficiency_analyzer_dimensions():
    # 1. Sufficient when all components present
    res = EvidenceSufficiencyAnalyzer.evaluate(
        has_renders=True,
        bounding_boxes=[{"box": [10, 10, 100, 100]}],
        findings=[{"failure_code": "TEXT_CONTAINER_OVERFLOW", "message": "overflow detected"}],
        traceability_links=[{"source_id": "src_1"}],
        repair_history=[{"iteration": 1}],
        provenance_graph={"findings_by_id": {"f1": {}}},
        artifact_type="PRESENTATION",
    )
    assert res.overall_sufficiency == EvidenceSufficiencyLevel.SUFFICIENT
    assert res.geometric_evidence
    assert res.provenance_completeness

    # 2. Insufficient when layout defect has no renders and no bounding boxes
    res_no_geo = EvidenceSufficiencyAnalyzer.evaluate(
        has_renders=False,
        bounding_boxes=[],
        findings=[{"failure_code": "TEXT_CONTAINER_OVERFLOW", "message": "overflow detected"}],
        traceability_links=[],
        repair_history=[],
        provenance_graph=None,
        artifact_type="PRESENTATION",
    )
    assert res_no_geo.overall_sufficiency == EvidenceSufficiencyLevel.INSUFFICIENT
    assert not res_no_geo.geometric_evidence
    assert not res_no_geo.provenance_completeness


def test_review_lineage_adapter():
    prov = {
        "findings_by_id": {
            "f1": {
                "failure_code": "BOX_COLLISION",
                "severity": "MAJOR",
                "message": "collision with header",
            }
        },
        "signals_by_id": {
            "s1": {
                "signal_id": "s1",
                "metric_name": "element_collision",
                "location": (10.0, 20.0, 50.0, 60.0),
                "page_or_slide": 2,
            }
        },
        "finding_to_signals": {"f1": ["s1"]},
        "decision_record": {"decision": "MANUAL_REVIEW_REQUIRED"},
    }

    adapted = ReviewLineageAdapter.adapt_quality_provenance(prov)
    assert len(adapted["findings"]) == 1
    assert adapted["findings"][0]["finding_id"] == "f1"
    assert len(adapted["findings"][0]["contributing_signals"]) == 1

    bboxes = ReviewLineageAdapter.extract_bounding_boxes(adapted["signals"])
    assert len(bboxes) == 1
    assert bboxes[0]["page_or_slide"] == 2
    assert bboxes[0]["bounding_box"] == (10.0, 20.0, 50.0, 60.0)


def test_evidence_package_builder_and_markdown():
    pkg = EvidencePackageBuilder.assemble(
        case_id="case_123",
        artifact_id="art_presentation_01",
        artifact_type="PRESENTATION",
        trigger=ReviewTrigger.QUALITY_MANUAL_REVIEW,
        hard_blockers=["BLOCKER_COLLISION"],
        findings=[{"failure_code": "COLLISION", "message": "Element overlap", "severity": "BLOCKING"}],
        signals=[{"signal_id": "sig_1", "location": (0, 0, 10, 10), "page_or_slide": 1}],
        render_snapshot_paths=["/tmp/fake_slide_1.png"],
        repair_history=[{"iteration": 1, "strategy": "split_slide", "is_committed": False}],
        provenance_graph={"findings_by_id": {"f1": {}}},
    )

    assert pkg.case_id == "case_123"
    assert pkg.artifact_type == "PRESENTATION"
    assert len(pkg.hard_blockers) == 1
    assert len(pkg.failed_strategies) == 1

    md = EvidencePackageBuilder.generate_markdown_summary(pkg)
    assert "REVIEW EVIDENCE PACKAGE" in md
    assert "BLOCKER_COLLISION" in md
    assert "split_slide" in md
