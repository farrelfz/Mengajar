"""
Scientific Thinking domain direction policy.
"""

from app.capabilities.taxonomy import CapabilityFamily, VisualGrammar
from app.director.contracts import MaterialStrategyType
from app.director.policies.base import BaseDomainPolicy


class ScientificThinkingDomainPolicy(BaseDomainPolicy):
    domain_name = "scientific_thinking"
    preferred_strategies = [
        MaterialStrategyType.SCIENTIFIC_REASONING,
        MaterialStrategyType.CONCEPTUAL_DISCOVERY,
        MaterialStrategyType.PROBLEM_BASED_LEARNING,
    ]
    preferred_families = [
        CapabilityFamily.EVIDENCE_ANALYSIS,
        CapabilityFamily.PROCESS_VISUALIZATION,
        CapabilityFamily.RELATIONSHIP_MAPPING,
        CapabilityFamily.COMPARATIVE_REASONING,
    ]
    preferred_visual_grammars = [
        VisualGrammar.REASONING_FLOW,
        VisualGrammar.PROCESS_FLOW,
        VisualGrammar.ANNOTATED_DIAGRAM,
        VisualGrammar.COMPARISON,
    ]
