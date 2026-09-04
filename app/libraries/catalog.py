"""
KIR AI Document Intelligence — Capability Catalog & Discovery API.

Provides machine-readable discovery, filtering, and summary statistics across all
registered domain packs and capability families.
"""

from __future__ import annotations

from typing import Any

from app.capabilities.contracts import Capability
from app.capabilities.registry import CapabilityRegistry
from app.capabilities.taxonomy import CapabilityFamily, SemanticIntent
from app.libraries import register_all_default_capabilities


class CapabilityCatalog:
    """Discovery API and catalog manager for all registered capabilities."""

    def __init__(self, registry: CapabilityRegistry | None = None) -> None:
        if registry is None:
            self.registry = CapabilityRegistry()
            register_all_default_capabilities(self.registry)
        else:
            self.registry = registry

    def list_domains(self) -> list[str]:
        """List all distinct domains represented in the catalog."""
        domains = {cap.metadata.domain for cap in self.registry.list_all()}
        return sorted(list(domains))

    def list_capabilities(self, domain: str | None = None) -> list[Capability[Any]]:
        """List all capabilities, optionally filtered by domain."""
        all_caps = self.registry.list_all()
        if domain is None:
            return all_caps
        return [c for c in all_caps if c.metadata.domain == domain]

    def find_by_intent(self, intent: str | SemanticIntent) -> list[Capability[Any]]:
        """Discover capabilities fulfilling a specific semantic intent."""
        intent_val = intent.value if isinstance(intent, SemanticIntent) else str(intent)
        return self.registry.find(semantic_intent=intent_val)

    def find_by_family(self, family: str | CapabilityFamily) -> list[Capability[Any]]:
        """Discover capabilities belonging to a specific capability family."""
        fam = family if isinstance(family, CapabilityFamily) else CapabilityFamily(family)
        return self.registry.list_by_family(fam)

    def get_summary(self) -> dict[str, Any]:
        """Generate statistical summary of the entire capability ecosystem."""
        all_caps = self.registry.list_all()
        by_domain: dict[str, int] = {}
        by_family: dict[str, int] = {}
        by_category: dict[str, int] = {}

        for cap in all_caps:
            d = cap.metadata.domain
            by_domain[d] = by_domain.get(d, 0) + 1

            fam = cap.metadata.family.value
            by_family[fam] = by_family.get(fam, 0) + 1

            cat = cap.metadata.category
            by_category[cat] = by_category.get(cat, 0) + 1

        return {
            "total_capabilities": len(all_caps),
            "domains_count": len(by_domain),
            "capabilities_by_domain": by_domain,
            "capabilities_by_family": by_family,
            "capabilities_by_category": by_category,
        }
