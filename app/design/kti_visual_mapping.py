"""
KIR AI Document Intelligence — KTI Visual Mapping.

Dedicated rules for visualizing KTI BAB 1-5 content with distinct treatments.
"""

from app.intelligence.schemas import ContentType
from app.design.schemas import ComponentFamily, VisualWeight


def get_kti_component_family(role: ContentType) -> tuple[ComponentFamily, VisualWeight]:
    """
    Returns the visual component family and weight for specific KTI roles.
    This ensures that different epistemic concepts (e.g. Data vs Interpretation)
    receive visually distinct treatments.
    """
    
    # BAB 1
    if role == ContentType.RESEARCH_PROBLEM:
        return ComponentFamily.WARNING_BLOCK, VisualWeight.DOMINANT
    if role == ContentType.RESEARCH_OBJECTIVE:
        return ComponentFamily.KEY_STATEMENT, VisualWeight.STRONG
    if role == ContentType.RESEARCH_HYPOTHESIS:
        return ComponentFamily.INSIGHT_BLOCK, VisualWeight.NORMAL
        
    # BAB 2
    if role == ContentType.KEY_CONCEPT:
        return ComponentFamily.CALLOUT, VisualWeight.STRONG
    if role == ContentType.RESEARCH_GAP:
        return ComponentFamily.WARNING_BLOCK, VisualWeight.STRONG
        
    # BAB 3
    if role == ContentType.RESEARCH_METHOD:
        return ComponentFamily.STEP_BLOCK, VisualWeight.NORMAL
        
    # BAB 4 (Explicit differentiation)
    if role in {ContentType.DATA, ContentType.DATA_POINT}:
        return ComponentFamily.DATA_BLOCK, VisualWeight.NORMAL
    if role in {ContentType.RESEARCH_RESULT, ContentType.RESULT}:
        return ComponentFamily.INSIGHT_BLOCK, VisualWeight.STRONG
    if role in {ContentType.RESEARCH_FINDING, ContentType.FINDING}:
        return ComponentFamily.KEY_STATEMENT, VisualWeight.DOMINANT
    if role in {ContentType.RESEARCH_INTERPRETATION, ContentType.INTERPRETATION}:
        return ComponentFamily.TEXT_BLOCK, VisualWeight.NORMAL
    if role in {ContentType.RESEARCH_DISCUSSION, ContentType.DISCUSSION}:
        return ComponentFamily.COMPARISON_BLOCK, VisualWeight.NORMAL
        
    # BAB 5 (Explicit differentiation)
    if role in {ContentType.RESEARCH_CONCLUSION, ContentType.CONCLUSION}:
        return ComponentFamily.SUMMARY_BLOCK, VisualWeight.DOMINANT
    if role in {ContentType.RESEARCH_LIMITATION, ContentType.LIMITATION}:
        return ComponentFamily.WARNING_BLOCK, VisualWeight.NORMAL
    if role in {ContentType.RESEARCH_RECOMMENDATION, ContentType.RECOMMENDATION}:
        return ComponentFamily.CALLOUT, VisualWeight.STRONG
    if role in {ContentType.RESEARCH_FUTURE_WORK, ContentType.FUTURE_WORK}:
        return ComponentFamily.STEP_BLOCK, VisualWeight.NORMAL
    
    # Default
    return ComponentFamily.TEXT_BLOCK, VisualWeight.NORMAL
