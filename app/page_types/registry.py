"""
KIR AI Document Intelligence — Page Type Registry.

Deterministic logic for selecting appropriate page types based on semantic roles.
"""

from app.page_types.schemas import PageType
from app.intelligence.schemas import ContentType, ContentDensity, DocumentMode, VisualIntent


class PageTypeRegistry:
    def __init__(self):
        self._types: dict[str, PageType] = {}
        
    def register(self, pt: PageType):
        self._types[pt.name] = pt
        
    def select_page_type(
        self, 
        role: ContentType, 
        intent: VisualIntent, 
        density: ContentDensity, 
        mode: DocumentMode
    ) -> str:
        """
        Deterministic selection of page type based on provided signals.
        """
        # KTI Specific logic for BAB 4 and BAB 5
        if role in {ContentType.DATA, ContentType.DATA_POINT}:
            return "DATA_FOCUS"
        if role in {ContentType.RESEARCH_RESULT, ContentType.RESULT}:
            return "RESULT_HIGHLIGHT"
        if role in {ContentType.RESEARCH_FINDING, ContentType.FINDING}:
            return "KEY_FINDING"
        if role in {ContentType.RESEARCH_INTERPRETATION, ContentType.INTERPRETATION}:
            return "INTERPRETATION"
        if role in {ContentType.RESEARCH_DISCUSSION, ContentType.DISCUSSION}:
            return "DISCUSSION"
            
        if role in {ContentType.RESEARCH_CONCLUSION, ContentType.CONCLUSION}:
            return "CONCLUSION"
        if role in {ContentType.RESEARCH_LIMITATION, ContentType.LIMITATION}:
            return "LIMITATION"
        if role in {ContentType.RESEARCH_RECOMMENDATION, ContentType.RECOMMENDATION}:
            return "RECOMMENDATION"
        if role in {ContentType.RESEARCH_FUTURE_WORK, ContentType.FUTURE_WORK}:
            return "FUTURE_WORK"
            
        # General mappings based on intent
        if intent == VisualIntent.COMPARATIVE:
            return "COMPARISON"
        if intent == VisualIntent.STEP_BY_STEP or intent == VisualIntent.PROCESS_FLOW:
            return "STEP_BY_STEP"
        if intent == VisualIntent.SUMMARY:
            return "SUMMARY"
        if intent == VisualIntent.QUOTE_HIGHLIGHT:
            return "KEY_STATEMENT"
            
        # Fallbacks based on role
        if role == ContentType.TITLE:
            return "INTRODUCTION_PAGE"
        if role == ContentType.KEY_CONCEPT:
            return "CONCEPT_EXPLANATION"
            
        return "GENERIC_CONTENT"

page_registry = PageTypeRegistry()

# Register core page types
page_registry.register(PageType(
    name="INTRODUCTION_PAGE",
    purpose="Used for title and initial document entry",
))
page_registry.register(PageType(
    name="DATA_FOCUS",
    purpose="Presents hard data evidence"
))
page_registry.register(PageType(
    name="RESULT_HIGHLIGHT",
    purpose="Highlights organized outcomes of research"
))
page_registry.register(PageType(
    name="KEY_FINDING",
    purpose="Emphasizes a key insight or discovery"
))
page_registry.register(PageType(
    name="INTERPRETATION",
    purpose="Explains the meaning of findings"
))
page_registry.register(PageType(
    name="DISCUSSION",
    purpose="Synthesizes findings with broader theory"
))
page_registry.register(PageType(
    name="CONCLUSION",
    purpose="Distilled synthesis closure"
))
page_registry.register(PageType(
    name="LIMITATION",
    purpose="Constraint acknowledgement"
))
page_registry.register(PageType(
    name="RECOMMENDATION",
    purpose="Action-oriented suggestions"
))
page_registry.register(PageType(
    name="FUTURE_WORK",
    purpose="Forward-looking continuation"
))
page_registry.register(PageType(
    name="GENERIC_CONTENT",
    purpose="Standard textual layout"
))
page_registry.register(PageType(
    name="STEP_BY_STEP",
    purpose="Sequential explanatory layout"
))
page_registry.register(PageType(
    name="COMPARISON",
    purpose="Side-by-side or contrasting layout"
))
page_registry.register(PageType(
    name="SUMMARY",
    purpose="Distilled compilation layout"
))
