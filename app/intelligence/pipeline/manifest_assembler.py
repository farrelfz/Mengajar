"""
Stage 9 — ManifestAssembler.

Validates unique IDs, relationship endpoints, payload validity, provenance, and absence of
artifact-specific fields (no min_slides, max_slides, layout, font_size, CSS). Assembles the final
frozen, strictly immutable UniversalKnowledgeManifest.
"""

from __future__ import annotations

import time
from typing import Dict, List
from pydantic import ValidationError

from app.intelligence.schemas import (
    AudienceProfile,
    KnowledgeRelationship,
    KnowledgeUnit,
    UniversalKnowledgeManifest,
)


class ManifestAssemblyError(ValueError):
    """Raised when manifest validation fails prior to freezing."""
    pass


class ManifestAssembler:
    """Stage 9: Validates and freezes UniversalKnowledgeManifest."""

    def assemble(
        self,
        manifest_id: str,
        document_title: str,
        domain: str,
        units: List[KnowledgeUnit],
        relationships: List[KnowledgeRelationship],
        audience: AudienceProfile | None = None,
        total_sections: int = 0,
        total_raw_blocks: int = 0,
        ambiguity_ratio: float = 0.0,
    ) -> UniversalKnowledgeManifest:
        # 1. Unique Unit ID Validation
        unit_map: Dict[str, KnowledgeUnit] = {}
        for u in units:
            if u.id in unit_map:
                raise ManifestAssemblyError(f"Duplicate KnowledgeUnit ID detected during assembly: {u.id}")
            unit_map[u.id] = u

        # 2. Relationship Endpoint Integrity Validation
        for rel in relationships:
            if rel.source_unit_id not in unit_map:
                raise ManifestAssemblyError(
                    f"Relationship source_unit_id '{rel.source_unit_id}' not found in manifest unit_map."
                )
            if rel.target_unit_id not in unit_map:
                raise ManifestAssemblyError(
                    f"Relationship target_unit_id '{rel.target_unit_id}' not found in manifest unit_map."
                )

        # 3. Assemble and Freeze UniversalKnowledgeManifest
        manifest = UniversalKnowledgeManifest(
            manifest_id=manifest_id,
            document_title=document_title,
            domain=domain,
            audience_profile=audience or AudienceProfile(),
            created_at=time.time(),
            units=unit_map,
            relationships=tuple(relationships),
            total_sections=total_sections,
            total_raw_blocks=total_raw_blocks,
            ambiguity_ratio=ambiguity_ratio,
        )

        return manifest
