"""
Universal Document Intelligence System V5 — Quality Dimension Model.

Phase 2C: Universal and specialized quality dimensions for artifact evaluation.
Base dimensions apply across all artifacts; specialized dimensions capture
artifact-specific pedagogical, scientific, reading, and visual requirements.
"""

from __future__ import annotations

from enum import Enum
from typing import Dict, List, Set
from pydantic import BaseModel, ConfigDict, Field


class BaseQualityDimension(str, Enum):
    """Base universal quality dimensions evaluated across all artifact types."""
    STRUCTURAL_QUALITY = "structural_quality"
    INFORMATION_DESIGN = "information_design"
    READABILITY = "readability"
    COMPOSITION = "composition"
    RHYTHM = "rhythm"
    ARTIFACT_SPECIFIC = "artifact_specific"


class PresentationDimension(str, Enum):
    """Specialized dimensions for slide presentations."""
    VISUAL_HIERARCHY = "visual_hierarchy"
    VISUAL_GRAMMAR_ALIGNMENT = "visual_grammar_alignment"
    COMPOSITION_DIVERSITY = "composition_diversity"
    SLIDE_RHYTHM = "slide_rhythm"


class HandoutDimension(str, Enum):
    """Specialized dimensions for reading handouts."""
    READING_FLOW = "reading_flow"
    HIERARCHY_QUALITY = "hierarchy_quality"
    PAGE_BALANCE = "page_balance"
    EXPLANATORY_COHERENCE = "explanatory_coherence"


class WorksheetDimension(str, Enum):
    """Specialized dimensions for active learning worksheets."""
    INQUIRY_INTEGRITY = "inquiry_integrity"
    INTERACTION_QUALITY = "interaction_quality"
    WORKSPACE_ADEQUACY = "workspace_adequacy"
    ANTI_SPOILING_INTEGRITY = "anti_spoiling_integrity"


class ScientificDocumentDimension(str, Enum):
    """Specialized dimensions for academic scientific documents."""
    ARGUMENT_INTEGRITY = "argument_integrity"
    EVIDENCE_DISCIPLINE = "evidence_discipline"
    ACADEMIC_STRUCTURE = "academic_structure"
    CITATION_INTEGRITY = "citation_integrity"


SPECIALIZED_DIMENSIONS_BY_TYPE: Dict[str, List[str]] = {
    "PRESENTATION": [d.value for d in PresentationDimension],
    "HANDOUT": [d.value for d in HandoutDimension],
    "WORKSHEET": [d.value for d in WorksheetDimension],
    "SCIENTIFIC_DOCUMENT": [d.value for d in ScientificDocumentDimension],
}
