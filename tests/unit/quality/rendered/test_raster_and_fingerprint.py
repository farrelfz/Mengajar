"""
Unit tests for RasterImageInspector, CompositionFingerprintEngine, and WhitespaceIntentModel.

Phase 3A: Deterministic pixel and layout statistics:
- Non-background visual density and blank page detection
- Visual balance and edge density
- Spatial layout fingerprinting and repetition streak detection
- Context-aware whitespace model distinguishing student workspace from void
"""

import pytest
import pymupdf as fitz
from pathlib import Path

from app.quality.rendered.raster_inspector import RasterImageInspector
from app.quality.rendered.composition_fingerprint import (
    CompositionFingerprintEngine,
    PageCompositionFingerprint,
)
from app.quality.rendered.whitespace_model import WhitespaceIntentModel
from app.quality.rendered.failure_taxonomy import RenderedFailureCode, RenderedFailureSeverity


@pytest.fixture
def temp_pdf_dir(tmp_path: Path) -> Path:
    return tmp_path / "raster_tests"


def test_01_detect_completely_blank_page(temp_pdf_dir: Path):
    temp_pdf_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = temp_pdf_dir / "blank_page.pdf"

    # Create a document with 1 normal page and 1 completely blank page
    doc = fitz.open()
    p1 = doc.new_page(width=960, height=540)
    p1.insert_text((100, 100), "This is a slide with content", fontsize=24)
    # Page 2 has no content at all
    doc.new_page(width=960, height=540)
    doc.save(str(pdf_path))
    doc.close()

    inspector = RasterImageInspector(dpi=72)
    metrics, analyses, failures = inspector.inspect_document(pdf_path, artifact_type="PRESENTATION")

    assert analyses[1].is_blank is True
    assert any(f.code == RenderedFailureCode.BLANK_PAGE for f in failures)
    blank_fail = [f for f in failures if f.code == RenderedFailureCode.BLANK_PAGE][0]
    assert blank_fail.severity == RenderedFailureSeverity.CRITICAL
    assert blank_fail.page_indices == (2,)


def test_02_visual_density_and_balance(temp_pdf_dir: Path):
    temp_pdf_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = temp_pdf_dir / "balanced.pdf"

    doc = fitz.open()
    page = doc.new_page(width=960, height=540)
    # Put text symmetrically
    page.insert_textbox(fitz.Rect(100, 100, 450, 400), "Left column text content explaining the topic in detail.", fontsize=18)
    page.insert_textbox(fitz.Rect(510, 100, 860, 400), "Right column text content balancing the layout equally.", fontsize=18)
    doc.save(str(pdf_path))
    doc.close()

    inspector = RasterImageInspector(dpi=72)
    metrics, analyses, failures = inspector.inspect_document(pdf_path, artifact_type="PRESENTATION")

    assert metrics.mean_visual_density > 0.001
    assert analyses[0].visual_balance_score > 0.5
    assert not analyses[0].is_blank
    assert len(failures) == 0


def test_03_composition_fingerprint_similarity_and_streak():
    engine = CompositionFingerprintEngine(presentation_max_allowed_streak=3)

    # 5 identical page layouts (cards in Q1, Q2, Q3, Q4) -> streak length 5 >= 3+2 triggers MAJOR
    fp_identical = [
        PageCompositionFingerprint(
            page_number=i,
            quadrants=(0.25, 0.25, 0.25, 0.25),
            text_density=0.30,
            whitespace_ratio=0.50,
            major_blocks_count=4,
        )
        for i in range(1, 6)
    ]

    metrics, streaks, failures = engine.analyze_fingerprints(fp_identical, artifact_type="PRESENTATION")

    assert metrics.max_repetition_streak == 5
    assert len(streaks) >= 1
    assert any(f.code == RenderedFailureCode.REPETITION_STREAK for f in failures)
    streak_fail = [f for f in failures if f.code == RenderedFailureCode.REPETITION_STREAK][0]
    assert streak_fail.severity == RenderedFailureSeverity.MAJOR
    assert streak_fail.page_indices == (1, 2, 3, 4, 5)


def test_04_composition_fingerprint_diverse_layouts_no_streak():
    engine = CompositionFingerprintEngine(presentation_max_allowed_streak=3)

    # 4 varied layouts: hero, 2-column, full quote, 3-card
    fp_diverse = [
        PageCompositionFingerprint(
            page_number=1,
            quadrants=(0.60, 0.05, 0.05, 0.05),
            text_density=0.15,
            whitespace_ratio=0.70,
            major_blocks_count=1,
        ),
        PageCompositionFingerprint(
            page_number=2,
            quadrants=(0.40, 0.40, 0.10, 0.10),
            text_density=0.45,
            whitespace_ratio=0.35,
            major_blocks_count=2,
        ),
        PageCompositionFingerprint(
            page_number=3,
            quadrants=(0.10, 0.10, 0.40, 0.40),
            text_density=0.25,
            whitespace_ratio=0.60,
            major_blocks_count=3,
        ),
    ]

    metrics, streaks, failures = engine.analyze_fingerprints(fp_diverse, artifact_type="PRESENTATION")

    assert metrics.max_repetition_streak <= 2
    assert len(failures) == 0


def test_05_whitespace_intent_model_worksheet_vs_presentation():
    # In worksheet, high whitespace is student workspace (intentional)
    ws_eval = WhitespaceIntentModel.evaluate_page(
        page_idx=2,
        artifact_type="WORKSHEET",
        occupancy_ratio=0.10,  # 90% empty
        text_length=60,
        reserved_workspace_area_ratio=0.40,
    )
    assert ws_eval.is_acceptable is True
    assert ws_eval.failure is None
    assert ws_eval.intentional_whitespace_ratio > 0.30

    # In presentation, an underfilled slide with 60 chars and 92% empty is a suspicious void
    pres_eval = WhitespaceIntentModel.evaluate_page(
        page_idx=2,
        artifact_type="PRESENTATION",
        occupancy_ratio=0.05,  # 95% empty
        text_length=40,
        is_last_page=False,
    )
    assert pres_eval.is_acceptable is False
    assert pres_eval.failure is not None
    assert pres_eval.failure.code == RenderedFailureCode.SUSPICIOUS_VOID
