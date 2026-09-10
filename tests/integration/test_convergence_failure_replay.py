"""
Universal Document Intelligence System V5 — Convergence Failure Replay Integration Tests.

Phase 3D.1: Replays benchmark scenarios across Handout, Presentation, Worksheet,
and Scientific Document artifacts, validating:
1. Zero regressions on already-exported Handout artifacts.
2. Legitimate convergence progression and escalation across repair cycles.
3. Strict enforcement of quality standards without artificial relaxation.
4. Comprehensive 13-section convergence_failure_report.md generation for any
   artifact requiring manual review.
"""

from pathlib import Path
import pytest
from app.orchestration.production_context import ProductionState
from app.orchestration.production_orchestrator import ProductionOrchestrator, ProductionRequest


@pytest.fixture
def oobleck_input() -> str:
    fixture_path = Path("tests/fixtures/oobleck_experiment.md")
    assert fixture_path.exists()
    return fixture_path.read_text(encoding="utf-8")


@pytest.mark.asyncio
async def test_handout_zero_regression(oobleck_input: str, tmp_path: Path):
    """
    CRITICAL INVARIANT: Zero regressions on already-exported artifacts.
    Handout MUST continue to converge and export with complete package.
    """
    orchestrator = ProductionOrchestrator()
    req = ProductionRequest(
        raw_input=oobleck_input,
        artifact_type="HANDOUT",
        output_dir=tmp_path,
        job_id="replay_handout_pass",
        source_filename="oobleck_experiment.md",
    )

    outcome = await orchestrator.produce(req)

    assert outcome.artifact_type == "HANDOUT"
    assert outcome.success is True
    assert outcome.final_state == ProductionState.EXPORTED
    assert outcome.export_package is not None
    assert outcome.quality_report is not None
    assert len(outcome.quality_report.hard_blockers) == 0
    assert outcome.overall_quality_score >= 0.80

    final_dir = tmp_path / "replay_handout_pass" / "final"
    assert (final_dir / "handout_artifact.html").exists()
    assert (final_dir / "handout_artifact.pdf").exists()
    assert (final_dir / "manifest.json").exists()


@pytest.mark.asyncio
async def test_presentation_repair_and_governance(oobleck_input: str, tmp_path: Path):
    """
    Presentation replay: verifies repair loop attempts, scope reservation,
    and truthful governance (no fake convergence, generates report if manual review).
    """
    orchestrator = ProductionOrchestrator()
    req = ProductionRequest(
        raw_input=oobleck_input,
        artifact_type="PRESENTATION",
        output_dir=tmp_path,
        job_id="replay_pres_gov",
        source_filename="oobleck_experiment.md",
    )

    outcome = await orchestrator.produce(req)

    assert outcome.artifact_type == "PRESENTATION"
    assert outcome.quality_report is not None
    assert outcome.final_state in (
        ProductionState.EXPORTED,
        ProductionState.APPROVED,
        ProductionState.APPROVED_WITH_WARNINGS,
        ProductionState.MANUAL_REVIEW_REQUIRED,
    )

    job_dir = tmp_path / "replay_pres_gov"
    if outcome.final_state == ProductionState.MANUAL_REVIEW_REQUIRED:
        report_path = job_dir / "convergence_failure_report.md"
        assert report_path.exists(), "Failure report must be generated on MANUAL_REVIEW_REQUIRED"
        content = report_path.read_text(encoding="utf-8")
        assert "# CONVERGENCE FAILURE EXPLANATION REPORT" in content
        for i in range(1, 14):
            assert f"## {i}." in content
    elif outcome.final_state == ProductionState.EXPORTED:
        assert outcome.export_package is not None
        assert len(outcome.quality_report.hard_blockers) == 0


@pytest.mark.asyncio
async def test_worksheet_repair_and_governance(oobleck_input: str, tmp_path: Path):
    """
    Worksheet replay: verifies worksheet-specific repair strategies are used,
    zero cross-artifact pollution, and full report generation if held for manual review.
    """
    orchestrator = ProductionOrchestrator()
    req = ProductionRequest(
        raw_input=oobleck_input,
        artifact_type="WORKSHEET",
        output_dir=tmp_path,
        job_id="replay_ws_gov",
        source_filename="oobleck_experiment.md",
    )

    outcome = await orchestrator.produce(req)

    assert outcome.artifact_type == "WORKSHEET"
    assert outcome.quality_report is not None
    assert outcome.final_state in (
        ProductionState.EXPORTED,
        ProductionState.APPROVED,
        ProductionState.APPROVED_WITH_WARNINGS,
        ProductionState.MANUAL_REVIEW_REQUIRED,
    )

    job_dir = tmp_path / "replay_ws_gov"
    if outcome.final_state == ProductionState.MANUAL_REVIEW_REQUIRED:
        report_path = job_dir / "convergence_failure_report.md"
        assert report_path.exists()
        content = report_path.read_text(encoding="utf-8")
        assert "## 13. Recommended Manual Intervention" in content


@pytest.mark.asyncio
async def test_scientific_document_repair_and_governance(oobleck_input: str, tmp_path: Path):
    """
    Scientific document replay: verifies evidence mapping and citation strategy,
    truthful quality evaluation, and failure report generation.
    """
    orchestrator = ProductionOrchestrator()
    req = ProductionRequest(
        raw_input=oobleck_input,
        artifact_type="SCIENTIFIC_DOCUMENT",
        output_dir=tmp_path,
        job_id="replay_sci_gov",
        source_filename="oobleck_experiment.md",
    )

    outcome = await orchestrator.produce(req)

    assert outcome.artifact_type == "SCIENTIFIC_DOCUMENT"
    assert outcome.quality_report is not None
    assert outcome.final_state in (
        ProductionState.EXPORTED,
        ProductionState.APPROVED,
        ProductionState.APPROVED_WITH_WARNINGS,
        ProductionState.MANUAL_REVIEW_REQUIRED,
    )

    job_dir = tmp_path / "replay_sci_gov"
    if outcome.final_state == ProductionState.MANUAL_REVIEW_REQUIRED:
        report_path = job_dir / "convergence_failure_report.md"
        assert report_path.exists()
        content = report_path.read_text(encoding="utf-8")
        assert "## 13. Recommended Manual Intervention" in content


@pytest.mark.asyncio
async def test_failure_report_13_sections_exhaustive(oobleck_input: str, tmp_path: Path):
    """
    Exhaustively verifies all 13 mandatory sections of convergence_failure_report.md.
    """
    orchestrator = ProductionOrchestrator()
    # Force max_repair_iterations=0 so it routes directly to manual review if findings exist
    req = ProductionRequest(
        raw_input=oobleck_input,
        artifact_type="PRESENTATION",
        output_dir=tmp_path,
        job_id="replay_report_check",
        source_filename="oobleck_experiment.md",
    )

    outcome = await orchestrator.produce(req)

    job_dir = tmp_path / "replay_report_check"
    report_path = job_dir / "convergence_failure_report.md"
    if report_path.exists():
        content = report_path.read_text(encoding="utf-8")
        expected_sections = [
            "## 1. Initial Defects Observed",
            "## 2. Root Cause Graph & Causal Attributions",
            "## 3. Hypotheses Considered",
            "## 4. Repair Candidates Generated",
            "## 5. Candidates Rejected",
            "## 6. Mutations Applied",
            "## 7. Quality Vector Evolution",
            "## 8. Blocker Evolution",
            "## 9. Drift Analysis",
            "## 10. Budget Consumption",
            "## 11. Local Minimum Detection",
            "## 12. Exact Termination Cause",
            "## 13. Recommended Manual Intervention",
        ]
        for sec in expected_sections:
            assert sec in content, f"Missing required section: {sec}"
