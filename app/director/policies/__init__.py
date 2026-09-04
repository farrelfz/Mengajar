"""
Director Domain Direction Policies registry and factory.
"""

from app.director.policies.academic_writing import AcademicWritingDomainPolicy
from app.director.policies.base import (
    BaseDomainPolicy,
    DefaultDomainPolicy,
    DomainPolicyRegistry,
)
from app.director.policies.pedagogy import PedagogyDomainPolicy
from app.director.policies.physics import PhysicsDomainPolicy
from app.director.policies.presentation import PresentationDomainPolicy
from app.director.policies.research_education import ResearchEducationDomainPolicy
from app.director.policies.scientific_thinking import ScientificThinkingDomainPolicy


def get_default_policy_registry() -> DomainPolicyRegistry:
    """Instantiate and populate the canonical domain policy registry."""
    reg = DomainPolicyRegistry()
    reg.register(DefaultDomainPolicy())
    reg.register(PhysicsDomainPolicy())
    reg.register(ResearchEducationDomainPolicy())
    reg.register(AcademicWritingDomainPolicy())
    reg.register(PedagogyDomainPolicy())
    reg.register(ScientificThinkingDomainPolicy())
    reg.register(PresentationDomainPolicy())
    return reg


__all__ = [
    "BaseDomainPolicy",
    "DefaultDomainPolicy",
    "DomainPolicyRegistry",
    "PhysicsDomainPolicy",
    "ResearchEducationDomainPolicy",
    "AcademicWritingDomainPolicy",
    "PedagogyDomainPolicy",
    "ScientificThinkingDomainPolicy",
    "PresentationDomainPolicy",
    "get_default_policy_registry",
]
