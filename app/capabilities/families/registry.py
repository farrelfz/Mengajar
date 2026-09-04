"""
KIR AI Document Generation System — Family Template Registry.

Provides central registration, indexing, and lookup for Generative Family Templates.
"""

from __future__ import annotations

import logging
from typing import Any

from app.capabilities.families.contracts import FamilyTemplate
from app.capabilities.families.templates import (
    CardCollectionTemplate,
    EvidenceChainTemplate,
    HierarchyTreeTemplate,
    LinearProcessTemplate,
    MatrixComparisonTemplate,
    ProgressionLadderTemplate,
    QuantitativeDerivationTemplate,
    RelationshipMapTemplate,
)
from app.capabilities.taxonomy import CapabilityFamily

logger = logging.getLogger(__name__)


class FamilyTemplateRegistry:
    """Registry for structural Generative Family Templates."""

    def __init__(self) -> None:
        self._templates: dict[str, FamilyTemplate[Any]] = {}
        self._family_index: dict[CapabilityFamily, list[FamilyTemplate[Any]]] = {}

    def register(self, template: FamilyTemplate[Any], overwrite: bool = False) -> None:
        """Register a family template."""
        if not template.template_id:
            raise ValueError("Template must have a non-empty template_id.")

        if template.template_id in self._templates and not overwrite:
            raise ValueError(f"Template with ID '{template.template_id}' is already registered.")

        self._templates[template.template_id] = template
        self._family_index.setdefault(template.family, []).append(template)
        logger.debug(f"Registered family template '{template.template_id}' for family {template.family}")

    def get(self, template_id: str) -> FamilyTemplate[Any] | None:
        """Retrieve a template by its template ID."""
        return self._templates.get(template_id)

    def list_by_family(self, family: CapabilityFamily) -> list[FamilyTemplate[Any]]:
        """List all templates associated with a capability family."""
        return self._family_index.get(family, [])

    def list_all(self) -> list[FamilyTemplate[Any]]:
        """List all registered templates."""
        return list(self._templates.values())


_DEFAULT_FAMILY_REGISTRY: FamilyTemplateRegistry | None = None


def get_default_family_registry() -> FamilyTemplateRegistry:
    """Singleton getter for default family template registry."""
    global _DEFAULT_FAMILY_REGISTRY
    if _DEFAULT_FAMILY_REGISTRY is None:
        reg = FamilyTemplateRegistry()
        reg.register(LinearProcessTemplate())
        reg.register(MatrixComparisonTemplate())
        reg.register(HierarchyTreeTemplate())
        reg.register(EvidenceChainTemplate())
        reg.register(ProgressionLadderTemplate())
        reg.register(QuantitativeDerivationTemplate())
        reg.register(RelationshipMapTemplate())
        reg.register(CardCollectionTemplate())
        _DEFAULT_FAMILY_REGISTRY = reg
    return _DEFAULT_FAMILY_REGISTRY
