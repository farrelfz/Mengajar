"""
Universal Knowledge Core — Cross-Fixture Quality Benchmark Test Suite.

Phase 2C Adversarial Artifact Quality Calibration:
Executes the full 28-artifact matrix (7 benchmark fixtures x 4 artifact types).
Validates quality scoring, fidelity, calibrated decisions, statistical distribution,
non-degeneracy, contact sheets, and baseline regression compliance.
"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
import statistics
import time
from typing import Any, Dict, List, Tuple
import pytest

from app.intelligence.pipeline import (
    KnowledgeCompiler,
    OfflineMockResolutionProvider,
)
from app.intelligence.schemas import UniversalKnowledgeManifest
from app.intelligence.transformation import (
    ArtifactType,
    HandoutTransformer,
    KnowledgeSelectionEngine,
    PresentationTransformer,
    ScientificDocumentTransformer,
    WorksheetTransformer,
    get_default_intent,
)
from app.integration.artifact_bridge import (
    HandoutBlueprintBridge,
    PresentationBlueprintBridge,
    RenderArtifact,
    ScientificDocumentBlueprintBridge,
    WorksheetBlueprintBridge,
)
from app.integration.render_execution import (
    HandoutExecutor,
    PresentationExecutor,
    RendererExecutionResult,
    ScientificDocumentExecutor,
    WorksheetExecutor,
)
from app.integration.renderer_adapters import (
    HandoutContractAdapter,
    PresentationContractAdapter,
    ScientificDocumentContractAdapter,
    WorksheetContractAdapter,
)
from app.presentation.contact_sheet import ContactSheetGenerator
from app.quality.artifact_fidelity.unified_fidelity_validator import (
    UnifiedFidelityValidator,
)
from app.quality.calibration.benchmark_matrix import (
    BenchmarkArtifactEntry,
    BenchmarkQualityMatrix,
)
from app.quality.calibration.decision_engine import CalibratedDecisionEngine
from app.quality.calibration.degeneracy_detector import (
    QualityScoreDegeneracyDetector,
)
from app.quality.calibration.quality_scoring import MasterQualityScoringEngine
from app.quality.contracts.decision_contract import (
    CalibratedQualityDecision,
    QualityDecisionStatus,
)
from app.quality.contracts.fidelity_contract import ArtifactFidelityReport
from app.quality.contracts.quality_contract import ArtifactQualityReport

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures" / "benchmark"
OUTPUT_DIR = Path(__file__).parent.parent.parent / "outputs" / "benchmark" / "phase_2c"
BASELINES_FILE = Path(__file__).parent.parent / "quality_baselines" / "quality_regression_baseline.json"

FIXTURE_FILES = [
    "01_oobleck_experiment.md",
    "02_dinamika_rotasi.md",
    "03_gerak_melingkar.md",
    "04_hand_fire.md",
    "05_short_concept.md",
    "06_long_material.md",
    "07_data_heavy_research.md",
]


class ArtifactExecutionPackage:
    """Encapsulates all execution artifacts and evaluation reports for one run."""

    def __init__(
        self,
        fixture_stem: str,
        artifact_type: str,
        render_artifact: RenderArtifact,
        legacy_model: Any,
        execution_result: RendererExecutionResult,
        fidelity_report: ArtifactFidelityReport,
        quality_report: ArtifactQualityReport,
        decision: CalibratedQualityDecision,
        contact_sheet_path: Path | None,
        duration_ms: float,
    ) -> None:
        self.fixture_stem = fixture_stem
        self.artifact_type = artifact_type
        self.render_artifact = render_artifact
        self.legacy_model = legacy_model
        self.execution_result = execution_result
        self.fidelity_report = fidelity_report
        self.quality_report = quality_report
        self.decision = decision
        self.contact_sheet_path = contact_sheet_path
        self.duration_ms = duration_ms


@pytest.fixture(scope="module")
def execution_matrix() -> Dict[str, Dict[str, ArtifactExecutionPackage]]:
    """Executes the full 28-artifact matrix once and caches results."""
    compiler = KnowledgeCompiler(resolution_provider=OfflineMockResolutionProvider())
    selection_engine = KnowledgeSelectionEngine()
    validator = UnifiedFidelityValidator()
    contact_sheet_gen = ContactSheetGenerator(columns=4, scale=0.35)

    matrix_results: Dict[str, Dict[str, ArtifactExecutionPackage]] = {}
    benchmark_entries: List[BenchmarkArtifactEntry] = []

    out_artifacts_dir = OUTPUT_DIR / "artifacts"
    out_contact_dir = OUTPUT_DIR / "contact_sheets"
    out_reports_dir = OUTPUT_DIR / "reports"

    out_artifacts_dir.mkdir(parents=True, exist_ok=True)
    out_contact_dir.mkdir(parents=True, exist_ok=True)
    out_reports_dir.mkdir(parents=True, exist_ok=True)

    for fname in FIXTURE_FILES:
        fpath = FIXTURES_DIR / fname
        assert fpath.exists(), f"Benchmark fixture missing: {fpath}"
        raw_md = fpath.read_text(encoding="utf-8")
        stem = fpath.stem
        matrix_results[stem] = {}

        manifest = asyncio.run(compiler.compile(raw_md, source_filename=fname))

        # 1. PRESENTATION
        t0 = time.perf_counter()
        intent_p = get_default_intent(ArtifactType.PRESENTATION)
        bp_p = PresentationTransformer().transform(
            manifest, selection_engine.select(manifest, intent_p), intent_p
        )
        ra_p = PresentationBlueprintBridge().bridge(bp_p)
        deck = PresentationContractAdapter().adapt(ra_p)
        p_res = PresentationExecutor().execute(
            deck, out_artifacts_dir / stem / "presentation", "presentation"
        )
        p_fid_eval = validator.evaluate_artifact(ra_p, deck, p_res)
        p_fid_rep = ArtifactFidelityReport.compute(
            artifact_type=ra_p.artifact_type,
            semantic_preservation=p_fid_eval.semantic_fidelity,
            structural_preservation=p_fid_eval.structural_fidelity,
            traceability_preservation=p_fid_eval.traceability_fidelity,
            artifact_contract_preservation=p_fid_eval.artifact_specific_fidelity,
            execution_reliability=p_fid_eval.execution_reliability,
            violations=list(p_fid_eval.violations),
            warnings=list(p_fid_eval.warnings),
            traceability_stats=p_fid_eval.traceability_stats,
            metadata=p_fid_eval.metadata,
        )
        p_q_rep = MasterQualityScoringEngine.evaluate("PRESENTATION", deck)
        p_dec = CalibratedDecisionEngine.arbitrate(p_fid_rep, p_q_rep)

        p_cs_path = out_contact_dir / f"{stem}_presentation_contact_sheet.png"
        if p_res.pdf_path and p_res.pdf_path.exists():
            contact_sheet_gen.generate(p_res.pdf_path, p_cs_path)
        else:
            p_cs_path = None

        dur_p = (time.perf_counter() - t0) * 1000.0
        pkg_p = ArtifactExecutionPackage(
            stem, "PRESENTATION", ra_p, deck, p_res, p_fid_rep, p_q_rep, p_dec, p_cs_path, dur_p
        )
        matrix_results[stem]["PRESENTATION"] = pkg_p
        benchmark_entries.append(
            BenchmarkArtifactEntry(
                fixture_name=stem,
                artifact_type="PRESENTATION",
                fidelity_score=p_fid_rep.overall_fidelity_score,
                quality_score=p_q_rep.overall_quality_score,
                status=p_dec.overall_decision.value,
                critical_failures=tuple(p_dec.blocking_failures),
                warnings=tuple(p_dec.warnings),
                duration_ms=round(dur_p, 1),
            )
        )

        # 2. HANDOUT
        t0 = time.perf_counter()
        intent_h = get_default_intent(ArtifactType.HANDOUT)
        bp_h = HandoutTransformer().transform(
            manifest, selection_engine.select(manifest, intent_h), intent_h
        )
        ra_h = HandoutBlueprintBridge().bridge(bp_h)
        h_doc = HandoutContractAdapter().adapt(ra_h)
        h_res = HandoutExecutor().execute(
            h_doc, out_artifacts_dir / stem / "handout", "handout"
        )
        h_fid_eval = validator.evaluate_artifact(ra_h, h_doc, h_res)
        h_fid_rep = ArtifactFidelityReport.compute(
            artifact_type=ra_h.artifact_type,
            semantic_preservation=h_fid_eval.semantic_fidelity,
            structural_preservation=h_fid_eval.structural_fidelity,
            traceability_preservation=h_fid_eval.traceability_fidelity,
            artifact_contract_preservation=h_fid_eval.artifact_specific_fidelity,
            execution_reliability=h_fid_eval.execution_reliability,
            violations=list(h_fid_eval.violations),
            warnings=list(h_fid_eval.warnings),
            traceability_stats=h_fid_eval.traceability_stats,
            metadata=h_fid_eval.metadata,
        )
        h_q_rep = MasterQualityScoringEngine.evaluate("HANDOUT", h_doc)
        h_dec = CalibratedDecisionEngine.arbitrate(h_fid_rep, h_q_rep)

        h_cs_path = out_contact_dir / f"{stem}_handout_contact_sheet.png"
        if h_res.pdf_path and h_res.pdf_path.exists():
            contact_sheet_gen.generate(h_res.pdf_path, h_cs_path)
        else:
            h_cs_path = None

        dur_h = (time.perf_counter() - t0) * 1000.0
        pkg_h = ArtifactExecutionPackage(
            stem, "HANDOUT", ra_h, h_doc, h_res, h_fid_rep, h_q_rep, h_dec, h_cs_path, dur_h
        )
        matrix_results[stem]["HANDOUT"] = pkg_h
        benchmark_entries.append(
            BenchmarkArtifactEntry(
                fixture_name=stem,
                artifact_type="HANDOUT",
                fidelity_score=h_fid_rep.overall_fidelity_score,
                quality_score=h_q_rep.overall_quality_score,
                status=h_dec.overall_decision.value,
                critical_failures=tuple(h_dec.blocking_failures),
                warnings=tuple(h_dec.warnings),
                duration_ms=round(dur_h, 1),
            )
        )

        # 3. WORKSHEET
        t0 = time.perf_counter()
        intent_w = get_default_intent(ArtifactType.WORKSHEET)
        bp_w = WorksheetTransformer().transform(
            manifest, selection_engine.select(manifest, intent_w), intent_w
        )
        ra_w = WorksheetBlueprintBridge().bridge(bp_w)
        w_doc = WorksheetContractAdapter().adapt(ra_w, grouping_mode="compatibility")
        w_res = WorksheetExecutor().execute(
            w_doc, out_artifacts_dir / stem / "worksheet", "worksheet"
        )
        w_fid_eval = validator.evaluate_artifact(ra_w, w_doc, w_res)
        w_fid_rep = ArtifactFidelityReport.compute(
            artifact_type=ra_w.artifact_type,
            semantic_preservation=w_fid_eval.semantic_fidelity,
            structural_preservation=w_fid_eval.structural_fidelity,
            traceability_preservation=w_fid_eval.traceability_fidelity,
            artifact_contract_preservation=w_fid_eval.artifact_specific_fidelity,
            execution_reliability=w_fid_eval.execution_reliability,
            violations=list(w_fid_eval.violations),
            warnings=list(w_fid_eval.warnings),
            traceability_stats=w_fid_eval.traceability_stats,
            metadata=w_fid_eval.metadata,
        )
        w_q_rep = MasterQualityScoringEngine.evaluate("WORKSHEET", w_doc)
        w_dec = CalibratedDecisionEngine.arbitrate(w_fid_rep, w_q_rep)

        w_cs_path = out_contact_dir / f"{stem}_worksheet_contact_sheet.png"
        if w_res.pdf_path and w_res.pdf_path.exists():
            contact_sheet_gen.generate(w_res.pdf_path, w_cs_path)
        else:
            w_cs_path = None

        dur_w = (time.perf_counter() - t0) * 1000.0
        pkg_w = ArtifactExecutionPackage(
            stem, "WORKSHEET", ra_w, w_doc, w_res, w_fid_rep, w_q_rep, w_dec, w_cs_path, dur_w
        )
        matrix_results[stem]["WORKSHEET"] = pkg_w
        benchmark_entries.append(
            BenchmarkArtifactEntry(
                fixture_name=stem,
                artifact_type="WORKSHEET",
                fidelity_score=w_fid_rep.overall_fidelity_score,
                quality_score=w_q_rep.overall_quality_score,
                status=w_dec.overall_decision.value,
                critical_failures=tuple(w_dec.blocking_failures),
                warnings=tuple(w_dec.warnings),
                duration_ms=round(dur_w, 1),
            )
        )

        # 4. SCIENTIFIC DOCUMENT
        t0 = time.perf_counter()
        intent_s = get_default_intent(ArtifactType.SCIENTIFIC_DOCUMENT)
        bp_s = ScientificDocumentTransformer().transform(
            manifest, selection_engine.select(manifest, intent_s), intent_s
        )
        ra_s = ScientificDocumentBlueprintBridge().bridge(bp_s)
        s_doc = ScientificDocumentContractAdapter().adapt(ra_s)
        s_res = ScientificDocumentExecutor().execute(
            s_doc, out_artifacts_dir / stem / "scientific", "scientific"
        )
        s_fid_eval = validator.evaluate_artifact(ra_s, s_doc, s_res)
        s_fid_rep = ArtifactFidelityReport.compute(
            artifact_type=ra_s.artifact_type,
            semantic_preservation=s_fid_eval.semantic_fidelity,
            structural_preservation=s_fid_eval.structural_fidelity,
            traceability_preservation=s_fid_eval.traceability_fidelity,
            artifact_contract_preservation=s_fid_eval.artifact_specific_fidelity,
            execution_reliability=s_fid_eval.execution_reliability,
            violations=list(s_fid_eval.violations),
            warnings=list(s_fid_eval.warnings),
            traceability_stats=s_fid_eval.traceability_stats,
            metadata=s_fid_eval.metadata,
        )
        s_q_rep = MasterQualityScoringEngine.evaluate("SCIENTIFIC_DOCUMENT", s_doc)
        s_dec = CalibratedDecisionEngine.arbitrate(s_fid_rep, s_q_rep)

        s_cs_path = out_contact_dir / f"{stem}_scientific_contact_sheet.png"
        if s_res.pdf_path and s_res.pdf_path.exists():
            contact_sheet_gen.generate(s_res.pdf_path, s_cs_path)
        else:
            s_cs_path = None

        dur_s = (time.perf_counter() - t0) * 1000.0
        pkg_s = ArtifactExecutionPackage(
            stem, "SCIENTIFIC_DOCUMENT", ra_s, s_doc, s_res, s_fid_rep, s_q_rep, s_dec, s_cs_path, dur_s
        )
        matrix_results[stem]["SCIENTIFIC_DOCUMENT"] = pkg_s
        benchmark_entries.append(
            BenchmarkArtifactEntry(
                fixture_name=stem,
                artifact_type="SCIENTIFIC_DOCUMENT",
                fidelity_score=s_fid_rep.overall_fidelity_score,
                quality_score=s_q_rep.overall_quality_score,
                status=s_dec.overall_decision.value,
                critical_failures=tuple(s_dec.blocking_failures),
                warnings=tuple(s_dec.warnings),
                duration_ms=round(dur_s, 1),
            )
        )

    # Save benchmark matrix
    matrix = BenchmarkQualityMatrix(
        matrix_id="phase_2c_benchmark_execution",
        entries=tuple(benchmark_entries),
    )
    matrix.save_reports(out_reports_dir)

    return matrix_results


# ============================================================================
# 1. FIXTURE 01: OOBLECK EXPERIMENT (4 Artifacts)
# ============================================================================

def test_01_oobleck_presentation(execution_matrix):
    pkg = execution_matrix["01_oobleck_experiment"]["PRESENTATION"]
    assert pkg.execution_result.success is True
    assert pkg.fidelity_report.overall_fidelity_score >= 0.95
    assert pkg.quality_report.overall_quality_score >= 0.80
    assert pkg.decision.can_export is True


def test_02_oobleck_handout(execution_matrix):
    pkg = execution_matrix["01_oobleck_experiment"]["HANDOUT"]
    assert pkg.execution_result.success is True
    assert pkg.fidelity_report.overall_fidelity_score >= 0.95
    assert pkg.quality_report.overall_quality_score >= 0.80
    assert pkg.decision.can_export is True


def test_03_oobleck_worksheet(execution_matrix):
    pkg = execution_matrix["01_oobleck_experiment"]["WORKSHEET"]
    assert pkg.execution_result.success is True
    assert pkg.fidelity_report.overall_fidelity_score >= 0.95
    assert pkg.quality_report.overall_quality_score >= 0.80
    assert pkg.decision.can_export is True


def test_04_oobleck_scientific(execution_matrix):
    pkg = execution_matrix["01_oobleck_experiment"]["SCIENTIFIC_DOCUMENT"]
    assert pkg.execution_result.success is True
    assert pkg.fidelity_report.overall_fidelity_score >= 0.95
    assert pkg.quality_report.overall_quality_score >= 0.80
    assert pkg.decision.can_export is True


# ============================================================================
# 2. FIXTURE 02: DINAMIKA ROTASI (4 Artifacts)
# ============================================================================

def test_05_dinamika_rotasi_presentation(execution_matrix):
    pkg = execution_matrix["02_dinamika_rotasi"]["PRESENTATION"]
    assert pkg.execution_result.success is True
    assert pkg.fidelity_report.overall_fidelity_score >= 0.95
    assert pkg.quality_report.overall_quality_score >= 0.80


def test_06_dinamika_rotasi_handout(execution_matrix):
    pkg = execution_matrix["02_dinamika_rotasi"]["HANDOUT"]
    assert pkg.execution_result.success is True
    assert pkg.fidelity_report.overall_fidelity_score >= 0.95
    assert pkg.quality_report.overall_quality_score >= 0.80


def test_07_dinamika_rotasi_worksheet(execution_matrix):
    pkg = execution_matrix["02_dinamika_rotasi"]["WORKSHEET"]
    assert pkg.execution_result.success is True
    assert pkg.fidelity_report.overall_fidelity_score >= 0.95
    assert pkg.quality_report.overall_quality_score >= 0.80


def test_08_dinamika_rotasi_scientific(execution_matrix):
    pkg = execution_matrix["02_dinamika_rotasi"]["SCIENTIFIC_DOCUMENT"]
    assert pkg.execution_result.success is True
    assert pkg.fidelity_report.overall_fidelity_score >= 0.95
    assert pkg.quality_report.overall_quality_score >= 0.80


# ============================================================================
# 3. FIXTURE 03: GERAK MELINGKAR (4 Artifacts)
# ============================================================================

def test_09_gerak_melingkar_presentation(execution_matrix):
    pkg = execution_matrix["03_gerak_melingkar"]["PRESENTATION"]
    assert pkg.execution_result.success is True
    assert pkg.quality_report.overall_quality_score >= 0.80


def test_10_gerak_melingkar_handout(execution_matrix):
    pkg = execution_matrix["03_gerak_melingkar"]["HANDOUT"]
    assert pkg.execution_result.success is True
    assert pkg.quality_report.overall_quality_score >= 0.80


def test_11_gerak_melingkar_worksheet(execution_matrix):
    pkg = execution_matrix["03_gerak_melingkar"]["WORKSHEET"]
    assert pkg.execution_result.success is True
    assert pkg.quality_report.overall_quality_score >= 0.80


def test_12_gerak_melingkar_scientific(execution_matrix):
    pkg = execution_matrix["03_gerak_melingkar"]["SCIENTIFIC_DOCUMENT"]
    assert pkg.execution_result.success is True
    assert pkg.quality_report.overall_quality_score >= 0.80


# ============================================================================
# 4. FIXTURE 04: HAND FIRE (4 Artifacts)
# ============================================================================

def test_13_hand_fire_presentation(execution_matrix):
    pkg = execution_matrix["04_hand_fire"]["PRESENTATION"]
    assert pkg.execution_result.success is True
    assert pkg.quality_report.overall_quality_score >= 0.80


def test_14_hand_fire_handout(execution_matrix):
    pkg = execution_matrix["04_hand_fire"]["HANDOUT"]
    assert pkg.execution_result.success is True
    assert pkg.quality_report.overall_quality_score >= 0.80


def test_15_hand_fire_worksheet(execution_matrix):
    pkg = execution_matrix["04_hand_fire"]["WORKSHEET"]
    assert pkg.execution_result.success is True
    assert pkg.quality_report.overall_quality_score >= 0.80


def test_16_hand_fire_scientific(execution_matrix):
    pkg = execution_matrix["04_hand_fire"]["SCIENTIFIC_DOCUMENT"]
    assert pkg.execution_result.success is True
    assert pkg.quality_report.overall_quality_score >= 0.80


# ============================================================================
# 5. FIXTURE 05: SHORT CONCEPT (4 Artifacts)
# ============================================================================

def test_17_short_concept_presentation(execution_matrix):
    pkg = execution_matrix["05_short_concept"]["PRESENTATION"]
    assert pkg.execution_result.success is True
    assert pkg.quality_report.overall_quality_score >= 0.80


def test_18_short_concept_handout(execution_matrix):
    pkg = execution_matrix["05_short_concept"]["HANDOUT"]
    assert pkg.execution_result.success is True
    assert pkg.quality_report.overall_quality_score >= 0.80


def test_19_short_concept_worksheet(execution_matrix):
    pkg = execution_matrix["05_short_concept"]["WORKSHEET"]
    assert pkg.execution_result.success is True
    assert pkg.quality_report.overall_quality_score >= 0.80


def test_20_short_concept_scientific(execution_matrix):
    pkg = execution_matrix["05_short_concept"]["SCIENTIFIC_DOCUMENT"]
    assert pkg.execution_result.success is True
    assert pkg.quality_report.overall_quality_score >= 0.80


# ============================================================================
# 6. FIXTURE 06: LONG MATERIAL (4 Artifacts)
# ============================================================================

def test_21_long_material_presentation(execution_matrix):
    pkg = execution_matrix["06_long_material"]["PRESENTATION"]
    assert pkg.execution_result.success is True
    assert pkg.quality_report.overall_quality_score >= 0.80


def test_22_long_material_handout(execution_matrix):
    pkg = execution_matrix["06_long_material"]["HANDOUT"]
    assert pkg.execution_result.success is True
    assert pkg.quality_report.overall_quality_score >= 0.80


def test_23_long_material_worksheet(execution_matrix):
    pkg = execution_matrix["06_long_material"]["WORKSHEET"]
    assert pkg.execution_result.success is True
    assert pkg.quality_report.overall_quality_score >= 0.80


def test_24_long_material_scientific(execution_matrix):
    pkg = execution_matrix["06_long_material"]["SCIENTIFIC_DOCUMENT"]
    assert pkg.execution_result.success is True
    assert pkg.quality_report.overall_quality_score >= 0.80


# ============================================================================
# 7. FIXTURE 07: DATA HEAVY RESEARCH (4 Artifacts)
# ============================================================================

def test_25_data_heavy_research_presentation(execution_matrix):
    pkg = execution_matrix["07_data_heavy_research"]["PRESENTATION"]
    assert pkg.execution_result.success is True
    assert pkg.quality_report.overall_quality_score >= 0.80


def test_26_data_heavy_research_handout(execution_matrix):
    pkg = execution_matrix["07_data_heavy_research"]["HANDOUT"]
    assert pkg.execution_result.success is True
    assert pkg.quality_report.overall_quality_score >= 0.80


def test_27_data_heavy_research_worksheet(execution_matrix):
    pkg = execution_matrix["07_data_heavy_research"]["WORKSHEET"]
    assert pkg.execution_result.success is True
    assert pkg.quality_report.overall_quality_score >= 0.80


def test_28_data_heavy_research_scientific(execution_matrix):
    pkg = execution_matrix["07_data_heavy_research"]["SCIENTIFIC_DOCUMENT"]
    assert pkg.execution_result.success is True
    assert pkg.quality_report.overall_quality_score >= 0.80


# ============================================================================
# 8. MATRIX & STATISTICAL CALIBRATION VERIFICATION (Tests 29 - 36)
# ============================================================================

def test_29_quality_matrix_report_persisted(execution_matrix):
    """29. Both Markdown and JSON matrix reports exist and have 28 entries."""
    md_file = OUTPUT_DIR / "reports" / "benchmark_quality_matrix.md"
    json_file = OUTPUT_DIR / "reports" / "benchmark_quality_matrix.json"

    assert md_file.exists(), f"Missing markdown report at {md_file}"
    assert json_file.exists(), f"Missing JSON report at {json_file}"

    data = json.loads(json_file.read_text(encoding="utf-8"))
    assert data["total_entries"] == 28
    assert len(data["entries"]) == 28


def test_30_statistical_score_distribution(execution_matrix):
    """30. Quality scores exhibit non-degenerate variance across artifacts."""
    scores: List[float] = []
    for fixture_pkg in execution_matrix.values():
        for pkg in fixture_pkg.values():
            scores.append(pkg.quality_report.overall_quality_score)

    assert len(scores) == 28
    mean_score = statistics.mean(scores)
    std_dev = statistics.stdev(scores)

    assert 0.80 <= mean_score <= 1.0
    assert std_dev > 0.001, f"Zero variance detected in quality scores: std_dev={std_dev}"
    assert min(scores) >= 0.75
    assert max(scores) <= 1.0


def test_31_non_degeneracy_detection(execution_matrix):
    """31. QualityScoreDegeneracyDetector confirms healthy variance."""
    reports: List[ArtifactQualityReport] = []
    for fixture_pkg in execution_matrix.values():
        for pkg in fixture_pkg.values():
            reports.append(pkg.quality_report)

    degeneracy = QualityScoreDegeneracyDetector.detect(reports)
    assert degeneracy is None, f"Degeneracy detected in production benchmark: {degeneracy}"


def test_32_calibrated_decision_arbitration(execution_matrix):
    """32. All clean baselines receive PASS or PASS_WITH_WARNINGS (no false positive BLOCKED)."""
    for f_stem, fixture_pkg in execution_matrix.items():
        for a_type, pkg in fixture_pkg.items():
            assert pkg.decision.can_export is True, (
                f"Unexpected BLOCKED decision on clean baseline: {f_stem} ({a_type}) - "
                f"Blockers: {pkg.decision.blocking_failures}"
            )
            assert pkg.decision.overall_decision in (
                QualityDecisionStatus.PASS,
                QualityDecisionStatus.PASS_WITH_WARNINGS,
            )


def test_33_baseline_regression_compliance(execution_matrix):
    """33. Matrix results comply with quality regression baseline thresholds."""
    assert BASELINES_FILE.exists(), f"Baselines file missing: {BASELINES_FILE}"
    baselines = json.loads(BASELINES_FILE.read_text(encoding="utf-8"))["baselines"]

    # Check presentation good case
    pres_min = baselines["presentation_good_case"]["minimum_quality_score"]
    for fixture_pkg in execution_matrix.values():
        assert fixture_pkg["PRESENTATION"].quality_report.overall_quality_score >= pres_min

    # Check handout good case
    handout_min = baselines["handout_good_case"]["minimum_quality_score"]
    for fixture_pkg in execution_matrix.values():
        assert fixture_pkg["HANDOUT"].quality_report.overall_quality_score >= handout_min

    # Check worksheet good case
    ws_min = baselines["worksheet_good_case"]["minimum_quality_score"]
    for fixture_pkg in execution_matrix.values():
        assert fixture_pkg["WORKSHEET"].quality_report.overall_quality_score >= ws_min

    # Check scientific good case
    sci_min = baselines["scientific_good_case"]["minimum_quality_score"]
    for fixture_pkg in execution_matrix.values():
        assert fixture_pkg["SCIENTIFIC_DOCUMENT"].quality_report.overall_quality_score >= sci_min


def test_34_visual_contact_sheets_generated(execution_matrix):
    """34. Visual contact sheets exist and are non-empty for Presentation and Handout."""
    for f_stem, fixture_pkg in execution_matrix.items():
        pres_cs = fixture_pkg["PRESENTATION"].contact_sheet_path
        assert pres_cs is not None and pres_cs.exists()
        assert pres_cs.stat().st_size > 1000, f"Empty presentation contact sheet: {pres_cs}"

        handout_cs = fixture_pkg["HANDOUT"].contact_sheet_path
        assert handout_cs is not None and handout_cs.exists()
        assert handout_cs.stat().st_size > 1000, f"Empty handout contact sheet: {handout_cs}"


def test_35_physical_html_and_pdf_artifacts(execution_matrix):
    """35. All 28 artifacts produce valid HTML and PDF on disk."""
    for f_stem, fixture_pkg in execution_matrix.items():
        for a_type, pkg in fixture_pkg.items():
            res = pkg.execution_result
            assert res.html_path is not None and res.html_path.exists()
            assert res.html_path.stat().st_size > 100
            assert res.pdf_path is not None and res.pdf_path.exists()
            assert res.pdf_path.stat().st_size > 500


def test_36_zero_ai_guarantee(execution_matrix):
    """36. Strictly zero LLM / AI dependencies in calibration and scoring."""
    import sys
    for fixture_pkg in execution_matrix.values():
        for pkg in fixture_pkg.values():
            # Verify explanations and findings contain no LLM tokens
            for s in pkg.quality_report.signals:
                assert "openai" not in s.signal.lower()
                assert "gemini" not in s.signal.lower()
                assert "claude" not in s.signal.lower()
            for f in pkg.quality_report.findings:
                assert "ai generated" not in f.finding.lower()
