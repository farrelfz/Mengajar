"""Critical domain semantic validation tests for KTI BAB 4 (Hasil dan Pembahasan).

MANDATORY BEHAVIOR:
DATA ≠ RESULT ≠ FINDING ≠ INTERPRETATION ≠ DISCUSSION.
The system must preserve distinction between all 5 stages of evidence transformation.
"""


from app.intelligence.schemas import (
    ContentType,
    ContentUnit,
    KtiBab,
)
from app.intelligence.traceability_engine import ResearchTraceabilityEngine


def test_bab4_critical_distinction_data_result_finding_interpretation_discussion():
    """Verify DATA, RESULT, FINDING, INTERPRETATION, and DISCUSSION never collapse."""
    u_data = ContentUnit(
        source_order=0,
        raw_text="Rata-rata mortalitas kontrol 0%, 5% 25%, 10% 55%, 15% 78%, 20% 92%.",
        normalized_text="Rata-rata mortalitas kontrol 0%, 5% 25%, 10% 55%, 15% 78%, 20% 92%.",
        content_type=ContentType.DATA,
        research_role=ContentType.DATA_POINT,
        kti_bab=KtiBab.BAB_4,
    )
    u_result = ContentUnit(
        source_order=1,
        raw_text="Hasil pengujian disajikan pada Tabel 4.1 dan grafik pertumbuhan.",
        normalized_text="Hasil pengujian disajikan pada Tabel 4.1 dan grafik pertumbuhan.",
        content_type=ContentType.RESULT,
        research_role=ContentType.RESEARCH_RESULT,
        kti_bab=KtiBab.BAB_4,
    )
    u_finding = ContentUnit(
        source_order=2,
        raw_text="Peningkatan konsentrasi berkorelasi positif dan signifikan terhadap mortalitas (p < 0.05).",
        normalized_text="Peningkatan konsentrasi berkorelasi positif dan signifikan terhadap mortalitas (p < 0.05).",
        content_type=ContentType.FINDING,
        research_role=ContentType.RESEARCH_FINDING,
        kti_bab=KtiBab.BAB_4,
    )
    u_interpretation = ContentUnit(
        source_order=3,
        raw_text="Hal ini menunjukkan adanya potensi bioaktivitas insektisida yang merusak pencernaan larva.",
        normalized_text="Hal ini menunjukkan adanya potensi bioaktivitas insektisida yang merusak pencernaan larva.",
        content_type=ContentType.INTERPRETATION,
        research_role=ContentType.RESEARCH_INTERPRETATION,
        kti_bab=KtiBab.BAB_4,
    )
    u_discussion = ContentUnit(
        source_order=4,
        raw_text="Temuan ini sejalan dengan teori Schmutterer (1990) bahwa azadirachtin menimbulkan antifeedant effect.",
        normalized_text="Temuan ini sejalan dengan teori Schmutterer (1990) bahwa azadirachtin menimbulkan antifeedant effect.",
        content_type=ContentType.DISCUSSION,
        research_role=ContentType.RESEARCH_DISCUSSION,
        kti_bab=KtiBab.BAB_4,
    )

    roles = [u_data.research_role, u_result.research_role, u_finding.research_role, u_interpretation.research_role, u_discussion.research_role]
    
    # 1. Assert all 5 are unique
    assert len(set(roles)) == 5

    # 2. Explicit pairwise inequalities
    assert ContentType.DATA_POINT != ContentType.RESEARCH_RESULT
    assert ContentType.RESEARCH_RESULT != ContentType.RESEARCH_FINDING
    assert ContentType.RESEARCH_FINDING != ContentType.RESEARCH_INTERPRETATION
    assert ContentType.RESEARCH_INTERPRETATION != ContentType.RESEARCH_DISCUSSION

    # 3. Verify general types are also distinct
    general_types = [u_data.content_type, u_result.content_type, u_finding.content_type, u_interpretation.content_type, u_discussion.content_type]
    assert len(set(general_types)) == 5


def test_bab4_traceability_detection():
    """Verify ResearchTraceabilityEngine detects BAB 4 results and discussion."""
    engine = ResearchTraceabilityEngine()
    units = [
        ContentUnit(source_order=0, raw_text="Data", normalized_text="Data", research_role=ContentType.RESEARCH_RESULT, kti_bab=KtiBab.BAB_4),
        ContentUnit(source_order=1, raw_text="Diskusi", normalized_text="Diskusi", research_role=ContentType.RESEARCH_DISCUSSION, kti_bab=KtiBab.BAB_4),
    ]
    traceability = engine.build_traceability(units, [])
    assert traceability.has_results is True
    assert traceability.has_discussion is True
    assert KtiBab.BAB_4 in traceability.detected_bab_coverage
