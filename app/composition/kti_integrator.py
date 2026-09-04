"""
KIR AI Document Intelligence — KTI Integrator.
"""
from app.composition.schemas import CompositionWarning, CompositionWarningCode, DocumentComposition
from app.intelligence.schemas import KtiBab

def validate_kti_progression(composition: DocumentComposition) -> list[CompositionWarning]:
    """Validates that a KTI report maintains the correct BAB progression."""
    warnings = []
    
    bab_order = {
        KtiBab.BAB_1: 1,
        KtiBab.BAB_2: 2,
        KtiBab.BAB_3: 3,
        KtiBab.BAB_4: 4,
        KtiBab.BAB_5: 5
    }
    
    last_bab_value = 0
    for page in composition.pages:
        bab = page.metadata.get("kti_bab")
        if bab and bab in bab_order:
            val = bab_order[bab]
            if val < last_bab_value:
                warnings.append(
                    CompositionWarning(
                        code=CompositionWarningCode.SEMANTIC_SEQUENCE_BREAK,
                        severity="error",
                        page_number=page.page_number,
                        reason=f"BAB {bab.value} appears after a later BAB in the sequence."
                    )
                )
            last_bab_value = val
            
    return warnings
