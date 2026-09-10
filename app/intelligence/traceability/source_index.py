"""
Universal Knowledge Core — Source-to-KnowledgeUnit Traceability Index.

Phase 1B Traceability boundary:
[Raw Source Markdown] <---> [KnowledgeUnit ID]
"""

from __future__ import annotations

from typing import Dict, List, Optional
from pydantic import BaseModel, Field

from app.intelligence.schemas import KnowledgeProvenance, UniversalKnowledgeManifest


class TraceabilityRecord(BaseModel):
    unit_id: str
    provenance: KnowledgeProvenance


class SourceToKnowledgeUnitTraceabilityIndex(BaseModel):
    """Bidirectional traceability index between source raw text blocks and KnowledgeUnits."""
    unit_to_provenance: Dict[str, KnowledgeProvenance] = Field(default_factory=dict)
    unit_to_all_provenances: Dict[str, List[KnowledgeProvenance]] = Field(default_factory=dict)
    section_to_units: Dict[str, List[str]] = Field(default_factory=dict)
    block_to_units: Dict[str, List[str]] = Field(default_factory=dict)

    @classmethod
    def build_from_manifest(cls, manifest: UniversalKnowledgeManifest) -> SourceToKnowledgeUnitTraceabilityIndex:
        unit_to_prov: Dict[str, KnowledgeProvenance] = {}
        unit_to_all_provs: Dict[str, List[KnowledgeProvenance]] = {}
        sec_to_units: Dict[str, List[str]] = {}
        blk_to_units: Dict[str, List[str]] = {}

        for unit_id, unit in manifest.units.items():
            all_provs = unit.all_provenances
            unit_to_prov[unit_id] = unit.provenance
            unit_to_all_provs[unit_id] = all_provs

            for prov in all_provs:
                # Index section
                sec_id = prov.source_section_id
                if sec_id not in sec_to_units:
                    sec_to_units[sec_id] = []
                if unit_id not in sec_to_units[sec_id]:
                    sec_to_units[sec_id].append(unit_id)

                # Index block IDs
                for blk_id in prov.block_ids:
                    if blk_id not in blk_to_units:
                        blk_to_units[blk_id] = []
                    if unit_id not in blk_to_units[blk_id]:
                        blk_to_units[blk_id].append(unit_id)

        return cls(
            unit_to_provenance=unit_to_prov,
            unit_to_all_provenances=unit_to_all_provs,
            section_to_units=sec_to_units,
            block_to_units=blk_to_units,
        )

    def get_provenance(self, unit_id: str) -> Optional[KnowledgeProvenance]:
        """Forward lookup: KnowledgeUnit.id -> Primary KnowledgeProvenance."""
        return self.unit_to_provenance.get(unit_id)

    def get_all_provenances(self, unit_id: str) -> List[KnowledgeProvenance]:
        """Forward lookup: KnowledgeUnit.id -> List of all KnowledgeProvenances."""
        return self.unit_to_all_provenances.get(unit_id, [])

    def get_units_by_section(self, section_id: str) -> List[str]:
        """Reverse lookup: section_id -> List[KnowledgeUnit.id]."""
        return self.section_to_units.get(section_id, [])

    def get_units_by_block(self, block_id: str) -> List[str]:
        """Reverse lookup: block_id -> List[KnowledgeUnit.id]."""
        return self.block_to_units.get(block_id, [])
