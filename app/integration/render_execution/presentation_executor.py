"""
Universal Knowledge Core — Presentation Renderer Executor.

Phase 2B Controlled Renderer Execution & Artifact Fidelity:
Executes legacy SlideGenerator and MasterRenderEngine to realize presentation decks
from adapted LegacyPresentationDeck models.
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from app.composition.schemas import (
    ContentBlock as CompositionBlock,
    DocumentComposition,
    PageComposition,
    PageRegion,
    RegionRole,
)
from app.design.schemas import ComponentFamily
from app.intelligence.markdown_tree_parser import ContentBlock as SourceBlock, SemanticBlockType
from app.intelligence.schemas import DocumentMode
from app.integration.artifact_bridge.contracts import RenderArtifact
from app.integration.render_execution.execution_contract import RendererExecutor
from app.integration.render_execution.renderer_result import RendererExecutionResult
from app.integration.renderer_adapters.contracts import LegacyPresentationDeck, SlideBlueprint
from app.integration.renderer_adapters.presentation_adapter import PresentationContractAdapter
from app.presentation.slide_architect import PlannedSlide
from app.presentation.slide_generator import GeneratedSlide, SlideGenerator
from app.rendering.engine import MasterRenderEngine

SUPPORTED_LAYOUTS = {
    "hero_composition",
    "formula_explainer",
    "three_column_comparison",
    "triangle_relationship",
    "data_table",
    "risk_matrix",
    "timeline_horizontal",
    "minimal_question",
    "synthesis",
    "concept_card",
}


class PresentationExecutor(RendererExecutor):
    """Executes legacy SlideGenerator and MasterRenderEngine for presentation decks."""

    def __init__(self, templates_dir: Optional[Path] = None):
        self.templates_dir = (
            templates_dir
            or Path(__file__).parent.parent.parent / "rendering" / "html" / "templates"
        )
        self.generator = SlideGenerator()

    @property
    def supported_artifact_type(self) -> str:
        return "PRESENTATION"

    def execute(
        self,
        legacy_model: LegacyPresentationDeck,
        output_dir: Path,
        output_filename: Optional[str] = None,
    ) -> RendererExecutionResult:
        """Renders LegacyPresentationDeck into HTML and PDF."""
        start_time = time.time()
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        generated_slides: List[GeneratedSlide] = []
        source_element_ids_rendered: List[str] = []
        errors: List[str] = []
        warnings: List[str] = []

        # 1. Translate SlideBlueprints into PlannedSlides and generate HTML
        pages: List[PageComposition] = []

        for slide in legacy_model.slides:
            layout = slide.layout if slide.layout in SUPPORTED_LAYOUTS else "concept_card"
            source_refs = list(slide.source_element_ids or slide.source_refs)
            source_element_ids_rendered.extend(source_refs)

            # Build source block for SlideGenerator
            body_content = slide.content or (slide.bullet_points[0] if slide.bullet_points else "")
            key_block = SourceBlock(
                id=f"block_{slide.slide_id}",
                type=SemanticBlockType.PARAGRAPH,
                content=body_content,
                metadata={"bullet_points": list(slide.bullet_points)},
            )

            planned = PlannedSlide(
                slide_id=slide.slide_id,
                slide_number=slide.slide_number,
                act_id=slide.act_id,
                act_name=slide.act_name,
                title=slide.title,
                subtitle=slide.subtitle,
                layout=layout,
                narrative_function=slide.narrative_function,
                visual_priority=slide.visual_priority,
                visual_intent=slide.visual_intent,
                key_blocks=[key_block],
                source_refs=source_refs,
            )

            gen = self.generator.generate_slide(planned)
            generated_slides.append(gen)

            if gen.has_sanitization_error:
                errors.append(f"Sanitization error on slide {gen.slide_id}")
            if gen.has_hallucination_warning:
                warnings.append(f"Hallucination warning on slide {gen.slide_id}")

            # 2. Wrap into PageComposition
            c_block = CompositionBlock(
                block_id=f"comp_{gen.slide_id}",
                component_family=ComponentFamily.TEXT_BLOCK,
                source_unit_ids=source_refs,
                rendered_html=gen.rendered_html,
            )
            page = PageComposition(
                page_number=gen.slide_number,
                page_type="slide",
                composition_type="slide_presentation",
                hierarchy_level=1,
                regions={
                    RegionRole.PRIMARY: PageRegion(
                        role=RegionRole.PRIMARY,
                        blocks=[c_block],
                    )
                },
                source_unit_ids=source_refs,
                metadata={"title": gen.title, "layout": gen.layout},
            )
            pages.append(page)

        # 3. Assemble DocumentComposition
        slug = output_filename or "presentation"
        composition = DocumentComposition(
            composition_id=f"comp_pres_{slug}",
            mode=DocumentMode.PRESENTATION_16_9,
            format_id="presentation_16_9",
            theme_reference="default",
            source_blueprint_id="bp_presentation",
            pages=pages,
            metadata={"title": legacy_model.deck_title, "format_id": "presentation_16_9"},
        )

        # 4. Invoke MasterRenderEngine
        render_engine = MasterRenderEngine(
            templates_dir=self.templates_dir,
            output_dir=output_dir,
        )
        render_res = render_engine.render(composition, output_filename=slug)

        duration = (time.time() - start_time) * 1000
        html_p = output_dir / f"{slug}.html"
        pdf_p = Path(render_res.pdf_path) if render_res.pdf_path else (output_dir / f"{slug}.pdf")

        return RendererExecutionResult(
            success=render_res.success and len(errors) == 0,
            artifact_type="PRESENTATION",
            html_path=html_p if html_p.exists() else None,
            pdf_path=pdf_p if pdf_p.exists() else None,
            total_pages=len(pages),
            source_element_ids_rendered=tuple(dict.fromkeys(source_element_ids_rendered)),
            rendered_objects_count=len(generated_slides),
            execution_duration_ms=round(duration, 2),
            errors=tuple(errors + list(render_res.errors)),
            warnings=tuple(warnings),
            metadata={
                "deck_title": legacy_model.deck_title,
                "total_slides": len(legacy_model.slides),
                "layout_distribution": legacy_model.layout_distribution,
            },
        )

    def execute_from_render_artifact(
        self,
        render_artifact: RenderArtifact,
        output_dir: Path,
        output_filename: Optional[str] = None,
        **adapter_kwargs: Any,
    ) -> RendererExecutionResult:
        """Adapts RenderArtifact to LegacyPresentationDeck and renders."""
        adapter = PresentationContractAdapter()
        deck = adapter.adapt(render_artifact, **adapter_kwargs)
        return self.execute(deck, output_dir=output_dir, output_filename=output_filename)
