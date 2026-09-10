"""
Universal Knowledge Core — Universal Render Contract Boundary.

Phase 1D Artifact Blueprint Bridge Integration:
Defines renderer-neutral RenderArtifact, RenderSection, RenderUnit, and RenderTraceabilityRef
contracts that isolate existing renderers from Universal Knowledge Core internals.

Contains NO layout decisions, CSS, pixel offsets, or Playwright settings.
"""

from __future__ import annotations

import time
from typing import Dict, List, Tuple, Any, Optional
from pydantic import BaseModel, ConfigDict, Field


class RenderTraceabilityRef(BaseModel):
    """Traceability mapping attaching a RenderUnit to source blueprint elements and KnowledgeUnits."""
    model_config = ConfigDict(frozen=True)

    blueprint_element_id: str
    knowledge_unit_ids: Tuple[str, ...] = Field(default_factory=tuple)
    relationship_ids: Tuple[str, ...] = Field(default_factory=tuple)
    source_section_ids: Tuple[str, ...] = Field(default_factory=tuple)


class RenderUnit(BaseModel):
    """Renderer-neutral atomic rendering unit containing text, role, and semantic hints."""
    model_config = ConfigDict(frozen=True)

    unit_id: str
    role: str  # CONCEPTUAL_BEAT, EXPLANATORY_BLOCK, LEARNING_ACTIVITY, SCIENTIFIC_ARGUMENT
    title: str
    content: str
    supporting_content: Tuple[str, ...] = Field(default_factory=tuple)
    sequence_index: int
    semantic_metadata: Dict[str, Any] = Field(default_factory=dict)
    traceability_refs: RenderTraceabilityRef


class RenderSection(BaseModel):
    """Renderer-neutral structural container for grouped render units."""
    model_config = ConfigDict(frozen=True)

    section_id: str
    title: str
    sequence_index: int
    units: Tuple[RenderUnit, ...] = Field(default_factory=tuple)
    section_metadata: Dict[str, Any] = Field(default_factory=dict)


class RenderMetadata(BaseModel):
    """High-level metadata attached to a RenderArtifact."""
    model_config = ConfigDict(frozen=True)

    artifact_type: str
    document_title: str
    domain: str
    audience_level: str
    total_units: int
    total_sections: int
    rendering_hints: Dict[str, Any] = Field(default_factory=dict)


class RenderArtifact(BaseModel):
    """Authoritative, renderer-neutral contract emitted by ArtifactBlueprintBridge."""
    model_config = ConfigDict(frozen=True)

    artifact_id: str
    artifact_type: str
    document_title: str
    source_blueprint_id: str
    source_manifest_id: str
    metadata: RenderMetadata
    sections: Tuple[RenderSection, ...] = Field(default_factory=tuple)
    units: Tuple[RenderUnit, ...] = Field(default_factory=tuple)
    traceability_refs: Dict[str, RenderTraceabilityRef] = Field(default_factory=dict)
    created_at: float = Field(default_factory=time.time)
