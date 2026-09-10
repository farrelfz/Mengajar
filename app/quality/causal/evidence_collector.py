"""
Universal Document Intelligence System V5 — Causal Evidence Collector.

Phase 3A.1: Deterministically gathers multi-layer diagnostic evidence from:
- Source & Transformation layers (entity count, compression, selection)
- Blueprint layer (planned blocks, cognitive load, section allocation)
- Layout layer (template family, card count, slot capacity)
- Physical Render layer (bounding boxes, font distributions, collisions, raster density)
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class MultiLayerEvidence(BaseModel):
    """Immutable diagnostic evidence snapshot across the pipeline hierarchy."""
    model_config = ConfigDict(frozen=True)

    artifact_type: str
    total_pages: int = 1

    # Source Layer
    source_entity_count: int = 0
    source_word_count: int = 0

    # Transformation Layer
    selected_entity_count: int = 0
    compression_ratio: float = 1.0
    transformation_strategy: str = "DEFAULT"

    # Blueprint Layer
    mean_blocks_per_page: float = 1.0
    max_blocks_per_page: int = 1
    cognitive_load_index: float = 1.0
    page_block_counts: Dict[int, int] = Field(default_factory=dict)
    blueprint_capacity_exceeded: bool = False

    # Layout Layer
    predominant_layout_type: str = "DEFAULT"
    max_cards_per_container: int = 1
    layout_slot_capacity: int = 6

    # Render Layer
    min_observed_font_size: float = 12.0
    max_observed_font_size: float = 12.0
    is_font_globally_small: bool = False
    is_font_isolated_to_dense_pages: bool = False
    page_min_fonts: Dict[int, float] = Field(default_factory=dict)
    total_clipping_count: int = 0
    total_collision_count: int = 0
    mean_raster_density: float = 0.05
    page_collision_counts: Dict[int, int] = Field(default_factory=dict)

    # Diagnostic metadata
    raw_metadata: Dict[str, Any] = Field(default_factory=dict)


class CausalEvidenceCollector:
    """Collects multi-layer evidence from raw artifacts, ASTs, and inspection reports."""

    @classmethod
    def collect(
        cls,
        artifact_type: str,
        rendered_inspection: Any = None,
        intermediate_model: Any = None,
        source_manifest: Any = None,
    ) -> MultiLayerEvidence:
        total_pages = 1
        page_min_fonts: Dict[int, float] = {}
        page_collision_counts: Dict[int, int] = {}
        min_font = 12.0
        max_font = 12.0
        clipping_cnt = 0
        collision_cnt = 0
        raster_density = 0.05

        # 1. Extract physical render metrics from Phase 3A RenderedArtifactInspection
        if rendered_inspection is not None:
            total_pages = getattr(rendered_inspection, "page_count", 1)
            gm = getattr(rendered_inspection, "geometry_metrics", None)
            if gm:
                min_font = gm.min_observed_font_size
                max_font = gm.max_observed_font_size
                clipping_cnt = gm.text_clipping_instances
                collision_cnt = gm.element_collision_count
            rm = getattr(rendered_inspection, "raster_metrics", None)
            if rm:
                raster_density = rm.mean_visual_density

            # Per-page inspection details
            details = getattr(rendered_inspection, "page_details", ())
            for p in details:
                page_min_fonts[p.page_number] = p.min_font_size
                page_collision_counts[p.page_number] = 1 if p.has_collision else 0

        # 2. Extract blueprint & layout metrics from intermediate model
        page_block_counts: Dict[int, int] = {}
        max_blocks = 1
        mean_blocks = 1.0
        max_cards = 1
        strategy = "DEFAULT"

        if intermediate_model is not None:
            # Presentation deck
            slides = getattr(intermediate_model, "slides", [])
            if slides:
                total_pages = max(total_pages, len(slides))
                for idx, slide in enumerate(slides, start=1):
                    # Count bullets / cards / content items
                    items_cnt = len(getattr(slide, "bullet_points", [])) + len(getattr(slide, "cards", []))
                    page_block_counts[idx] = max(1, items_cnt)
                max_blocks = max(page_block_counts.values(), default=1)
                mean_blocks = sum(page_block_counts.values()) / max(1, len(page_block_counts))

            # Worksheet document
            sections = getattr(intermediate_model, "sections", [])
            if sections:
                strategy = "WORKSHEET"
                for idx, sec in enumerate(sections, start=1):
                    q_cnt = len(getattr(sec, "questions", [])) + len(getattr(sec, "activities", []))
                    page_block_counts[idx] = max(1, q_cnt)
                max_blocks = max(page_block_counts.values(), default=1)
                mean_blocks = sum(page_block_counts.values()) / max(1, len(page_block_counts))

        # Determine if tiny font is global vs isolated
        # presentation threshold 11.0pt, document threshold 8.5pt
        thresh = 11.0 if artifact_type == "PRESENTATION" else 8.5
        small_pages = [p for p, sz in page_min_fonts.items() if sz < thresh]
        is_global_small = (len(small_pages) / max(1, len(page_min_fonts))) > 0.70 if page_min_fonts else False
        is_isolated_small = len(small_pages) > 0 and not is_global_small

        # Blueprint capacity check
        # For presentation, > 5 items per slide is crowded. For A4, > 8 blocks.
        cap_limit = 5 if artifact_type == "PRESENTATION" else 8
        is_cap_exceeded = max_blocks > cap_limit

        return MultiLayerEvidence(
            artifact_type=artifact_type,
            total_pages=total_pages,
            transformation_strategy=strategy,
            mean_blocks_per_page=round(mean_blocks, 2),
            max_blocks_per_page=max_blocks,
            cognitive_load_index=round(max_blocks / cap_limit, 2),
            page_block_counts=page_block_counts,
            blueprint_capacity_exceeded=is_cap_exceeded,
            max_cards_per_container=max_cards,
            layout_slot_capacity=cap_limit,
            min_observed_font_size=min_font,
            max_observed_font_size=max_font,
            is_font_globally_small=is_global_small,
            is_font_isolated_to_dense_pages=is_isolated_small,
            page_min_fonts=page_min_fonts,
            total_clipping_count=clipping_cnt,
            total_collision_count=collision_cnt,
            mean_raster_density=raster_density,
            page_collision_counts=page_collision_counts,
        )
