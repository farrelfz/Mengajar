"""
KIR AI Document Intelligence — Visual Hierarchy Engine.

Maps semantic roles, importance scores, and KTI constraints into visual hierarchy levels.
"""

from app.intelligence.schemas import ContentUnit, ContentType, DocumentMode
from app.design.schemas import VisualHierarchyLevel, TypographyScale, VisualWeight


def determine_hierarchy(unit: ContentUnit, mode: DocumentMode) -> VisualHierarchyLevel:
    """
    Determines the visual hierarchy level of a content unit.
    Hierarchy Level 1 is the most prominent (e.g., Hero/Display).
    Hierarchy Level 4 is the least prominent (e.g., Metadata/Caption).
    """
    
    # 1. Check KTI Research Roles (They carry inherent hierarchy)
    role = unit.research_role or unit.content_type
    
    level_1_roles = {
        ContentType.TITLE, 
        ContentType.RESEARCH_PROBLEM,
        ContentType.RESEARCH_OBJECTIVE,
        ContentType.RESEARCH_FINDING,
        ContentType.CONCLUSION
    }
    
    level_2_roles = {
        ContentType.RESEARCH_QUESTION,
        ContentType.RESEARCH_HYPOTHESIS,
        ContentType.KEY_CONCEPT,
        ContentType.RESEARCH_RESULT,
        ContentType.INTERPRETATION,
        ContentType.RECOMMENDATION,
        ContentType.RESEARCH_GAP,
        ContentType.RESEARCH_GAP_KTI
    }
    
    level_4_roles = {
        ContentType.REFERENCE,
        ContentType.METADATA,
        ContentType.CAPTION if hasattr(ContentType, 'CAPTION') else ContentType.OTHER,
        ContentType.TIME_AND_PLACE
    }
    
    if role in level_1_roles:
        return VisualHierarchyLevel.LEVEL_1
    if role in level_2_roles:
        return VisualHierarchyLevel.LEVEL_2
    if role in level_4_roles:
        return VisualHierarchyLevel.LEVEL_4
        
    # 2. Use importance score for generic content
    # Note: Importance score is evaluated in Batch 2 (not provided in this scope, but assume we map density/depth)
    if unit.depth == 0 and unit.title:
        return VisualHierarchyLevel.LEVEL_1
    if unit.depth == 1 and unit.title:
        return VisualHierarchyLevel.LEVEL_2
        
    # Default body content
    return VisualHierarchyLevel.LEVEL_3


def map_hierarchy_to_typography(level: VisualHierarchyLevel, mode: DocumentMode) -> TypographyScale:
    """
    Translates a hierarchy level into a semantic typography scale based on document mode.
    Presentation mode scales up relative to A4.
    """
    if mode == DocumentMode.PRESENTATION_16_9:
        mapping = {
            VisualHierarchyLevel.LEVEL_1: TypographyScale.HERO,
            VisualHierarchyLevel.LEVEL_2: TypographyScale.HEADLINE,
            VisualHierarchyLevel.LEVEL_3: TypographyScale.BODY_LARGE,
            VisualHierarchyLevel.LEVEL_4: TypographyScale.SUPPORTING
        }
    else:  # A4_TUTORIAL
        mapping = {
            VisualHierarchyLevel.LEVEL_1: TypographyScale.TITLE,
            VisualHierarchyLevel.LEVEL_2: TypographyScale.SECTION,
            VisualHierarchyLevel.LEVEL_3: TypographyScale.BODY,
            VisualHierarchyLevel.LEVEL_4: TypographyScale.CAPTION
        }
    return mapping[level]


def map_hierarchy_to_weight(level: VisualHierarchyLevel) -> VisualWeight:
    """Assigns abstract visual weight based on hierarchy level."""
    mapping = {
        VisualHierarchyLevel.LEVEL_1: VisualWeight.DOMINANT,
        VisualHierarchyLevel.LEVEL_2: VisualWeight.STRONG,
        VisualHierarchyLevel.LEVEL_3: VisualWeight.NORMAL,
        VisualHierarchyLevel.LEVEL_4: VisualWeight.LIGHT
    }
    return mapping[level]
