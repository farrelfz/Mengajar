"""
Unit tests for PDFGeometryInspector.

Phase 3A: Physical vector geometry inspection:
- Clipping outside page boundaries
- Tiny text detection per artifact threshold
- Element collision detection
- Margin variance
"""

import pytest
import pymupdf as fitz
from pathlib import Path

from app.quality.rendered.pdf_inspector import PDFGeometryInspector
from app.quality.rendered.failure_taxonomy import RenderedFailureCode, RenderedFailureSeverity


@pytest.fixture
def temp_pdf_dir(tmp_path: Path) -> Path:
    return tmp_path / "pdf_geometry_tests"


def test_01_detect_text_clipping_outside_boundary(temp_pdf_dir: Path):
    temp_pdf_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = temp_pdf_dir / "clipped.pdf"

    # Create a slide with text placed outside page bounds (width=960, height=540)
    doc = fitz.open()
    page = doc.new_page(width=960, height=540)
    # Put text starting at x=950, y=530 with fontsize 24 so it flows way past 960 and 540
    page.insert_text((950, 530), "This text extends outside the physical page bounds", fontsize=24)
    doc.save(str(pdf_path))
    doc.close()

    inspector = PDFGeometryInspector()
    metrics, analyses, failures = inspector.inspect_document(pdf_path, artifact_type="PRESENTATION")

    assert metrics.text_clipping_instances >= 1
    assert any(f.code == RenderedFailureCode.TEXT_CLIPPING for f in failures)
    clipping_fail = [f for f in failures if f.code == RenderedFailureCode.TEXT_CLIPPING][0]
    assert clipping_fail.severity == RenderedFailureSeverity.CRITICAL
    assert clipping_fail.page_indices == (1,)


def test_02_tiny_text_detection_with_thresholds(temp_pdf_dir: Path):
    temp_pdf_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = temp_pdf_dir / "tiny_text.pdf"

    doc = fitz.open()
    page = doc.new_page(width=960, height=540)
    # Normal title
    page.insert_text((50, 80), "Readable Slide Title", fontsize=28)
    # Presentation threshold is 11.0pt. Insert text at 7.0pt (CRITICAL) and 9.5pt (MAJOR)
    page.insert_text((50, 200), "Very tiny unreadable slide text", fontsize=7.0)
    page.insert_text((50, 250), "Slightly small body text", fontsize=9.5)
    doc.save(str(pdf_path))
    doc.close()

    inspector = PDFGeometryInspector()
    metrics, analyses, failures = inspector.inspect_document(pdf_path, artifact_type="PRESENTATION")

    tiny_fails = [f for f in failures if f.code == RenderedFailureCode.TEXT_TOO_SMALL]
    assert len(tiny_fails) >= 2
    assert any(f.severity == RenderedFailureSeverity.CRITICAL for f in tiny_fails)
    assert metrics.tiny_text_spans_count >= 2


def test_03_element_collision_detection(temp_pdf_dir: Path):
    temp_pdf_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = temp_pdf_dir / "collision.pdf"

    doc = fitz.open()
    page = doc.new_page(width=960, height=540)
    # Insert two multi-line text boxes at overlapping coordinates with distinct fonts to form distinct blocks
    page.insert_textbox(fitz.Rect(100, 100, 500, 250), "First content box with lots of text that takes up space in the box", fontname="helv", fontsize=20)
    page.insert_textbox(fitz.Rect(120, 110, 450, 250), "Second overlapping content box that crashes directly into the first box", fontname="times-roman", fontsize=16)
    doc.save(str(pdf_path))
    doc.close()

    inspector = PDFGeometryInspector()
    metrics, analyses, failures = inspector.inspect_document(pdf_path, artifact_type="PRESENTATION")

    assert metrics.element_collision_count >= 1
    collision_fails = [f for f in failures if f.code == RenderedFailureCode.ELEMENT_COLLISION]
    assert len(collision_fails) >= 1
    assert collision_fails[0].evidence["overlap_area"] > 20.0


def test_04_clean_page_geometry_no_failures(temp_pdf_dir: Path):
    temp_pdf_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = temp_pdf_dir / "clean.pdf"

    doc = fitz.open()
    page = doc.new_page(width=960, height=540)
    # Clean layout with good margins and readable font sizes
    page.insert_text((80, 100), "Title of Slide", fontsize=32)
    page.insert_textbox(fitz.Rect(80, 140, 500, 400), "Clear readable body text placed well within margins.", fontsize=18)
    doc.save(str(pdf_path))
    doc.close()

    inspector = PDFGeometryInspector()
    metrics, analyses, failures = inspector.inspect_document(pdf_path, artifact_type="PRESENTATION")

    assert metrics.text_clipping_instances == 0
    assert metrics.element_collision_count == 0
    assert metrics.tiny_text_spans_count == 0
    assert len(failures) == 0
    assert analyses[0].occupancy_ratio > 0.0
