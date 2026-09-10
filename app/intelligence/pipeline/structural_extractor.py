"""
Stage 1 — StructuralExtractor.

Parses raw Markdown into a canonical AST hierarchy (StructuralTree).
100% deterministic, 0 AI calls, NO semantic inference.
"""

from __future__ import annotations

import hashlib
import re
from typing import Any, List
from pydantic import BaseModel, Field

from app.intelligence.markdown_tree_parser import ContentBlock, ContentTree, MarkdownTreeParser


class StructuralSection(BaseModel):
    section_id: str
    level: int
    title: str
    heading_path: List[str] = Field(default_factory=list)
    blocks: List[ContentBlock] = Field(default_factory=list)


class StructuralTree(BaseModel):
    source_document_id: str
    source_filename: str
    source_fingerprint: str
    title: str
    sections: List[StructuralSection] = Field(default_factory=list)
    total_blocks_count: int = 0


class StructuralExtractor:
    """Stage 1: Deterministic Markdown AST Parser."""

    def __init__(self, parser: MarkdownTreeParser | None = None) -> None:
        self.parser = parser or MarkdownTreeParser()

    def extract(self, raw_text: str, source_filename: str = "input.md") -> StructuralTree:
        doc_title = source_filename.replace(".md", "").replace("_", " ").title()
        tree: ContentTree = self.parser.parse(raw_text, document_title=doc_title)

        # Compute stable source fingerprint
        fingerprint = hashlib.sha256(raw_text.encode("utf-8")).hexdigest()[:16]
        doc_id = f"doc_{fingerprint[:8]}"

        structural_sections: List[StructuralSection] = []
        for sec in tree.all_sections_flat():
            heading_path = [s.title for s in tree.all_sections_flat() if s.id != sec.id and sec.id.startswith(s.id)]
            heading_path.append(sec.title)
            structural_sections.append(
                StructuralSection(
                    section_id=sec.id,
                    level=sec.level,
                    title=sec.title,
                    heading_path=heading_path,
                    blocks=sec.blocks,
                )
            )

        return StructuralTree(
            source_document_id=doc_id,
            source_filename=source_filename,
            source_fingerprint=fingerprint,
            title=tree.title or doc_title,
            sections=structural_sections,
            total_blocks_count=tree.total_blocks_count,
        )
