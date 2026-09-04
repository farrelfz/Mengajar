"""
Presentation domain direction policy.
"""

from app.capabilities.taxonomy import CapabilityFamily, VisualGrammar
from app.director.contracts import MaterialStrategyType
from app.director.policies.base import BaseDomainPolicy


class PresentationDomainPolicy(BaseDomainPolicy):
    domain_name = "presentation"
    preferred_strategies = [
        MaterialStrategyType.PRESENTATION_STORY,
        MaterialStrategyType.QUICK_EXPLANATION,
        MaterialStrategyType.CONCRETE_TO_ABSTRACT,
    ]
    preferred_families = [
        CapabilityFamily.TITLE_FRAMING,
        CapabilityFamily.CONCEPT_STRUCTURE,
        CapabilityFamily.PROCESS_VISUALIZATION,
        CapabilityFamily.COMPARATIVE_REASONING,
    ]
    preferred_visual_grammars = [
        VisualGrammar.HERO,
        VisualGrammar.CONCEPT_PANEL,
        VisualGrammar.PROCESS_FLOW,
        VisualGrammar.COMPARISON,
    ]
