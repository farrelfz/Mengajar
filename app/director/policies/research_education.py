"""
Research Education domain direction policy.
"""

from app.capabilities.taxonomy import CapabilityFamily, VisualGrammar
from app.director.contracts import MaterialStrategyType
from app.director.policies.base import BaseDomainPolicy


class ResearchEducationDomainPolicy(BaseDomainPolicy):
    domain_name = "research_education"
    preferred_strategies = [
        MaterialStrategyType.RESEARCH_METHOD_TUTORIAL,
        MaterialStrategyType.PROBLEM_BASED_LEARNING,
        MaterialStrategyType.SCIENTIFIC_REASONING,
    ]
    preferred_families = [
        CapabilityFamily.CONCEPT_STRUCTURE,
        CapabilityFamily.COMPARATIVE_REASONING,
        CapabilityFamily.RELATIONSHIP_MAPPING,
        CapabilityFamily.PROCESS_VISUALIZATION,
    ]
    preferred_visual_grammars = [
        VisualGrammar.CONCEPT_MAP,
        VisualGrammar.COMPARISON,
        VisualGrammar.ANNOTATED_DIAGRAM,
        VisualGrammar.PROCESS_FLOW,
    ]
