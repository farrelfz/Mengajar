"""
KIR AI Document Intelligence — Capability Registry.

Central catalog where all parameterized capabilities register and are discovered.
Enforces duplicate ID prevention, namespacing validation, domain isolation,
and multi-axis taxonomy indexing.
"""

from __future__ import annotations

import logging
from enum import Enum
from typing import Any

from app.capabilities.contracts import Capability, CapabilityMetadata
from app.capabilities.taxonomy import (
    CapabilityFamily,
    DensityProfile,
    InformationStructure,
    PedagogicalRole,
    SemanticIntent,
    VisualGrammar,
)

log = logging.getLogger(__name__)


class CapabilityRegistry:
    """Singleton/Injectable central registry for all system capabilities with multi-axis taxonomy indexing."""

    _instance: CapabilityRegistry | None = None

    def __init__(self) -> None:
        self._capabilities: dict[str, Capability[Any]] = {}
        self._tag_index: dict[str, set[str]] = {}
        self._category_index: dict[str, set[str]] = {}
        self._domain_index: dict[str, set[str]] = {}
        
        # Taxonomy Indices
        self._family_index: dict[str, set[str]] = {}
        self._intent_index: dict[str, set[str]] = {}
        self._structure_index: dict[str, set[str]] = {}
        self._pedagogy_index: dict[str, set[str]] = {}
        self._grammar_index: dict[str, set[str]] = {}
        self._density_index: dict[str, set[str]] = {}

    @classmethod
    def get_instance(cls) -> CapabilityRegistry:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset(cls) -> None:
        """Reset the singleton instance (useful in tests)."""
        cls._instance = None

    def register(self, capability: Capability[Any], overwrite: bool = False) -> None:
        """Register a new capability in the catalog and index its taxonomy signature."""
        cap_id = capability.metadata.capability_id

        # Namespace format check: category.sub.name
        if "." not in cap_id:
            log.warning("Capability ID '%s' lacks namespacing (expected domain.name or category.name).", cap_id)

        # Duplicate ID check
        if cap_id in self._capabilities and not overwrite:
            raise ValueError(f"Capability with ID '{cap_id}' is already registered. Set overwrite=True to replace.")

        self._capabilities[cap_id] = capability

        # 1. Index by category & domain
        cat = capability.metadata.category
        self._category_index.setdefault(cat, set()).add(cap_id)

        dom = capability.metadata.domain
        self._domain_index.setdefault(dom, set()).add(cap_id)

        # 2. Index by semantic tags
        for tag in capability.metadata.semantic_tags:
            tag_clean = tag.lower().strip()
            self._tag_index.setdefault(tag_clean, set()).add(cap_id)

        # 3. Index by canonical taxonomy
        fam = capability.metadata.family.value if isinstance(capability.metadata.family, Enum) else str(capability.metadata.family)
        self._family_index.setdefault(fam, set()).add(cap_id)

        intent = capability.metadata.primary_intent.value if isinstance(capability.metadata.primary_intent, Enum) else str(capability.metadata.primary_intent)
        self._intent_index.setdefault(intent, set()).add(cap_id)

        if capability.metadata.taxonomy:
            for extra_intent in capability.metadata.taxonomy.supported_intents:
                ex_val = extra_intent.value if isinstance(extra_intent, Enum) else str(extra_intent)
                self._intent_index.setdefault(ex_val, set()).add(cap_id)

        struct = capability.metadata.structure.value if isinstance(capability.metadata.structure, Enum) else str(capability.metadata.structure)
        self._structure_index.setdefault(struct, set()).add(cap_id)

        ped = capability.metadata.pedagogical_role.value if isinstance(capability.metadata.pedagogical_role, Enum) else str(capability.metadata.pedagogical_role)
        self._pedagogy_index.setdefault(ped, set()).add(cap_id)

        gram = capability.metadata.visual_grammar.value if isinstance(capability.metadata.visual_grammar, Enum) else str(capability.metadata.visual_grammar)
        self._grammar_index.setdefault(gram, set()).add(cap_id)

        dens = capability.metadata.density.value if isinstance(capability.metadata.density, Enum) else str(capability.metadata.density)
        self._density_index.setdefault(dens, set()).add(cap_id)

        log.debug("Registered capability: %s in family %s (intent: %s, domain: %s)", cap_id, fam, intent, dom)

    def get(self, capability_id: str) -> Capability[Any] | None:
        """Retrieve capability by exact ID."""
        return self._capabilities.get(capability_id)

    def list_all(self) -> list[Capability[Any]]:
        """List all registered capabilities."""
        return list(self._capabilities.values())

    def list_by_category(self, category: str) -> list[Capability[Any]]:
        """List capabilities by category."""
        ids = self._category_index.get(category, set())
        return [self._capabilities[cid] for cid in ids if cid in self._capabilities]

    def list_by_domain(self, domain: str) -> list[Capability[Any]]:
        """List capabilities by domain."""
        ids = self._domain_index.get(domain, set())
        return [self._capabilities[cid] for cid in ids if cid in self._capabilities]

    def list_by_family(self, family: CapabilityFamily | str) -> list[Capability[Any]]:
        """List capabilities by family."""
        fam_key = family.value if isinstance(family, Enum) else str(family)
        ids = self._family_index.get(fam_key, set())
        return [self._capabilities[cid] for cid in ids if cid in self._capabilities]

    def find(
        self,
        semantic_intent: SemanticIntent | str | None = None,
        information_structure: InformationStructure | str | None = None,
        pedagogical_role: PedagogicalRole | str | None = None,
        visual_grammar: VisualGrammar | str | None = None,
        family: CapabilityFamily | str | None = None,
        density: DensityProfile | str | None = None,
        domain: str | None = None,
        artifact_type: str | None = None,
        format_id: str | None = None,
        tags: list[str] | None = None,
    ) -> list[Capability[Any]]:
        """Multi-axis intersection search across all taxonomy dimensions."""
        candidate_ids: set[str] = set(self._capabilities.keys())

        if semantic_intent:
            intent_val = semantic_intent.value if isinstance(semantic_intent, Enum) else str(semantic_intent).lower()
            candidate_ids &= self._intent_index.get(intent_val, set())

        if information_structure:
            struct_val = information_structure.value if isinstance(information_structure, Enum) else str(information_structure).lower()
            candidate_ids &= self._structure_index.get(struct_val, set())

        if pedagogical_role:
            role_val = pedagogical_role.value if isinstance(pedagogical_role, Enum) else str(pedagogical_role).lower()
            candidate_ids &= self._pedagogy_index.get(role_val, set())

        if visual_grammar:
            gram_val = visual_grammar.value if isinstance(visual_grammar, Enum) else str(visual_grammar).lower()
            candidate_ids &= self._grammar_index.get(gram_val, set())

        if family:
            fam_val = family.value if isinstance(family, Enum) else str(family).lower()
            candidate_ids &= self._family_index.get(fam_val, set())

        if density:
            dens_val = density.value if isinstance(density, Enum) else str(density).lower()
            candidate_ids &= self._density_index.get(dens_val, set())

        if domain and domain != "general":
            domain_matches = self._domain_index.get(domain, set()) | self._domain_index.get("general", set())
            candidate_ids &= domain_matches

        if tags:
            tag_matched: set[str] = set()
            for t in tags:
                tag_clean = t.lower().strip()
                tag_matched.update(self._tag_index.get(tag_clean, set()))
            if tag_matched:
                candidate_ids &= tag_matched

        candidates = [self._capabilities[cid] for cid in candidate_ids if cid in self._capabilities]

        if artifact_type:
            candidates = [
                c for c in candidates
                if "all" in c.metadata.supported_artifacts
                or artifact_type in c.metadata.supported_artifacts
                or any(sup in artifact_type or artifact_type in sup for sup in c.metadata.supported_artifacts)
            ]

        if format_id:
            candidates = [
                c for c in candidates
                if not c.metadata.taxonomy
                or format_id in c.metadata.taxonomy.preferred_formats
            ]

        return candidates
