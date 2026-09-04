"""Domain semantic validation tests for KTI BAB 2 (Tinjauan Pustaka) and BAB 3 (Metodologi)."""


from app.intelligence.schemas import (
    ContentType,
    ContentUnit,
    KtiBab,
)
from app.intelligence.traceability_engine import ResearchTraceabilityEngine


def test_bab2_theory_vs_concept_vs_prior_research_vs_gap():
    """Verify distinction between Theory, Concept, Prior Research, and Research Gap."""
    u_theory = ContentUnit(
        source_order=0,
        raw_text="Menurut teori toksikologi (Schmutterer, 1990)...",
        normalized_text="Menurut teori toksikologi (Schmutterer, 1990)...",
        content_type=ContentType.THEORY,
        research_role=ContentType.THEORETICAL_FOUNDATION,
        kti_bab=KtiBab.BAB_2,
    )
    u_concept = ContentUnit(
        source_order=1,
        raw_text="Biopestisida merupakan agen pengendali...",
        normalized_text="Biopestisida merupakan agen pengendali...",
        content_type=ContentType.CONCEPT,
        research_role=ContentType.KEY_CONCEPT,
        kti_bab=KtiBab.BAB_2,
    )
    u_prior = ContentUnit(
        source_order=2,
        raw_text="Penelitian Pratama (2021) menemukan...",
        normalized_text="Penelitian Pratama (2021) menemukan...",
        content_type=ContentType.PRIOR_RESEARCH,
        research_role=ContentType.RESEARCH_PRIOR,
        kti_bab=KtiBab.BAB_2,
    )
    u_gap = ContentUnit(
        source_order=3,
        raw_text="Meskipun demikian, efektivitas daun mimba liar belum banyak diteliti...",
        normalized_text="Meskipun demikian, efektivitas daun mimba liar belum banyak diteliti...",
        content_type=ContentType.RESEARCH_GAP,
        research_role=ContentType.RESEARCH_GAP_KTI,
        kti_bab=KtiBab.BAB_2,
    )

    roles = {u_theory.research_role, u_concept.research_role, u_prior.research_role, u_gap.research_role}
    assert len(roles) == 4
    assert ContentType.THEORETICAL_FOUNDATION != ContentType.RESEARCH_PRIOR
    assert ContentType.RESEARCH_PRIOR != ContentType.RESEARCH_GAP_KTI


def test_bab2_traceability_detection():
    """Verify ResearchTraceabilityEngine detects BAB 2 theoretical foundation and prior research."""
    engine = ResearchTraceabilityEngine()
    units = [
        ContentUnit(source_order=0, raw_text="Teori", normalized_text="Teori", research_role=ContentType.THEORETICAL_FOUNDATION, kti_bab=KtiBab.BAB_2),
        ContentUnit(source_order=1, raw_text="Riset Dulu", normalized_text="Riset Dulu", research_role=ContentType.RESEARCH_PRIOR, kti_bab=KtiBab.BAB_2),
    ]
    traceability = engine.build_traceability(units, [])
    assert traceability.has_theoretical_foundation is True
    assert traceability.has_prior_research is True
    assert KtiBab.BAB_2 in traceability.detected_bab_coverage
