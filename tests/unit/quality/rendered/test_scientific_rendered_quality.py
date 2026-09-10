"""
Unit tests for ScientificRenderedQualityEvaluator.

Phase 3A: Independent rendered evaluation of academic scientific papers / KTI:
- Formal BAB 1–5 / IMRAD chapter hierarchy consistency
- Claim-to-evidence proximity and table/chart context
- In-text citation visibility and bibliographic integrity
- Real rendered scientific document evaluation
"""

import pytest
import pymupdf as fitz
from pathlib import Path

from app.quality.rendered.scientific_quality import ScientificRenderedQualityEvaluator
from app.quality.rendered.failure_taxonomy import RenderedFailureCode, RenderedFailureSeverity
from app.quality.rendered.contracts import RenderedQualityDecision


@pytest.fixture
def temp_pdf_dir(tmp_path: Path) -> Path:
    return tmp_path / "scientific_quality_tests"


def test_01_scientific_valid_hierarchy_and_citations_passes(temp_pdf_dir: Path):
    temp_pdf_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = temp_pdf_dir / "clean_scientific.pdf"

    doc = fitz.open()
    # Page 1: BAB I
    p1 = doc.new_page(width=595.3, height=841.9)
    p1.insert_text((54, 70), "BAB I PENDAHULUAN", fontsize=14)
    p1.insert_textbox(
        fitz.Rect(54, 90, 541, 700),
        "Fluida non-Newtonian merupakan sistem multifasa yang menunjukkan perilaku reologi kompleks [1]. Penelitian ini bertujuan untuk mengkarakterisasi respons mekanis suspensi pati jagung dalam medium air saat mengalami laju geser tinggi [2].",
        fontsize=10.5,
    )

    # Page 2: BAB II
    p2 = doc.new_page(width=595.3, height=841.9)
    p2.insert_text((54, 70), "BAB II TINJAUAN PUSTAKA", fontsize=14)
    p2.insert_textbox(
        fitz.Rect(54, 90, 541, 700),
        "Menurut teori hidrodinamika suspensi koloid (Barnes, 1989), viskositas fluida meningkat tajam akibat formasi hidrogugus partikel. Tabel 1 merangkum perbandingan koefisien viskositas berbagai jenis fluida.",
        fontsize=10.5,
    )

    # Page 3: BAB III
    p3 = doc.new_page(width=595.3, height=841.9)
    p3.insert_text((54, 70), "BAB III METODE PENELITIAN", fontsize=14)
    p3.insert_textbox(
        fitz.Rect(54, 90, 541, 700),
        "Metode eksperimental menggunakan rheometer putar dan uji impak mekanik [3]. Data direkam secara digital dengan frekuensi pencuplikan 1000 Hz.",
        fontsize=10.5,
    )

    doc.save(str(pdf_path))
    doc.close()

    evaluator = ScientificRenderedQualityEvaluator()
    result = evaluator.evaluate(pdf_path)

    assert result.artifact_type == "SCIENTIFIC_DOCUMENT"
    assert result.page_count == 3
    assert not result.has_critical_failures
    assert result.decision in (RenderedQualityDecision.PASS, RenderedQualityDecision.PASS_WITH_WARNINGS)
    assert result.can_export is True
    assert result.artifact_specific_metrics.get("citations_found_count", 0) >= 3


def test_02_scientific_bab_hierarchy_inversion_critical(temp_pdf_dir: Path):
    temp_pdf_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = temp_pdf_dir / "inverted_scientific.pdf"

    doc = fitz.open()
    # Inverted order: BAB II appears on page 1 before BAB I on page 2
    p1 = doc.new_page(width=595.3, height=841.9)
    p1.insert_text((54, 70), "BAB II TINJAUAN PUSTAKA", fontsize=14)
    p1.insert_textbox(fitz.Rect(54, 90, 541, 400), "Tinjauan pustaka diletakkan di awal [1]...", fontsize=10.5)

    p2 = doc.new_page(width=595.3, height=841.9)
    p2.insert_text((54, 70), "BAB I PENDAHULUAN", fontsize=14)
    p2.insert_textbox(fitz.Rect(54, 90, 541, 400), "Pendahuluan terlambat diletakkan di halaman 2 [2]...", fontsize=10.5)

    doc.save(str(pdf_path))
    doc.close()

    evaluator = ScientificRenderedQualityEvaluator()
    result = evaluator.evaluate(pdf_path)

    assert result.has_critical_failures is True
    assert result.can_export is False
    assert result.decision == RenderedQualityDecision.BLOCKED
    inv_fails = [f for f in result.critical_failures if f.code == RenderedFailureCode.SCIENTIFIC_HIERARCHY_FAILURE]
    assert len(inv_fails) >= 1


def test_03_scientific_invisible_citations_detected(temp_pdf_dir: Path):
    temp_pdf_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = temp_pdf_dir / "uncited_scientific.pdf"

    doc = fitz.open()
    # 3-page scientific document without any citation tags like [1] or (Author, Year)
    for i in range(1, 4):
        p = doc.new_page(width=595.3, height=841.9)
        p.insert_text((54, 70), f"BAB {i} BAGIAN KARYA ILMIAH", fontsize=14)
        p.insert_textbox(fitz.Rect(54, 90, 541, 600), "Klaim ilmiah tanpa menyertakan referensi akademik sama sekali dalam naskah tulisan...", fontsize=10.5)

    doc.save(str(pdf_path))
    doc.close()

    evaluator = ScientificRenderedQualityEvaluator()
    result = evaluator.evaluate(pdf_path)

    assert any(f.code == RenderedFailureCode.SCIENTIFIC_CITATION_INVISIBLE for f in result.major_warnings)


def test_04_scientific_real_fixture_truthful_evaluation():
    real_pdf = Path("outputs/benchmark/phase_2c/artifacts/01_oobleck_experiment/scientific/scientific.pdf")
    if not real_pdf.exists():
        pytest.skip("Phase 2C scientific artifact not available")

    evaluator = ScientificRenderedQualityEvaluator()
    result = evaluator.evaluate(real_pdf)

    assert result.artifact_type == "SCIENTIFIC_DOCUMENT"
    assert result.page_count == 10
    # In Phase 2C output, zero citations were rendered in the body -> truthful diagnostic caught it!
    assert any(f.code == RenderedFailureCode.SCIENTIFIC_CITATION_INVISIBLE for f in result.major_warnings)
    assert result.overall_quality_score > 0.80
