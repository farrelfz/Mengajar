"""
Universal Knowledge Core — Controlled Renderer Execution Test Suite.

Phase 2B Controlled Renderer Execution & Artifact Fidelity:
Comprehensive integration test suite verifying that all four legacy renderers
(Presentation, Handout, Worksheet, Scientific Document) consume adapter outputs
and produce high-fidelity rendered HTML, PDF, and visual contact sheets without
semantic, structural, pedagogical, scientific, or visual contract corruption.

Tests:
1-4: Executor instantiation and contract compliance
5-9: Presentation Renderer Execution & Visual Validation
10-13: Handout Renderer Execution & Reading Hierarchy Validation
14-18: Worksheet Renderer Execution & Anti-Spoiling Integrity Validation
19-22: Scientific Document Execution & Evidence Grounding Validation
23-25: End-to-End System Fidelity Evaluation & Contact Sheet Verification
"""

import asyncio
from pathlib import Path
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
    RendererExecutor,
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
from app.quality.artifact_fidelity import (
    ArtifactFidelityEvaluation,
    ComprehensiveFidelityReport,
    UnifiedFidelityValidator,
)

FIXTURE_PATH = Path(__file__).parent.parent / "fixtures" / "oobleck_experiment.md"
OUTPUT_DIR = Path(__file__).parent.parent.parent / "outputs" / "benchmark" / "phase_2b"


@pytest.fixture(scope="module")
def oobleck_manifest() -> UniversalKnowledgeManifest:
    assert FIXTURE_PATH.exists(), f"Fixture missing at {FIXTURE_PATH}"
    raw_md = FIXTURE_PATH.read_text(encoding="utf-8")
    compiler = KnowledgeCompiler(resolution_provider=OfflineMockResolutionProvider())
    manifest = asyncio.run(compiler.compile(raw_md, source_filename="oobleck_experiment.md"))
    return manifest


@pytest.fixture(scope="module")
def pres_render_artifact(oobleck_manifest) -> RenderArtifact:
    engine = KnowledgeSelectionEngine()
    intent = get_default_intent(ArtifactType.PRESENTATION)
    bp = PresentationTransformer().transform(oobleck_manifest, engine.select(oobleck_manifest, intent), intent)
    return PresentationBlueprintBridge().bridge(bp)


@pytest.fixture(scope="module")
def handout_render_artifact(oobleck_manifest) -> RenderArtifact:
    engine = KnowledgeSelectionEngine()
    intent = get_default_intent(ArtifactType.HANDOUT)
    bp = HandoutTransformer().transform(oobleck_manifest, engine.select(oobleck_manifest, intent), intent)
    return HandoutBlueprintBridge().bridge(bp)


@pytest.fixture(scope="module")
def worksheet_render_artifact(oobleck_manifest) -> RenderArtifact:
    engine = KnowledgeSelectionEngine()
    intent = get_default_intent(ArtifactType.WORKSHEET)
    bp = WorksheetTransformer().transform(oobleck_manifest, engine.select(oobleck_manifest, intent), intent)
    return WorksheetBlueprintBridge().bridge(bp)


@pytest.fixture(scope="module")
def scientific_render_artifact(oobleck_manifest) -> RenderArtifact:
    engine = KnowledgeSelectionEngine()
    intent = get_default_intent(ArtifactType.SCIENTIFIC_DOCUMENT)
    bp = ScientificDocumentTransformer().transform(oobleck_manifest, engine.select(oobleck_manifest, intent), intent)
    return ScientificDocumentBlueprintBridge().bridge(bp)


# ============================================================================
# 1. EXECUTOR CONTRACT COMPLIANCE (Tests 1 - 4)
# ============================================================================

def test_01_presentation_executor_contract():
    """1. PresentationExecutor implements RendererExecutor interface."""
    executor = PresentationExecutor()
    assert isinstance(executor, RendererExecutor)
    assert executor.supported_artifact_type == "PRESENTATION"


def test_02_handout_executor_contract():
    """2. HandoutExecutor implements RendererExecutor interface."""
    executor = HandoutExecutor()
    assert isinstance(executor, RendererExecutor)
    assert executor.supported_artifact_type == "HANDOUT"


def test_03_worksheet_executor_contract():
    """3. WorksheetExecutor implements RendererExecutor interface."""
    executor = WorksheetExecutor()
    assert isinstance(executor, RendererExecutor)
    assert executor.supported_artifact_type == "WORKSHEET"


def test_04_scientific_document_executor_contract():
    """4. ScientificDocumentExecutor implements RendererExecutor interface."""
    executor = ScientificDocumentExecutor()
    assert isinstance(executor, RendererExecutor)
    assert executor.supported_artifact_type == "SCIENTIFIC_DOCUMENT"


# ============================================================================
# 2. PRESENTATION EXECUTION & VISUAL VALIDATION (Tests 5 - 9)
# ============================================================================

def test_05_presentation_render_success(pres_render_artifact):
    """5. PresentationExecutor renders valid HTML and PDF for presentation deck."""
    executor = PresentationExecutor()
    out_dir = OUTPUT_DIR / "presentation"
    res = executor.execute_from_render_artifact(
        pres_render_artifact,
        output_dir=out_dir,
        output_filename="test_pres",
    )

    assert res.success is True
    assert res.artifact_type == "PRESENTATION"
    assert res.total_pages >= 12
    assert res.html_path is not None and res.html_path.exists()
    assert res.pdf_path is not None and res.pdf_path.exists()
    assert res.pdf_path.stat().st_size > 1000


def test_06_presentation_source_traceability_preserved(pres_render_artifact):
    """6. All source units in presentation RenderArtifact are rendered."""
    executor = PresentationExecutor()
    out_dir = OUTPUT_DIR / "presentation"
    res = executor.execute_from_render_artifact(
        pres_render_artifact,
        output_dir=out_dir,
        output_filename="test_pres_trace",
    )

    source_bp_ids = {u.traceability_refs.blueprint_element_id for u in pres_render_artifact.units}
    rendered_ids = set(res.source_element_ids_rendered)
    assert source_bp_ids.issubset(rendered_ids)


def test_07_presentation_html_contains_required_classes(pres_render_artifact):
    """7. Presentation rendered HTML contains proper 16:9 page and card classes."""
    executor = PresentationExecutor()
    out_dir = OUTPUT_DIR / "presentation"
    res = executor.execute_from_render_artifact(
        pres_render_artifact,
        output_dir=out_dir,
        output_filename="test_pres_classes",
    )

    html_text = res.html_path.read_text(encoding="utf-8")
    assert "page-presentation" in html_text
    assert "slide-header" in html_text
    assert "slide-content-area" in html_text


def test_08_presentation_contact_sheet_generated(pres_render_artifact):
    """8. Contact sheet PNG generated from presentation PDF via PyMuPDF."""
    out_dir = OUTPUT_DIR / "presentation"
    pdf_p = out_dir / "test_pres.pdf"
    img_p = out_dir / "test_pres_contact_sheet.png"

    cs_gen = ContactSheetGenerator(columns=4, scale=0.35)
    result_img = cs_gen.generate(pdf_p, img_p)

    assert result_img.exists()
    assert result_img.stat().st_size > 5000


def test_09_presentation_fidelity_score(pres_render_artifact):
    """9. Presentation execution achieves >= 0.85 fidelity score."""
    deck = PresentationContractAdapter().adapt(pres_render_artifact)
    res = PresentationExecutor().execute(deck, output_dir=OUTPUT_DIR / "presentation", output_filename="test_pres_fid")

    validator = UnifiedFidelityValidator()
    eval_res = validator.evaluate_artifact(pres_render_artifact, deck, res)

    assert eval_res.is_passing is True
    assert eval_res.overall_score >= 0.85
    assert eval_res.semantic_fidelity == 1.0


# ============================================================================
# 3. HANDOUT EXECUTION & READING HIERARCHY (Tests 10 - 13)
# ============================================================================

def test_10_handout_render_success(handout_render_artifact):
    """10. HandoutExecutor renders valid HTML and PDF for continuous reading material."""
    executor = HandoutExecutor()
    out_dir = OUTPUT_DIR / "handout"
    res = executor.execute_from_render_artifact(
        handout_render_artifact,
        output_dir=out_dir,
        output_filename="test_handout",
    )

    assert res.success is True
    assert res.artifact_type == "HANDOUT"
    assert res.total_pages >= 1
    assert res.html_path is not None and res.html_path.exists()
    assert res.pdf_path is not None and res.pdf_path.exists()


def test_11_handout_html_structure(handout_render_artifact):
    """11. Handout HTML contains A4 portrait container and definition callouts."""
    executor = HandoutExecutor()
    out_dir = OUTPUT_DIR / "handout"
    res = executor.execute_from_render_artifact(
        handout_render_artifact,
        output_dir=out_dir,
        output_filename="test_handout_struct",
    )

    html_text = res.html_path.read_text(encoding="utf-8")
    assert "page-a4-portrait" in html_text
    assert "handout-section" in html_text
    assert "DEFINISI KONSEP" in html_text


def test_12_handout_contact_sheet_generated(handout_render_artifact):
    """12. Contact sheet PNG generated from handout PDF."""
    out_dir = OUTPUT_DIR / "handout"
    pdf_p = out_dir / "test_handout.pdf"
    img_p = out_dir / "test_handout_contact_sheet.png"

    cs_gen = ContactSheetGenerator(columns=4, scale=0.30)
    result_img = cs_gen.generate(pdf_p, img_p)

    assert result_img.exists()
    assert result_img.stat().st_size > 5000


def test_13_handout_fidelity_score(handout_render_artifact):
    """13. Handout execution achieves >= 0.85 fidelity score."""
    content = HandoutContractAdapter().adapt(handout_render_artifact)
    res = HandoutExecutor().execute(content, output_dir=OUTPUT_DIR / "handout", output_filename="test_handout_fid")

    validator = UnifiedFidelityValidator()
    eval_res = validator.evaluate_artifact(handout_render_artifact, content, res)

    assert eval_res.is_passing is True
    assert eval_res.overall_score >= 0.85
    assert eval_res.structural_fidelity == 1.0


# ============================================================================
# 4. WORKSHEET EXECUTION & ANTI-SPOILING INTEGRITY (Tests 14 - 18)
# ============================================================================

def test_14_worksheet_render_success(worksheet_render_artifact):
    """14. WorksheetExecutor renders valid HTML and PDF with student workspace."""
    executor = WorksheetExecutor()
    out_dir = OUTPUT_DIR / "worksheet"
    res = executor.execute_from_render_artifact(
        worksheet_render_artifact,
        output_dir=out_dir,
        output_filename="test_ws",
    )

    assert res.success is True
    assert res.artifact_type == "WORKSHEET"
    assert res.total_pages >= 5
    assert res.html_path is not None and res.html_path.exists()
    assert res.pdf_path is not None and res.pdf_path.exists()


def test_15_worksheet_anti_spoiling_withholding_enforced(worksheet_render_artifact):
    """15. Anti-spoiling: withhold_explanation=True is verified across all activities."""
    doc = WorksheetContractAdapter().adapt(worksheet_render_artifact, grouping_mode="compatibility")

    for sec in doc.sections:
        for act in sec.activities:
            assert act.withhold_explanation is True


def test_16_worksheet_student_workspace_boxes_rendered(worksheet_render_artifact):
    """16. Worksheet HTML renders dedicated student workspace boxes."""
    executor = WorksheetExecutor()
    out_dir = OUTPUT_DIR / "worksheet"
    res = executor.execute_from_render_artifact(
        worksheet_render_artifact,
        output_dir=out_dir,
        output_filename="test_ws_workspace",
    )

    html_text = res.html_path.read_text(encoding="utf-8")
    assert "student-workspace-box" in html_text
    assert "Ruang Kerja &amp; Catatan Siswa" in html_text or "Ruang Kerja & Catatan Siswa" in html_text


def test_17_worksheet_contact_sheet_generated(worksheet_render_artifact):
    """17. Contact sheet PNG generated from worksheet PDF."""
    out_dir = OUTPUT_DIR / "worksheet"
    pdf_p = out_dir / "test_ws.pdf"
    img_p = out_dir / "test_ws_contact_sheet.png"

    cs_gen = ContactSheetGenerator(columns=4, scale=0.30)
    result_img = cs_gen.generate(pdf_p, img_p)

    assert result_img.exists()
    assert result_img.stat().st_size > 5000


def test_18_worksheet_fidelity_score(worksheet_render_artifact):
    """18. Worksheet execution achieves >= 0.85 fidelity score."""
    doc = WorksheetContractAdapter().adapt(worksheet_render_artifact, grouping_mode="compatibility")
    res = WorksheetExecutor().execute(doc, output_dir=OUTPUT_DIR / "worksheet", output_filename="test_ws_fid")

    validator = UnifiedFidelityValidator()
    eval_res = validator.evaluate_artifact(worksheet_render_artifact, doc, res)

    assert eval_res.is_passing is True
    assert eval_res.overall_score >= 0.85
    assert eval_res.artifact_specific_fidelity == 1.0


# ============================================================================
# 5. SCIENTIFIC DOCUMENT EXECUTION & EVIDENCE GROUNDING (Tests 19 - 22)
# ============================================================================

def test_19_scientific_document_render_success(scientific_render_artifact):
    """19. ScientificDocumentExecutor renders valid KTI HTML and PDF."""
    executor = ScientificDocumentExecutor()
    out_dir = OUTPUT_DIR / "scientific_document"
    res = executor.execute_from_render_artifact(
        scientific_render_artifact,
        output_dir=out_dir,
        output_filename="test_sci",
    )

    assert res.success is True
    assert res.artifact_type == "SCIENTIFIC_DOCUMENT"
    assert res.total_pages >= 5
    assert res.html_path is not None and res.html_path.exists()
    assert res.pdf_path is not None and res.pdf_path.exists()


def test_20_scientific_kti_chapters_rendered(scientific_render_artifact):
    """20. Scientific HTML renders Indonesian KTI BAB headers."""
    executor = ScientificDocumentExecutor()
    out_dir = OUTPUT_DIR / "scientific_document"
    res = executor.execute_from_render_artifact(
        scientific_render_artifact,
        output_dir=out_dir,
        output_filename="test_sci_chapters",
    )

    html_text = res.html_path.read_text(encoding="utf-8")
    assert "BAB I: PENDAHULUAN" in html_text
    assert "BAB II: TINJAUAN PUSTAKA" in html_text
    assert "BAB III: METODOLOGI PENELITIAN" in html_text
    assert "BAB IV: HASIL DAN PEMBAHASAN" in html_text
    assert "BAB V: KESIMPULAN DAN SARAN" in html_text


def test_21_scientific_evidence_and_citations_rendered(scientific_render_artifact):
    """21. Scientific HTML renders explicit evidence citation tags and panels."""
    executor = ScientificDocumentExecutor()
    out_dir = OUTPUT_DIR / "scientific_document"
    res = executor.execute_from_render_artifact(
        scientific_render_artifact,
        output_dir=out_dir,
        output_filename="test_sci_evidence",
    )

    html_text = res.html_path.read_text(encoding="utf-8")
    assert "Landasan Bukti Empiris" in html_text
    assert "Bukti:" in html_text


def test_22_scientific_fidelity_score(scientific_render_artifact):
    """22. Scientific document execution achieves >= 0.85 fidelity score."""
    doc = ScientificDocumentContractAdapter().adapt(scientific_render_artifact)
    res = ScientificDocumentExecutor().execute(doc, output_dir=OUTPUT_DIR / "scientific_document", output_filename="test_sci_fid")

    validator = UnifiedFidelityValidator()
    eval_res = validator.evaluate_artifact(scientific_render_artifact, doc, res)

    assert eval_res.is_passing is True
    assert eval_res.overall_score >= 0.85
    assert eval_res.structural_fidelity == 1.0


# ============================================================================
# 6. SYSTEM-WIDE FIDELITY & BENCHMARK INTEGRITY (Tests 23 - 25)
# ============================================================================

def test_23_zero_dropped_source_elements_across_all_four_artifacts(
    pres_render_artifact,
    handout_render_artifact,
    worksheet_render_artifact,
    scientific_render_artifact,
):
    """23. Zero dropped source elements invariant holds across all four rendered artifacts."""
    out_base = OUTPUT_DIR / "invariants"

    pres_res = PresentationExecutor().execute_from_render_artifact(
        pres_render_artifact, out_base / "pres", "pres_inv"
    )
    handout_res = HandoutExecutor().execute_from_render_artifact(
        handout_render_artifact, out_base / "handout", "handout_inv"
    )
    ws_res = WorksheetExecutor().execute_from_render_artifact(
        worksheet_render_artifact, out_base / "ws", "ws_inv"
    )
    sci_res = ScientificDocumentExecutor().execute_from_render_artifact(
        scientific_render_artifact, out_base / "sci", "sci_inv"
    )

    # 1. Pres
    pres_src = {u.traceability_refs.blueprint_element_id for u in pres_render_artifact.units}
    assert pres_src.issubset(set(pres_res.source_element_ids_rendered))

    # 2. Handout
    handout_src = {u.traceability_refs.blueprint_element_id for u in handout_render_artifact.units}
    assert handout_src.issubset(set(handout_res.source_element_ids_rendered))

    # 3. Worksheet
    ws_src = {u.traceability_refs.blueprint_element_id for u in worksheet_render_artifact.units}
    assert ws_src.issubset(set(ws_res.source_element_ids_rendered))

    # 4. Scientific
    sci_src = {u.traceability_refs.blueprint_element_id for u in scientific_render_artifact.units}
    assert sci_src.issubset(set(sci_res.source_element_ids_rendered))


def test_24_comprehensive_system_fidelity_report(
    pres_render_artifact,
    handout_render_artifact,
    worksheet_render_artifact,
    scientific_render_artifact,
):
    """24. UnifiedFidelityValidator produces passing ComprehensiveFidelityReport with macro score >= 0.90."""
    out_base = OUTPUT_DIR / "benchmark_run"

    p_deck = PresentationContractAdapter().adapt(pres_render_artifact)
    p_exec = PresentationExecutor().execute(p_deck, out_base / "p", "p")

    h_content = HandoutContractAdapter().adapt(handout_render_artifact)
    h_exec = HandoutExecutor().execute(h_content, out_base / "h", "h")

    w_doc = WorksheetContractAdapter().adapt(worksheet_render_artifact, grouping_mode="compatibility")
    w_exec = WorksheetExecutor().execute(w_doc, out_base / "w", "w")

    s_doc = ScientificDocumentContractAdapter().adapt(scientific_render_artifact)
    s_exec = ScientificDocumentExecutor().execute(s_doc, out_base / "s", "s")

    data = {
        "PRESENTATION": (pres_render_artifact, p_deck, p_exec),
        "HANDOUT": (handout_render_artifact, h_content, h_exec),
        "WORKSHEET": (worksheet_render_artifact, w_doc, w_exec),
        "SCIENTIFIC_DOCUMENT": (scientific_render_artifact, s_doc, s_exec),
    }

    validator = UnifiedFidelityValidator()
    report = validator.evaluate_system(data, manifest_title="Oobleck Non-Newtonian Benchmark")

    assert report.all_passing is True
    assert report.macro_fidelity_score >= 0.90
    assert report.total_violations == 0

    md_report = report.to_markdown()
    assert "# PHASE 2B CONTROLLED RENDERER FIDELITY REPORT" in md_report
    assert "Macro Fidelity Score" in md_report


def test_25_all_contact_sheets_exist_and_non_empty():
    """25. Contact sheets for all 4 artifacts exist in benchmark output directory."""
    cs_paths = [
        OUTPUT_DIR / "presentation" / "presentation_contact_sheet.png",
        OUTPUT_DIR / "handout" / "handout_contact_sheet.png",
        OUTPUT_DIR / "worksheet" / "worksheet_contact_sheet.png",
        OUTPUT_DIR / "scientific_document" / "scientific_contact_sheet.png",
    ]

    for p in cs_paths:
        assert p.exists(), f"Contact sheet missing at {p}"
        assert p.stat().st_size > 1000, f"Contact sheet empty at {p}"
