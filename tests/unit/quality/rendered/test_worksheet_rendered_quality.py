"""
Unit tests for WorksheetRenderedQualityEvaluator.

Phase 3A: Independent rendered evaluation of educational worksheets / LKS:
- Guided scientific inquiry progression
- Student workspace box detection via vector geometry
- Anti-spoiling verification (strict answer withholding)
- Quiz collapse detection
- Real rendered worksheet evaluation
"""

import pytest
import pymupdf as fitz
from pathlib import Path

from app.quality.rendered.worksheet_quality import WorksheetRenderedQualityEvaluator
from app.quality.rendered.failure_taxonomy import RenderedFailureCode, RenderedFailureSeverity
from app.quality.rendered.contracts import RenderedQualityDecision


@pytest.fixture
def temp_pdf_dir(tmp_path: Path) -> Path:
    return tmp_path / "worksheet_quality_tests"


def test_01_worksheet_adequate_workspace_and_inquiry_passes(temp_pdf_dir: Path):
    temp_pdf_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = temp_pdf_dir / "clean_worksheet.pdf"

    doc = fitz.open()
    # A4 Page
    page = doc.new_page(width=595.3, height=841.9)
    page.insert_text((54, 70), "LEMBAR KERJA SISWA (LKS): EKSPERIMEN OOBLECK", fontsize=16)
    page.insert_text((54, 100), "Fase 1: Prediksi dan Hipotesis Awal", fontsize=12)
    page.insert_textbox(
        fitz.Rect(54, 120, 541, 160),
        "Pertanyaan: Apa yang terjadi ketika fluida oobleck dipukul dengan kepalan tangan secara cepat?",
        fontsize=10.5,
    )
    # Designated student response box (vector rectangle with height >= 60pt)
    page.draw_rect(fitz.Rect(54, 170, 541, 280), color=(0.4, 0.4, 0.4), width=1.0)

    page.insert_text((54, 310), "Fase 2: Observasi dan Pengamatan Praktikum", fontsize=12)
    page.insert_textbox(
        fitz.Rect(54, 330, 541, 370),
        "Catat perubahan wujud dan viskositas fluida saat diberi tekanan perlahan versus cepat.",
        fontsize=10.5,
    )
    # Second student response box
    page.draw_rect(fitz.Rect(54, 380, 541, 520), color=(0.4, 0.4, 0.4), width=1.0)

    page.insert_text((54, 550), "Fase 3: Analisis dan Kesimpulan", fontsize=12)
    # Third student response box
    page.draw_rect(fitz.Rect(54, 570, 541, 720), color=(0.4, 0.4, 0.4), width=1.0)

    doc.save(str(pdf_path))
    doc.close()

    evaluator = WorksheetRenderedQualityEvaluator()
    result = evaluator.evaluate(pdf_path)

    assert result.artifact_type == "WORKSHEET"
    assert not result.has_critical_failures
    assert result.decision in (RenderedQualityDecision.PASS, RenderedQualityDecision.PASS_WITH_WARNINGS)
    assert result.can_export is True
    assert result.artifact_specific_metrics.get("total_workspace_boxes", 0) >= 3


def test_02_worksheet_spoiling_leak_critical(temp_pdf_dir: Path):
    temp_pdf_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = temp_pdf_dir / "spoiled_worksheet.pdf"

    doc = fitz.open()
    page = doc.new_page(width=595.3, height=841.9)
    page.insert_text((54, 70), "LEMBAR KERJA SISWA", fontsize=16)
    page.insert_textbox(fitz.Rect(54, 100, 541, 150), "1. Mengapa oobleck mengeras saat dipukul?", fontsize=11)
    # Leaked answer directly in student worksheet!
    page.insert_textbox(fitz.Rect(54, 160, 541, 250), "Kunci Jawaban: Karena molekul pati saling mengunci saat gaya impulsif...", fontsize=11)
    page.draw_rect(fitz.Rect(54, 260, 541, 400), color=(0, 0, 0), width=1.0)

    doc.save(str(pdf_path))
    doc.close()

    evaluator = WorksheetRenderedQualityEvaluator()
    result = evaluator.evaluate(pdf_path)

    assert result.has_critical_failures is True
    assert result.can_export is False
    assert result.decision == RenderedQualityDecision.BLOCKED
    spoiling_fails = [f for f in result.critical_failures if f.code == RenderedFailureCode.WORKSHEET_SPOILING_FAILURE]
    assert len(spoiling_fails) >= 1


def test_03_worksheet_quiz_collapse(temp_pdf_dir: Path):
    temp_pdf_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = temp_pdf_dir / "quiz_collapse.pdf"

    doc = fitz.open()
    page = doc.new_page(width=595.3, height=841.9)
    page.insert_text((54, 50), "LATIHAN SOAL PILIHAN GANDA", fontsize=14)
    # Insert 10 numbered quiz questions without any inquiry terms (prediksi, observasi, dll)
    for i in range(1, 11):
        y = 60 + (i * 70)
        page.insert_textbox(fitz.Rect(54, y, 541, y + 40), f"Pertanyaan {i}: Berapakah nilai konstanta laju geser fluida?", fontsize=10)
        page.draw_rect(fitz.Rect(54, y + 42, 541, y + 60), color=(0.8, 0.8, 0.8), width=1.0)

    doc.save(str(pdf_path))
    doc.close()

    evaluator = WorksheetRenderedQualityEvaluator()
    result = evaluator.evaluate(pdf_path)

    assert any(f.code == RenderedFailureCode.WORKSHEET_QUIZ_COLLAPSE for f in result.major_warnings)


def test_04_worksheet_real_fixture_truthful_evaluation():
    real_pdf = Path("outputs/benchmark/phase_2c/artifacts/01_oobleck_experiment/worksheet/worksheet.pdf")
    if not real_pdf.exists():
        pytest.skip("Phase 2C worksheet artifact not available")

    evaluator = WorksheetRenderedQualityEvaluator()
    result = evaluator.evaluate(real_pdf)

    assert result.artifact_type == "WORKSHEET"
    assert result.page_count == 15
    # Anti-spoiling rule was preserved (no critical spoiling leak)
    assert not any(f.code == RenderedFailureCode.WORKSHEET_SPOILING_FAILURE for f in result.critical_failures)
    # Truthful diagnostic: text size warning for small note fonts
    assert result.overall_quality_score > 0.70
