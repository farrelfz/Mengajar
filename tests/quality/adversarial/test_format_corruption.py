"""
Adversarial Case G & H: Format geometry mismatch and page count divergence detection.
"""

from pathlib import Path
import pytest
import pymupdf

from app.quality.contracts import QualityDimension, QualitySeverity
from app.quality.format_evaluator import FormatEvaluator


def test_major_format_geometry_mismatch_detected(tmp_path: Path):
    # Create a 16:9 presentation PDF (960 x 540 pt)
    pdf_file = tmp_path / "test_pres.pdf"
    doc = pymupdf.open()
    page = doc.new_page(width=960.0, height=540.0)
    page.insert_text((50, 50), "Landscape slide")
    doc.save(str(pdf_file))
    doc.close()

    # Intentionally evaluate as A4 Portrait (595.0 x 841.9 pt)
    metrics, findings = FormatEvaluator.evaluate(pdf_file, target_format="a4_portrait")

    assert len(findings) >= 1
    assert any(f.severity == QualitySeverity.CRITICAL for f in findings)
    assert any("deviate from contract" in f.finding.lower() for f in findings)
    assert metrics[0].score == 0.0


def test_page_count_mismatch_detected(tmp_path: Path):
    # Create a 2-page PDF
    pdf_file = tmp_path / "test_2pages.pdf"
    doc = pymupdf.open()
    doc.new_page(width=595.0, height=841.9)
    doc.new_page(width=595.0, height=841.9)
    doc.save(str(pdf_file))
    doc.close()

    # Evaluate against an expected composition of 4 pages
    metrics, findings = FormatEvaluator.evaluate(pdf_file, target_format="a4_portrait", expected_page_count=4)

    assert len(findings) >= 1
    assert any(f.severity == QualitySeverity.WARNING for f in findings)
    assert any("diverges from composition page allocation" in f.finding.lower() for f in findings)
    assert metrics[0].score < 1.0
