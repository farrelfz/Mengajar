"""Domain semantic validation tests for KTI BAB 1 (Pendahuluan)."""


from app.intelligence.schemas import (
    ContentType,
    ContentUnit,
    KtiBab,
)
from app.intelligence.traceability_engine import ResearchTraceabilityEngine


def test_bab1_elements_are_distinct():
    """Verify Background, Problem, Question, Objective, Benefit, and Hypothesis remain distinct."""
    units = [
        ContentUnit(source_order=0, raw_text="Latar belakang...", normalized_text="Latar belakang...", content_type=ContentType.BACKGROUND, research_role=ContentType.RESEARCH_CONTEXT, kti_bab=KtiBab.BAB_1),
        ContentUnit(source_order=1, raw_text="Rumusan masalah...", normalized_text="Rumusan masalah...", content_type=ContentType.PROBLEM, research_role=ContentType.RESEARCH_PROBLEM, kti_bab=KtiBab.BAB_1),
        ContentUnit(source_order=2, raw_text="Pertanyaan penelitian...", normalized_text="Pertanyaan penelitian...", content_type=ContentType.QUESTION, research_role=ContentType.RESEARCH_QUESTION, kti_bab=KtiBab.BAB_1),
        ContentUnit(source_order=3, raw_text="Tujuan penelitian...", normalized_text="Tujuan penelitian...", content_type=ContentType.OBJECTIVE, research_role=ContentType.RESEARCH_OBJECTIVE, kti_bab=KtiBab.BAB_1),
        ContentUnit(source_order=4, raw_text="Manfaat penelitian...", normalized_text="Manfaat penelitian...", content_type=ContentType.BENEFIT, research_role=ContentType.RESEARCH_BENEFIT, kti_bab=KtiBab.BAB_1),
        ContentUnit(source_order=5, raw_text="Hipotesis...", normalized_text="Hipotesis...", content_type=ContentType.HYPOTHESIS, research_role=ContentType.RESEARCH_HYPOTHESIS, kti_bab=KtiBab.BAB_1),
    ]

    roles = [u.research_role for u in units]
    assert len(set(roles)) == 6
    assert ContentType.RESEARCH_OBJECTIVE != ContentType.RESEARCH_BENEFIT
    assert ContentType.RESEARCH_PROBLEM != ContentType.RESEARCH_QUESTION


def test_bab1_traceability_detection():
    """Verify ResearchTraceabilityEngine detects BAB 1 coverage and problem/objective flags."""
    engine = ResearchTraceabilityEngine()
    units = [
        ContentUnit(source_order=0, raw_text="Masalah", normalized_text="Masalah", research_role=ContentType.RESEARCH_PROBLEM, kti_bab=KtiBab.BAB_1),
        ContentUnit(source_order=1, raw_text="Tujuan", normalized_text="Tujuan", research_role=ContentType.RESEARCH_OBJECTIVE, kti_bab=KtiBab.BAB_1),
    ]
    traceability = engine.build_traceability(units, [])
    assert traceability.has_research_problem is True
    assert traceability.has_research_objective is True
    assert KtiBab.BAB_1 in traceability.detected_bab_coverage
