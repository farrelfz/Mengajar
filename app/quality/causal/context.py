"""
Universal Document Intelligence System V5 — Quality Correlation Context Contract.

Phase 3A.2 Hardening & Phase 3B: Typed multi-dimensional context container
enabling spatial, structural, semantic, temporal, and lineage failure correlation.
"""

from __future__ import annotations

from typing import Any, Dict, Optional, Sequence, Tuple
from pydantic import BaseModel, ConfigDict, Field

from app.quality.causal.contracts import QualitySignal


class QualityCorrelationContext(BaseModel):
    """Normalized multi-dimensional context container for failure correlation."""
    model_config = ConfigDict(frozen=True)

    artifact_id: Optional[str] = None
    artifact_type: str = "UNKNOWN"
    document_id: Optional[str] = None
    section_id: Optional[str] = None
    page_number: Optional[int] = None
    slide_number: Optional[int] = None
    element_id: Optional[str] = None
    blueprint_element_id: Optional[str] = None
    knowledge_unit_ids: Tuple[str, ...] = Field(default_factory=tuple)
    semantic_role: Optional[str] = None
    layout_type: Optional[str] = None
    source_stage: Optional[str] = None
    render_stage: Optional[str] = None
    time_window: Optional[float] = None
    parent_container: Optional[str] = None
    relationship_context: Dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def from_quality_signal(cls, signal: QualitySignal) -> QualityCorrelationContext:
        """Extracts and normalizes correlation context from a QualitySignal."""
        loc = signal.location
        raw_meta = signal.raw_metadata or {}
        diag = signal.diagnostic_context or {}

        # Derive page or slide number
        slide_num = loc.slide_index
        page_num = loc.page_index if loc.page_index is not None else loc.slide_index

        # Derive section id if present
        sec_id = None
        if loc.section_index is not None:
            sec_id = f"section_{loc.section_index}"
        elif loc.chapter_index is not None:
            sec_id = f"bab_{loc.chapter_index}"
        elif loc.activity_index is not None:
            sec_id = f"activity_{loc.activity_index}"

        # Extract knowledge unit IDs
        ku_ids = tuple(loc.source_unit_ids)
        if not ku_ids and "knowledge_unit_ids" in raw_meta:
            ku_ids = tuple(raw_meta["knowledge_unit_ids"])
        elif not ku_ids and "source_unit_ids" in raw_meta:
            ku_ids = tuple(raw_meta["source_unit_ids"])

        # Extract blueprint element ID
        bp_elem_id = None
        if loc.blueprint_element_ids:
            bp_elem_id = loc.blueprint_element_ids[0]
        elif "blueprint_element_id" in raw_meta:
            bp_elem_id = raw_meta["blueprint_element_id"]
        elif "beat_id" in raw_meta:
            bp_elem_id = raw_meta["beat_id"]

        # Extract parent container / layout type
        parent_container = raw_meta.get("container_id", raw_meta.get("parent_id"))
        layout_type = raw_meta.get("layout_type", diag.get("layout_type"))
        semantic_role = raw_meta.get("semantic_role", diag.get("semantic_role"))

        return cls(
            artifact_id=raw_meta.get("artifact_id"),
            artifact_type=loc.artifact_type or "UNKNOWN",
            document_id=raw_meta.get("document_id"),
            section_id=sec_id,
            page_number=page_num,
            slide_number=slide_num,
            element_id=loc.element_id,
            blueprint_element_id=bp_elem_id,
            knowledge_unit_ids=ku_ids,
            semantic_role=semantic_role,
            layout_type=layout_type,
            source_stage=signal.source_phase,
            render_stage=signal.source_engine,
            time_window=signal.timestamp,
            parent_container=parent_container,
            relationship_context={
                "failure_domain": signal.failure_domain.value,
                "failure_code": signal.failure_code.value,
                "severity": signal.severity.value,
            },
        )
