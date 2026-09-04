"""
Physics domain direction policy.
"""

from app.capabilities.taxonomy import CapabilityFamily, VisualGrammar
from app.director.contracts import MaterialStrategyType
from app.director.policies.base import BaseDomainPolicy


class PhysicsDomainPolicy(BaseDomainPolicy):
    domain_name = "physics"
    preferred_strategies = [
        MaterialStrategyType.CONCRETE_TO_ABSTRACT,
        MaterialStrategyType.MISCONCEPTION_CORRECTION,
        MaterialStrategyType.WORKED_EXAMPLE_PROGRESSIVE,
    ]
    preferred_families = [
        CapabilityFamily.SPATIAL_SYSTEMS,
        CapabilityFamily.PROCESS_VISUALIZATION,
        CapabilityFamily.QUANTITATIVE_ANALYSIS,
        CapabilityFamily.COMPARATIVE_REASONING,
    ]
    preferred_visual_grammar = [
        VisualGrammar.PROCESS_FLOW,
        VisualGrammar.EQUATION_CHAIN,
        VisualGrammar.COMPARISON,
    ]
