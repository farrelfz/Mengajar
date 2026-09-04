"""
Academic Writing domain direction policy.
"""

from app.capabilities.taxonomy import CapabilityFamily, VisualGrammar
from app.director.contracts import MaterialStrategyType
from app.director.policies.base import BaseDomainPolicy


class AcademicWritingDomainPolicy(BaseDomainPolicy):
    domain_name = "academic_writing"
    preferred_strategies = [
        MaterialStrategyType.ARGUMENTATION_BUILDING,
        MaterialStrategyType.CONCRETE_TO_ABSTRACT,
        MaterialStrategyType.WORKED_EXAMPLE_PROGRESSIVE,
    ]
    preferred_families = [
        CapabilityFamily.EVIDENCE_ANALYSIS,
        CapabilityFamily.PROCESS_VISUALIZATION,
        CapabilityFamily.CONCEPT_STRUCTURE,
        CapabilityFamily.COMPARATIVE_REASONING,
    ]
    preferred_visual_grammars = [
        VisualGrammar.REASONING_FLOW,
        VisualGrammar.PROCESS_FLOW,
        VisualGrammar.CONCEPT_MAP,
        VisualGrammar.COMPARISON,
    ]
