"""Integration tests for Source Fidelity constraints."""


from app.intelligence.normalizer import InputNormalizer
from app.intelligence.schemas import (
    ContentType,
    ContentUnit,
    KtiBab,
)
from app.intelligence.segmenter import ContentSegmenter


def test_normalizer_and_segmenter_preserve_exact_numbers_and_data():
    """Verify raw numbers and text are preserved without summarization or hallucination."""
    raw = """
# Data Pengamatan

Hasil uji menunjukkan konsentrasi 15% menghasilkan mortalitas 78.5% pada 30 sampel.
"""
    normalizer = InputNormalizer()
    segmenter = ContentSegmenter()

    doc = normalizer.normalize(raw, "fidelity_test")
    res = segmenter.segment(doc)

    paragraph_unit = res.content_units[1]
    assert "15%" in paragraph_unit.normalized_text
    assert "78.5%" in paragraph_unit.normalized_text
    assert "30 sampel" in paragraph_unit.normalized_text
    assert paragraph_unit.raw_text == paragraph_unit.normalized_text


def test_hypothesis_is_not_silently_converted_to_conclusion():
    """Verify hypothesis unit retains RESEARCH_HYPOTHESIS role and is not falsely marked as CONCLUSION."""
    u_hyp = ContentUnit(
        source_order=0,
        raw_text="Hipotesis: Konsentrasi 15% diduga mampu menekan hama di atas 70%.",
        normalized_text="Hipotesis: Konsentrasi 15% diduga mampu menekan hama di atas 70%.",
        content_type=ContentType.HYPOTHESIS,
        research_role=ContentType.RESEARCH_HYPOTHESIS,
        kti_bab=KtiBab.BAB_1,
    )
    assert u_hyp.research_role == ContentType.RESEARCH_HYPOTHESIS
    assert u_hyp.research_role != ContentType.RESEARCH_CONCLUSION
    assert u_hyp.content_type != ContentType.CONCLUSION
