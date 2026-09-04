"""Domain semantic validation tests for KTI BAB 3 (Metodologi Penelitian)."""


from app.intelligence.schemas import (
    ContentType,
    ContentUnit,
    KtiBab,
)
from app.intelligence.traceability_engine import ResearchTraceabilityEngine


def test_bab3_method_vs_tools_vs_procedure_vs_analysis():
    """Verify Method, Design, Tools/Materials, Procedure, and Data Analysis remain distinct."""
    units = [
        ContentUnit(source_order=0, raw_text="Metode eksperimen RAL...", normalized_text="Metode eksperimen RAL...", content_type=ContentType.METHOD, research_role=ContentType.RESEARCH_METHOD, kti_bab=KtiBab.BAB_3),
        ContentUnit(source_order=1, raw_text="Desain penelitian RAL 5 perlakuan...", normalized_text="Desain penelitian RAL 5 perlakuan...", content_type=ContentType.METHOD, research_role=ContentType.RESEARCH_DESIGN, kti_bab=KtiBab.BAB_3),
        ContentUnit(source_order=2, raw_text="Alat: rotary evaporator...", normalized_text="Alat: rotary evaporator...", content_type=ContentType.OTHER, research_role=ContentType.TOOL, kti_bab=KtiBab.BAB_3),
        ContentUnit(source_order=3, raw_text="Prosedur maserasi 3x24 jam...", normalized_text="Prosedur maserasi 3x24 jam...", content_type=ContentType.PROCEDURE, research_role=ContentType.RESEARCH_PROCEDURE, kti_bab=KtiBab.BAB_3),
        ContentUnit(source_order=4, raw_text="Analisis ANOVA dan Probit...", normalized_text="Analisis ANOVA dan Probit...", content_type=ContentType.ANALYSIS, research_role=ContentType.DATA_ANALYSIS_METHOD, kti_bab=KtiBab.BAB_3),
    ]

    roles = {u.research_role for u in units}
    assert len(roles) == 5
    assert ContentType.RESEARCH_PROCEDURE != ContentType.DATA_ANALYSIS_METHOD
    assert ContentType.TOOL != ContentType.RESEARCH_METHOD


def test_bab3_traceability_detection():
    """Verify ResearchTraceabilityEngine detects BAB 3 method coverage."""
    engine = ResearchTraceabilityEngine()
    units = [
        ContentUnit(source_order=0, raw_text="Metode", normalized_text="Metode", research_role=ContentType.RESEARCH_METHOD, kti_bab=KtiBab.BAB_3),
    ]
    traceability = engine.build_traceability(units, [])
    assert traceability.has_research_method is True
    assert KtiBab.BAB_3 in traceability.detected_bab_coverage
