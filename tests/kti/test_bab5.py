"""Critical domain semantic validation tests for KTI BAB 5 (Kesimpulan dan Saran).

MANDATORY BEHAVIOR:
CONCLUSION ≠ RECOMMENDATION
LIMITATION ≠ FUTURE_WORK
CONCLUSION must trace to findings / objectives.
RECOMMENDATION must trace to findings / limitations / implications.
"""


from app.intelligence.schemas import (
    ContentRelationship,
    ContentType,
    ContentUnit,
    KtiBab,
    RelationshipType,
    TraceabilityWarning,
)
from app.intelligence.traceability_engine import ResearchTraceabilityEngine


def test_bab5_critical_distinction_conclusion_vs_recommendation_vs_limitation_vs_future_work():
    """Verify Conclusion, Limitation, Recommendation, and Future Work are strictly distinct."""
    u_conclusion = ContentUnit(
        unit_id="u_conc",
        source_order=0,
        raw_text="Ekstrak daun mimba efektif mengendalikan mortalitas larva dengan LC50 9.4%.",
        normalized_text="Ekstrak daun mimba efektif mengendalikan mortalitas larva dengan LC50 9.4%.",
        content_type=ContentType.CONCLUSION,
        research_role=ContentType.RESEARCH_CONCLUSION,
        kti_bab=KtiBab.BAB_5,
    )
    u_limitation = ContentUnit(
        unit_id="u_limit",
        source_order=1,
        raw_text="Penelitian ini hanya dilakukan dalam skala laboratorium terkontrol.",
        normalized_text="Penelitian ini hanya dilakukan dalam skala laboratorium terkontrol.",
        content_type=ContentType.LIMITATION,
        research_role=ContentType.RESEARCH_LIMITATION,
        kti_bab=KtiBab.BAB_5,
    )
    u_recommendation = ContentUnit(
        unit_id="u_rec",
        source_order=2,
        raw_text="Petani sayuran disarankan mengaplikasikan ekstrak daun mimba 10-15%.",
        normalized_text="Petani sayuran disarankan mengaplikasikan ekstrak daun mimba 10-15%.",
        content_type=ContentType.RECOMMENDATION,
        research_role=ContentType.RESEARCH_RECOMMENDATION,
        kti_bab=KtiBab.BAB_5,
    )
    u_future = ContentUnit(
        unit_id="u_future",
        source_order=3,
        raw_text="Pengembangan nano-enkapsulasi perlu dieksplorasi pada penelitian lanjutan.",
        normalized_text="Pengembangan nano-enkapsulasi perlu dieksplorasi pada penelitian lanjutan.",
        content_type=ContentType.FUTURE_WORK,
        research_role=ContentType.RESEARCH_FUTURE_WORK,
        kti_bab=KtiBab.BAB_5,
    )

    roles = [u_conclusion.research_role, u_limitation.research_role, u_recommendation.research_role, u_future.research_role]
    assert len(set(roles)) == 4

    assert ContentType.RESEARCH_CONCLUSION != ContentType.RESEARCH_RECOMMENDATION
    assert ContentType.RESEARCH_LIMITATION != ContentType.RESEARCH_FUTURE_WORK
    assert ContentType.RESEARCH_RECOMMENDATION != ContentType.RESEARCH_FUTURE_WORK


def test_bab5_traceability_grounded_recommendation_and_conclusion():
    """Verify ResearchTraceabilityEngine traces conclusions to objectives and recommendations to limitations."""
    engine = ResearchTraceabilityEngine()

    u_q = ContentUnit(unit_id="u_q", source_order=0, raw_text="Pertanyaan", normalized_text="Pertanyaan", research_role=ContentType.RESEARCH_QUESTION, kti_bab=KtiBab.BAB_1)
    u_finding = ContentUnit(unit_id="u_find", source_order=1, raw_text="Temuan", normalized_text="Temuan", research_role=ContentType.RESEARCH_FINDING, kti_bab=KtiBab.BAB_4)
    u_limit = ContentUnit(unit_id="u_limit", source_order=2, raw_text="Batasan lab", normalized_text="Batasan lab", research_role=ContentType.RESEARCH_LIMITATION, kti_bab=KtiBab.BAB_5)
    u_conc = ContentUnit(unit_id="u_conc", source_order=3, raw_text="Kesimpulan", normalized_text="Kesimpulan", research_role=ContentType.RESEARCH_CONCLUSION, kti_bab=KtiBab.BAB_5)
    u_rec = ContentUnit(unit_id="u_rec", source_order=4, raw_text="Saran lapangan", normalized_text="Saran lapangan", research_role=ContentType.RESEARCH_RECOMMENDATION, kti_bab=KtiBab.BAB_5)

    relationships = [
        ContentRelationship(source_unit_id="u_conc", target_unit_id="u_q", relationship_type=RelationshipType.ANSWERS),
        ContentRelationship(source_unit_id="u_conc", target_unit_id="u_find", relationship_type=RelationshipType.BASED_ON),
        ContentRelationship(source_unit_id="u_rec", target_unit_id="u_limit", relationship_type=RelationshipType.BASED_ON),
    ]

    traceability = engine.build_traceability([u_q, u_finding, u_limit, u_conc, u_rec], relationships)

    assert traceability.has_conclusion is True
    assert traceability.has_recommendation is True
    assert len(traceability.conclusion_traces) == 1
    assert traceability.conclusion_traces[0].answers_question_unit_id == "u_q"
    assert "u_find" in traceability.conclusion_traces[0].based_on_finding_unit_ids

    assert len(traceability.recommendation_bases) == 1
    assert traceability.recommendation_bases[0].is_grounded is True
    assert "u_limit" in traceability.recommendation_bases[0].based_on_limitation_unit_ids
    assert TraceabilityWarning.RECOMMENDATION_WITHOUT_BASIS not in traceability.traceability_warnings


def test_bab5_orphan_recommendation_triggers_warning():
    """Verify an ungrounded recommendation without basis triggers RECOMMENDATION_WITHOUT_BASIS warning."""
    engine = ResearchTraceabilityEngine()

    u_find = ContentUnit(unit_id="u_find", source_order=0, raw_text="Temuan", normalized_text="Temuan", research_role=ContentType.RESEARCH_FINDING, kti_bab=KtiBab.BAB_4)
    u_rec = ContentUnit(unit_id="u_rec", source_order=1, raw_text="Saran random tanpa dasar.", normalized_text="Saran random tanpa dasar.", research_role=ContentType.RESEARCH_RECOMMENDATION, kti_bab=KtiBab.BAB_5)

    traceability = engine.build_traceability([u_find, u_rec], [])
    assert TraceabilityWarning.RECOMMENDATION_WITHOUT_BASIS in traceability.traceability_warnings
