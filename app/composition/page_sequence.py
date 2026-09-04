"""
KIR AI Document Intelligence — Page Sequence Engine.
"""
from app.composition.schemas import PageComposition, CompositionWarning, CompositionWarningCode

def evaluate_page_sequence(pages: list[PageComposition]) -> list[CompositionWarning]:
    """Ensures there is variation in the sequence of pages to avoid monotony."""
    warnings = []
    
    if len(pages) < 3:
        return warnings
        
    consecutive = 0
    last_type = None
    
    for page in pages:
        if page.composition_type == last_type and page.composition_type != "continuation":
            consecutive += 1
        else:
            consecutive = 1
            
        if consecutive >= 3:
            warnings.append(
                CompositionWarning(
                    code=CompositionWarningCode.REPETITIVE_COMPOSITION,
                    severity="warning",
                    page_number=page.page_number,
                    reason=f"Composition type '{last_type}' repeats 3 or more times consecutively.",
                    recommended_action="Insert a transition page or vary the composition."
                )
            )
            consecutive = 0  # reset to avoid spamming
            
        last_type = page.composition_type
        
    return warnings
