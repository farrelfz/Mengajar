"""
Adversarial Unit Tests for Rendered Output Quality Intelligence Layer.

Phase 3A: Verifies that contract fidelity and semantic scores CANNOT mask
rendered visual failures:
1. High fidelity + clipped text -> BLOCKED
2. High fidelity + tiny unreadable font -> BLOCKED / NEEDS_REPAIR
3. High fidelity + anti-spoiling leakage in worksheet -> BLOCKED
4. High fidelity + completely blank page -> BLOCKED
5. High fidelity + inverted BAB hierarchy -> BLOCKED
6. High fidelity + extreme layout monotony -> NEEDS_REPAIR
7. High fidelity + monolithic wall of text -> NEEDS_REPAIR
"""

import pytest
import pymupdf as fitz
from pathlib import Path

from app.quality.rendered.quality_engine import MasterRenderedQualityEngine
from app.quality.rendered.failure_taxonomy import RenderedFailureCode, RenderedFailureSeverity
from app.quality.rendered.contracts import RenderedQualityDecision


@pytest.fixture
def temp_pdf_dir(tmp_path: Path) -> Path:
    return tmp_path / "adversarial_quality_tests"


def test_01_adversarial_clipping_blocks_export(temp_pdf_dir: Path):
    temp_pdf_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = temp_pdf_dir / "adv_clipped.pdf"

    # Perfect semantic content, but rendered text pushed past the right margin
    doc = fitz.open()
    p = doc.new_page(width=960, height=540)
    p.insert_text((950, 200), "Teks penting tentang fisika fluida yang terpotong di tepi layar", fontsize=24)
    doc.save(str(pdf_path))
    doc.close()

    engine = MasterRenderedQualityEngine()
    result = engine.inspect(pdf_path, artifact_type="PRESENTATION")

    assert result.decision == RenderedQualityDecision.BLOCKED
    assert result.can_export is False
    assert any(f.code == RenderedFailureCode.TEXT_CLIPPING for f in result.critical_failures)


def test_02_adversarial_tiny_text_blocks_export(temp_pdf_dir: Path):
    temp_pdf_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = temp_pdf_dir / "adv_tiny_text.pdf"

    # Perfect semantic content, but rendered at 6.5pt font (unreadable for 16:9 presentation)
    doc = fitz.open()
    p = doc.new_page(width=960, height=540)
    p.insert_text((100, 100), "Slide Judul", fontsize=28)
    p.insert_textbox(fitz.Rect(100, 150, 700, 400), "Teks materi lengkap namun dicetak sangat kecil sehingga tidak terbaca peserta didik di proyektor.", fontsize=6.5)
    doc.save(str(pdf_path))
    doc.close()

    engine = MasterRenderedQualityEngine()
    result = engine.inspect(pdf_path, artifact_type="PRESENTATION")

    assert result.decision == RenderedQualityDecision.BLOCKED
    assert result.can_export is False
    assert any(f.code == RenderedFailureCode.TEXT_TOO_SMALL for f in result.critical_failures)


def test_03_adversarial_worksheet_spoiling_leak_blocks_export(temp_pdf_dir: Path):
    temp_pdf_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = temp_pdf_dir / "adv_worksheet_spoiled.pdf"

    # High contract fidelity, but answer accidentally leaked into student worksheet
    doc = fitz.open()
    p = doc.new_page(width=595.3, height=841.9)
    p.insert_text((54, 70), "LEMBAR KERJA SISWA", fontsize=16)
    p.insert_textbox(fitz.Rect(54, 100, 541, 140), "Pertanyaan investigasi:", fontsize=11)
    p.insert_textbox(fitz.Rect(54, 150, 541, 220), "Kunci Jawaban: Hasil perhitungan viskositas adalah 4.5 Pa.s", fontsize=11)
    p.draw_rect(fitz.Rect(54, 230, 541, 400), color=(0, 0, 0), width=1.0)
    doc.save(str(pdf_path))
    doc.close()

    engine = MasterRenderedQualityEngine()
    result = engine.inspect(pdf_path, artifact_type="WORKSHEET")

    assert result.decision == RenderedQualityDecision.BLOCKED
    assert result.can_export is False
    assert any(f.code == RenderedFailureCode.WORKSHEET_SPOILING_FAILURE for f in result.critical_failures)


def test_04_adversarial_blank_page_blocks_export(temp_pdf_dir: Path):
    temp_pdf_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = temp_pdf_dir / "adv_blank_page.pdf"

    # Multi-page presentation with a completely blank page inserted in middle
    doc = fitz.open()
    p1 = doc.new_page(width=960, height=540)
    p1.insert_text((100, 100), "Slide Satu", fontsize=28)
    # Slide 2 completely blank
    doc.new_page(width=960, height=540)
    p3 = doc.new_page(width=960, height=540)
    p3.insert_text((100, 100), "Slide Tiga", fontsize=28)
    doc.save(str(pdf_path))
    doc.close()

    engine = MasterRenderedQualityEngine()
    result = engine.inspect(pdf_path, artifact_type="PRESENTATION")

    assert result.decision == RenderedQualityDecision.BLOCKED
    assert result.can_export is False
    assert any(f.code == RenderedFailureCode.BLANK_PAGE for f in result.critical_failures)


def test_05_adversarial_scientific_bab_inversion_blocks_export(temp_pdf_dir: Path):
    temp_pdf_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = temp_pdf_dir / "adv_bab_inversion.pdf"

    # High fidelity scientific document, but BAB sequence is inverted (BAB II before BAB I)
    doc = fitz.open()
    p1 = doc.new_page(width=595.3, height=841.9)
    p1.insert_text((54, 70), "BAB II TINJAUAN PUSTAKA", fontsize=14)
    p1.insert_textbox(fitz.Rect(54, 90, 541, 300), "Kajian teori pendukung [1]...", fontsize=10.5)

    p2 = doc.new_page(width=595.3, height=841.9)
    p2.insert_text((54, 70), "BAB I PENDAHULUAN", fontsize=14)
    p2.insert_textbox(fitz.Rect(54, 90, 541, 300), "Latar belakang masalah [2]...", fontsize=10.5)
    doc.save(str(pdf_path))
    doc.close()

    engine = MasterRenderedQualityEngine()
    result = engine.inspect(pdf_path, artifact_type="SCIENTIFIC_DOCUMENT")

    assert result.decision == RenderedQualityDecision.BLOCKED
    assert result.can_export is False
    assert any(f.code == RenderedFailureCode.SCIENTIFIC_HIERARCHY_FAILURE for f in result.critical_failures)


def test_06_adversarial_monotony_streak_requires_repair(temp_pdf_dir: Path):
    temp_pdf_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = temp_pdf_dir / "adv_monotony.pdf"

    # Slide deck with 6 identically-structured slides
    doc = fitz.open()
    for i in range(1, 7):
        p = doc.new_page(width=960, height=540)
        p.insert_text((80, 80), f"Topik Bagian {i}", fontsize=24)
        p.insert_textbox(fitz.Rect(80, 140, 880, 380), f"Deskripsi materi bagian {i} dengan format, letak kotak, dan panjang kalimat yang persis sama...", fontsize=16)
    doc.save(str(pdf_path))
    doc.close()

    engine = MasterRenderedQualityEngine()
    result = engine.inspect(pdf_path, artifact_type="PRESENTATION")

    assert result.decision in (RenderedQualityDecision.NEEDS_REPAIR, RenderedQualityDecision.BLOCKED)
    assert any(f.code == RenderedFailureCode.REPETITION_STREAK for f in result.major_warnings + result.minor_warnings)


def test_07_adversarial_handout_wall_of_text_requires_repair(temp_pdf_dir: Path):
    temp_pdf_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = temp_pdf_dir / "adv_wall_of_text.pdf"

    # Handout with a single massive monolithic paragraph
    doc = fitz.open()
    p = doc.new_page(width=595.3, height=841.9)
    huge_text = "Materi kajian fisika fluida non-Newtonian mencakup studi dinamika fluida berfase banyak. " * 35
    p.insert_textbox(fitz.Rect(54, 70, 541, 780), huge_text, fontsize=10)
    doc.save(str(pdf_path))
    doc.close()

    engine = MasterRenderedQualityEngine()
    result = engine.inspect(pdf_path, artifact_type="HANDOUT")

    assert any(f.code == RenderedFailureCode.HANDOUT_WALL_OF_TEXT for f in result.major_warnings)
    assert result.decision in (RenderedQualityDecision.NEEDS_REPAIR, RenderedQualityDecision.BLOCKED)
