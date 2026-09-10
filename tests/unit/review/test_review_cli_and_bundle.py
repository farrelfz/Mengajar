"""
Unit tests for Phase 6.15 CLI Review Harness and Static Review Bundle Generator.
"""

import json
import tempfile
from pathlib import Path

from app.review.cli import main
from app.review.contracts import (
    ReviewState,
    ReviewTrigger,
)
from app.review.evidence import EvidencePackageBuilder
from app.review.intake import ReviewIntakeRouter
from app.review.queue.registry import ReviewQueueRegistry
from app.review.static_bundle import StaticReviewBundleGenerator


def test_static_review_bundle_generator():
    with tempfile.TemporaryDirectory() as tmp_dir:
        out_dir = Path(tmp_dir) / "bundle_test"
        case = ReviewIntakeRouter.ingest_case(
            artifact_id="art_slide_99",
            artifact_type="PRESENTATION",
            trigger=ReviewTrigger.CONVERGENCE_FAILURE,
            findings=[{"failure_code": "TEXT_CONTAINER_OVERFLOW", "message": "Text overflow on slide 3"}],
            hard_blockers=["BLOCKER_OVERFLOW"],
        )
        pkg = EvidencePackageBuilder.assemble(
            case_id=case.case_id,
            artifact_id=case.artifact_id,
            artifact_type=case.artifact_type,
            trigger=case.trigger,
            hard_blockers=case.metadata.get("hard_blocker_count", 0) * ["BLOCKER_OVERFLOW"],
            findings=[{"failure_code": "TEXT_CONTAINER_OVERFLOW", "message": "Text overflow on slide 3"}],
        )

        bundle_path = StaticReviewBundleGenerator.generate_bundle(case, pkg, output_dir=out_dir)
        assert bundle_path.exists()
        assert (bundle_path / "case_manifest.json").exists()
        assert (bundle_path / "evidence.json").exists()
        assert (bundle_path / "evidence.md").exists()
        assert (bundle_path / "static_review.html").exists()

        html_content = (bundle_path / "static_review.html").read_text(encoding="utf-8")
        assert "Human Review Studio — Forensic Case Inspection" in html_content
        assert "READ-ONLY FORENSIC VIEW" in html_content
        assert case.case_id in html_content


def test_cli_execution_commands():
    # Ingest a case in default registry with real findings
    registry = ReviewQueueRegistry()
    case = ReviewIntakeRouter.ingest_case(
        artifact_id="cli_test_art",
        artifact_type="HANDOUT",
        trigger=ReviewTrigger.QUALITY_MANUAL_REVIEW,
        findings=[{"failure_code": "DENSITY_IMBALANCE", "message": "Section reading density uneven"}],
    )
    registry.register_case(case)
    assert case.current_state == ReviewState.OPEN

    # 1. list
    rc_list = main(["list"])
    assert rc_list == 0

    # 2. show
    rc_show = main(["show", case.case_id])
    assert rc_show == 0

    # 3. evidence
    rc_ev = main(["evidence", case.case_id])
    assert rc_ev == 0

    # 4. lease
    rc_lease = main(["lease", case.case_id, "reviewer_cli_01"])
    assert rc_lease == 0

    # 5. bundle
    rc_bundle = main(["bundle", case.case_id])
    assert rc_bundle == 0

    # 6. ledger-verify
    rc_ver = main(["ledger-verify"])
    assert rc_ver == 0
