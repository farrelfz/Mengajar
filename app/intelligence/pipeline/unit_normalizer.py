"""
Stage 2 — UnitNormalizer.

Normalizes raw text blocks into CandidateUnit instances while preserving exact
source line boundaries, section provenance, and structural AST context.
"""

from __future__ import annotations

import re
from typing import List, Optional
from pydantic import BaseModel, Field

from app.intelligence.markdown_tree_parser import ContentBlock, SemanticBlockType
from app.intelligence.pipeline.structural_extractor import StructuralSection, StructuralTree
from app.intelligence.schemas.provenance import KnowledgeProvenance


class CandidateUnit(BaseModel):
    candidate_id: str
    source_document_id: str
    source_fingerprint: str
    raw_content: str
    normalized_content: str
    parsed_block_type: SemanticBlockType
    provenance: KnowledgeProvenance
    parent_section_title: str
    heading_path: List[str] = Field(default_factory=list)


class UnitNormalizer:
    """Stage 2: Normalizes text and attaches AST provenance."""

    def normalize(self, tree: StructuralTree) -> List[CandidateUnit]:
        candidate_units: List[CandidateUnit] = []

        block_counter = 0
        for sec in tree.sections:
            for blk in sec.blocks:
                block_counter += 1
                raw_text = blk.content.strip()
                if not raw_text:
                    continue

                # Whitespace normalization
                normalized = re.sub(r"\s+", " ", raw_text)

                cand_id = f"cand_{sec.section_id}_{blk.id}"
                prov = KnowledgeProvenance(
                    source_document_id=tree.source_document_id,
                    source_path=tree.source_filename,
                    source_section_id=sec.section_id,
                    source_section_title=sec.title,
                    source_heading_path=sec.heading_path,
                    block_ids=[blk.id],
                    source_start_line=blk.source_line_start,
                    source_end_line=blk.source_line_end,
                    raw_snippet=raw_text[:200],
                    parser_origin="markdown_ast_parser",
                )

                candidate_units.append(
                    CandidateUnit(
                        candidate_id=cand_id,
                        source_document_id=tree.source_document_id,
                        source_fingerprint=tree.source_fingerprint,
                        raw_content=raw_text,
                        normalized_content=normalized,
                        parsed_block_type=blk.type,
                        provenance=prov,
                        parent_section_title=sec.title,
                        heading_path=sec.heading_path,
                    )
                )

        return candidate_units
