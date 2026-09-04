"""
Pedagogy domain direction policy.
"""

from app.capabilities.taxonomy import CapabilityFamily, VisualGrammar
from app.director.contracts import MaterialStrategyType
from app.director.policies.base import BaseDomainPolicy


class PedagogyDomainPolicy(BaseDomainPolicy):
    domain_name = "pedagogy"
    preferred_strategies = [
        MaterialStrategyType.CONCRETE_TO_ABSTRACT,
        MaterialStrategyType.MISCONCEPTION_CORRECTION,
        MaterialStrategyType.WORKED_EXAMPLE_PROGRESSIVE,
        MaterialStrategyType.EXAM_PREPARATION,
    ]
    preferred_families = [
        CapabilityFamily.STEPWISE_REASONING,
        CapabilityFamily.COMPARATIVE_REASONING,
        CapabilityFamily.PROCESS_VISUALIZATION,
        CapabilityFamily.CONCEPT_STRUCTURE,
    ]
    preferred_visual_grammars = [
        VisualGrammar.CHECKPOINT_CARD,
        VisualGrammar.COMPARISON,
        VisualGrammar.PROCESS_FLOW,
        VisualGrammar.CONCEPT_PANEL,
    ]
