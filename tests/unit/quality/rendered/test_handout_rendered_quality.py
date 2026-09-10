"""
Unit tests for HandoutRenderedQualityEvaluator.

Phase 3A: Independent rendered evaluation of A4 reading handouts:
- Continuous reading flow & paragraphs
- Orphan heading detection at page break
- Wall of text detection
- Real rendered handout evaluation
"""

import pytest
import pymupdf as fitz
from pathlib import Path

from app.quality.rendered.handout_quality import HandoutRenderedQualityEvaluator
from app.quality.rendered.failure_taxonomy import RenderedFailureCode, RenderedFailureSeverity
from app.quality.rendered.contracts import RenderedQualityDecision


@pytest.fixture
def temp_pdf_dir(tmp_path: Path) -> Path:
    return tmp_path / "handout_quality_tests"


def test_01_handout_clean_reading_flow_passes(temp_pdf_dir: Path):
    temp_pdf_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = temp_pdf_dir / "clean_handout.pdf"

    doc = fitz.open()
    # Page 1: A4 (595.3 x 841.9)
    p1 = doc.new_page(width=595.3, height=841.9)
    p1.insert_text((54, 70), "MODUL AJAR: MEKANIKA FLUIDA", fontsize=18)
    p1.insert_textbox(
        fitz.Rect(54, 100, 541, 350),
        "Fluida non-Newtonian adalah kelompok fluida yang viskositasnya berubah tergantung pada laju regangan geser atau tegangan geser yang diterapkan. Berbeda dengan fluida Newtonian seperti air dan minyak tanah di mana viskositas konstan pada suhu konstan.",
        fontsize=10.5,
    )
    p1.insert_text((54, 380), "1. Karakteristik Rheologi Suspensi Pati", fontsize=14)
    p1.insert_textbox(
        fitz.Rect(54, 410, 541, 750),
        "Pada konsentrasi tinggi antara tepung pati jagung dan air dengan perbandingan massa tertentu, terbentuk suspensi koloidal padat. Ketika gaya eksternal diberikan perlahan, partikel pati sempat bergeser relatif satu sama lain karena terlumasi oleh molekul air. Sebaliknya ketika gaya impulsif tiba-tiba diberikan, lapisan air terdorong keluar dan butiran pati saling mengunci secara mekanis.",
        fontsize=10.5,
    )

    # Page 2: Continuation
    p2 = doc.new_page(width=595.3, height=841.9)
    p2.insert_text((54, 70), "2. Aplikasi dalam Rompi Anti Peluru", fontsize=14)
    p2.insert_textbox(
        fitz.Rect(54, 100, 541, 500),
        "Prinsip shear thickening fluid (STF) ini kini dimanfaatkan secara luas dalam rekayasa material pertahanan, seperti rompi pelindung fleksibel (liquid body armor). Bahan ini tetap fleksibel dan nyaman dipakai oleh prajurit saat bergerak normal, namun segera mengeras seketika saat terkena tumbukan peluru berkecepatan tinggi.",
        fontsize=10.5,
    )

    doc.save(str(pdf_path))
    doc.close()

    evaluator = HandoutRenderedQualityEvaluator()
    result = evaluator.evaluate(pdf_path)

    assert result.artifact_type == "HANDOUT"
    assert result.page_count == 2
    assert not result.has_critical_failures
    assert result.decision in (RenderedQualityDecision.PASS, RenderedQualityDecision.PASS_WITH_WARNINGS)
    assert result.can_export is True
    assert result.overall_quality_score >= 0.85


def test_02_handout_orphan_heading_detected(temp_pdf_dir: Path):
    temp_pdf_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = temp_pdf_dir / "orphan_heading_handout.pdf"

    doc = fitz.open()
    # Page 1: A4 with content and a heading placed at the bottom edge (y=790 out of 841.9)
    p1 = doc.new_page(width=595.3, height=841.9)
    p1.insert_text((54, 70), "Pengantar Dinamika Partikel", fontsize=18)
    p1.insert_textbox(fitz.Rect(54, 100, 541, 700), "Teks isi bab pertama yang panjang mengisi halaman hingga bawah...", fontsize=11)
    # Heading at the very bottom with no text below it on this page
    p1.insert_text((54, 800), "Bab II: Metode Analisis Tegangan", fontsize=16)

    # Page 2: Body text
    p2 = doc.new_page(width=595.3, height=841.9)
    p2.insert_textbox(fitz.Rect(54, 70, 541, 400), "Kelanjutan materi di halaman kedua...", fontsize=11)

    doc.save(str(pdf_path))
    doc.close()

    evaluator = HandoutRenderedQualityEvaluator()
    result = evaluator.evaluate(pdf_path)

    orphan_fails = [f for f in result.critical_failures + result.major_warnings if f.code == RenderedFailureCode.ORPHAN_HEADING]
    assert len(orphan_fails) >= 1
    assert orphan_fails[0].severity == RenderedFailureSeverity.MAJOR
    assert 1 in orphan_fails[0].page_indices


def test_03_handout_wall_of_text_detected(temp_pdf_dir: Path):
    temp_pdf_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = temp_pdf_dir / "wall_of_text_handout.pdf"

    doc = fitz.open()
    page = doc.new_page(width=595.3, height=841.9)
    # Generate monolithic paragraph > 2300 characters
    long_p = "Eksperimen fluida non-Newtonian memberikan wawasan mendalam mengenai reologi fluida. " * 35
    assert len(long_p) > 2300
    page.insert_textbox(fitz.Rect(54, 70, 541, 780), long_p, fontsize=10)

    doc.save(str(pdf_path))
    doc.close()

    evaluator = HandoutRenderedQualityEvaluator()
    result = evaluator.evaluate(pdf_path)

    wall_fails = [f for f in result.critical_failures + result.major_warnings if f.code == RenderedFailureCode.HANDOUT_WALL_OF_TEXT]
    assert len(wall_fails) >= 1
    assert wall_fails[0].severity == RenderedFailureSeverity.MAJOR


def test_04_handout_real_fixture_evaluation():
    real_pdf = Path("outputs/benchmark/phase_2c/artifacts/01_oobleck_experiment/handout/handout.pdf")
    if not real_pdf.exists():
        pytest.skip("Phase 2C handout artifact not available")

    evaluator = HandoutRenderedQualityEvaluator()
    result = evaluator.evaluate(real_pdf)

    assert result.artifact_type == "HANDOUT"
    assert result.page_count == 3
    assert result.has_critical_failures is False
    assert result.can_export is True
    assert result.overall_quality_score > 0.85
