"""
KIR AI Document Intelligence — Completeness Validator.
"""
from app.composition.schemas import DocumentComposition, CompositionWarning, CompositionWarningCode

def validate_completeness(source_unit_ids: list[str], composition: DocumentComposition) -> list[CompositionWarning]:
    """
    Validates that all source units were consumed exactly once in the final composition.
    Returns a list of warnings (missing or duplicated content).
    """
    used_units = []
    warnings = []
    
    for page in composition.pages:
        for region in page.regions.values():
            for block in region.blocks:
                used_units.extend(block.source_unit_ids)
                
    source_set = set(source_unit_ids)
    used_set = set(used_units)
    
    missing = source_set - used_set
    if missing:
        warnings.append(
            CompositionWarning(
                code=CompositionWarningCode.MISSING_SOURCE_CONTENT,
                severity="error",
                source_unit_ids=list(missing),
                reason=f"{len(missing)} source units were not included in the final composition."
            )
        )
        
    # Check duplicates
    seen = set()
    duplicates = set()
    for uid in used_units:
        if uid in seen:
            duplicates.add(uid)
        seen.add(uid)
        
    if duplicates:
        warnings.append(
            CompositionWarning(
                code=CompositionWarningCode.DUPLICATED_SOURCE_CONTENT,
                severity="warning",
                source_unit_ids=list(duplicates),
                reason=f"{len(duplicates)} source units were used multiple times without explicit duplication intent."
            )
        )
        
    return warnings
