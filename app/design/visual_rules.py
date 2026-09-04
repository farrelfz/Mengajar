"""
KIR AI Document Intelligence — Visual Sequence Rules.

Evaluates sequences of pages to prevent visual monotony and ensure rhythm.
"""

from app.design.schemas import PageComposition, CompositionPattern, DesignWarning, DesignWarningCode

def evaluate_sequence(pages: list[PageComposition]) -> list[DesignWarning]:
    """
    Checks for visual monotony across the sequence of generated pages.
    """
    warnings = []
    
    if len(pages) < 3:
        return warnings
        
    consecutive_pattern_count = 0
    last_pattern = None
    
    for page in pages:
        if page.composition_pattern == last_pattern:
            consecutive_pattern_count += 1
        else:
            consecutive_pattern_count = 1
            
        if consecutive_pattern_count >= 3:
            # 3 or more of the exact same layout back-to-back
            warnings.append(
                DesignWarning(
                    code=DesignWarningCode.VISUAL_MONOTONY,
                    severity="warning",
                    reason=f"Pattern {last_pattern.value} repeated {consecutive_pattern_count} times consecutively.",
                    suggested_strategy="Vary the composition pattern or page type."
                )
            )
            # Reset to avoid spamming the same warning over and over for the same block
            consecutive_pattern_count = 0
            
        last_pattern = page.composition_pattern
        
    return warnings
