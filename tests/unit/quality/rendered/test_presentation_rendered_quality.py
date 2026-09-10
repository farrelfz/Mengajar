"""
Unit tests for PresentationRenderedQualityEvaluator.

Phase 3A: Independent rendered evaluation of 16:9 presentation slide decks:
- Clean deck evaluation
- Duplicate slide detection
- Card overload detection
- Real rendered deck evaluation
"""

import pytest
import pymupdf as fitz
from pathlib import Path

from app.quality.rendered.presentation_quality import PresentationRenderedQualityEvaluator
from app.quality.rendered.failure_taxonomy import RenderedFailureCode, RenderedFailureSeverity
from app.quality.rendered.contracts import RenderedQualityDecision


@pytest.fixture
def temp_pdf_dir(tmp_path: Path) -> Path:
    return tmp_path / "presentation_quality_tests"


def test_01_presentation_clean_deck_passes(temp_pdf_dir: Path):
    temp_pdf_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = temp_pdf_dir / "clean_presentation.pdf"

    doc = fitz.open()
    # Slide 1: Title slide
    s1 = doc.new_page(width=960, height=540)
    s1.insert_text((100, 200), "Fisika Fluida: Eksperimen Oobleck", fontsize=32)
    s1.insert_text((100, 260), "Panduan Praktikum Sains Interaktif", fontsize=18)

    # Slide 2: Two column concept
    s2 = doc.new_page(width=960, height=540)
    s2.insert_text((80, 80), "Konsep Dasar Fluida Non-Newtonian", fontsize=26)
    s2.insert_textbox(fitz.Rect(80, 140, 460, 420), "Fluida non-Newtonian memiliki viskositas yang berubah saat diberi tegangan geser atau gaya mendadak.", fontsize=16)
    s2.insert_textbox(fitz.Rect(500, 140, 880, 420), "Contoh nyata adalah campuran pati jagung dan air yang memadat saat dipukul cepat.", fontsize=16)

    # Slide 3: Conclusion / Summary
    s3 = doc.new_page(width=960, height=540)
    s3.insert_text((80, 80), "Kesimpulan Praktikum", fontsize=26)
    s3.insert_textbox(fitz.Rect(80, 140, 880, 420), "Pati jagung membentuk jaringan suspensi sementara saat mengalami tegangan mekanik.", fontsize=18)

    doc.save(str(pdf_path))
    doc.close()

    evaluator = PresentationRenderedQualityEvaluator()
    result = evaluator.evaluate(pdf_path)

    assert result.artifact_type == "PRESENTATION"
    assert result.page_count == 3
    assert not result.has_critical_failures
    assert result.decision in (RenderedQualityDecision.PASS, RenderedQualityDecision.PASS_WITH_WARNINGS)
    assert result.can_export is True
    assert result.overall_quality_score >= 0.80


def test_02_presentation_duplicate_slide_critical(temp_pdf_dir: Path):
    temp_pdf_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = temp_pdf_dir / "duplicate_presentation.pdf"

    doc = fitz.open()
    dup_text = "Slide Duplikat: Penjelasan materi yang sama persis diulang tanpa perubahan apapun pada slide berikutnya."

    s1 = doc.new_page(width=960, height=540)
    s1.insert_text((100, 100), "Slide Judul Pertama", fontsize=28)
    s1.insert_textbox(fitz.Rect(100, 160, 800, 400), dup_text, fontsize=18)

    s2 = doc.new_page(width=960, height=540)
    s2.insert_text((100, 100), "Slide Judul Pertama", fontsize=28)
    s2.insert_textbox(fitz.Rect(100, 160, 800, 400), dup_text, fontsize=18)

    doc.save(str(pdf_path))
    doc.close()

    evaluator = PresentationRenderedQualityEvaluator()
    result = evaluator.evaluate(pdf_path)

    assert any(f.code == RenderedFailureCode.DUPLICATE_COMPOSITION for f in result.critical_failures + result.major_warnings)
    dup_fails = [f for f in result.critical_failures + result.major_warnings if f.code == RenderedFailureCode.DUPLICATE_COMPOSITION]
    assert len(dup_fails) >= 1
    assert result.can_export is False or result.decision != RenderedQualityDecision.PASS


def test_03_presentation_card_overload(temp_pdf_dir: Path):
    temp_pdf_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = temp_pdf_dir / "card_overload.pdf"

    doc = fitz.open()
    page = doc.new_page(width=960, height=540)
    # Insert 10 distinct text blocks to trigger card overload
    for k in range(10):
        y = 40 + k * 45
        page.insert_textbox(fitz.Rect(80, y, 700, y + 35), f"Card Element {k}: distinct block with text description", fontsize=14)

    doc.save(str(pdf_path))
    doc.close()

    evaluator = PresentationRenderedQualityEvaluator()
    result = evaluator.evaluate(pdf_path)

    assert any(f.code == RenderedFailureCode.CARD_OVERLOAD for f in result.major_warnings)


def test_04_presentation_real_fixture_truthful_evaluation():
    real_pdf = Path("outputs/benchmark/phase_2c/artifacts/01_oobleck_experiment/presentation/presentation.pdf")
    if not real_pdf.exists():
        pytest.skip("Phase 2C presentation artifact not available")

    evaluator = PresentationRenderedQualityEvaluator()
    result = evaluator.evaluate(real_pdf)

    # Truthful diagnostic: element collision and tiny text were detected
    assert result.has_critical_failures is True
    assert result.decision == RenderedQualityDecision.BLOCKED
    assert result.can_export is False
    assert result.page_count == 14
    assert any(f.code == RenderedFailureCode.ELEMENT_COLLISION for f in result.critical_failures)
