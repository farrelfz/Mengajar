"""
Universal Knowledge Core — Knowledge Provenance & Origin Tracking.
"""

from __future__ import annotations

from typing import Any, List, Optional
from pydantic import BaseModel, Field


class KnowledgeProvenance(BaseModel):
    """Answers: WHERE DID THIS KNOWLEDGE COME FROM?
    
    Contains deterministic references to the source raw document, section AST,
    and line boundaries. Must NOT contain physical PDF/canvas coordinates.
    """
    source_document_id: str
    source_path: Optional[str] = None
    source_section_id: str
    source_section_title: str = ""
    source_heading_path: List[str] = Field(default_factory=list)
    block_ids: List[str] = Field(default_factory=list)
    source_start_line: Optional[int] = None
    source_end_line: Optional[int] = None
    raw_snippet: str = ""
    parser_origin: str = "markdown_ast_parser"
