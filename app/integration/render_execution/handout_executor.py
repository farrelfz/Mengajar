"""
Universal Knowledge Core — Handout Renderer Executor.

Phase 2B Controlled Renderer Execution & Artifact Fidelity:
Maps DocumentContent models into DocumentComposition and executes MasterRenderEngine
for clean A4 portrait continuous reading artifacts.
"""

from __future__ import annotations

import html
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
from app.intelligence.schemas import DocumentMode
from app.integration.artifact_bridge.contracts import RenderArtifact
from app.integration.render_execution.execution_contract import RendererExecutor
from app.integration.render_execution.renderer_result import RendererExecutionResult
from app.integration.renderer_adapters.contracts import DocumentContent, DocumentContentSection
from app.integration.renderer_adapters.handout_adapter import HandoutContractAdapter
from app.rendering.engine import MasterRenderEngine


def _render_section_html(sec: DocumentContentSection) -> str:
    """Renders a DocumentContentSection into structured semantic HTML."""
    heading_tag = f"h{min(max(sec.level + 1, 2), 4)}"
    title_esc = html.escape(sec.title)
    content_esc = html.escape(sec.content).replace("\n\n", "</p><p>").replace("\n", "<br/>")

    defs_html = ""
    if sec.definitions:
        items = "".join(f"<li>{html.escape(d)}</li>" for d in sec.definitions)
        defs_html = f"""
        <div class="card subcard definition-card" style="margin-top: 14px; border-left: 4px solid #3b82f6;">
            <div class="badge" style="background: #e0e7ff; color: #1e40af; margin-bottom: 8px; font-weight: 700;">DEFINISI KONSEP</div>
            <ul class="concept-list">{items}</ul>
        </div>
        """

    exs_html = ""
    if sec.examples:
        items = "".join(f"<li>{html.escape(ex)}</li>" for ex in sec.examples)
        exs_html = f"""
        <div class="card subcard example-card" style="margin-top: 14px; border-left: 4px solid #10b981;">
            <div class="badge" style="background: #dcfce7; color: #065f46; margin-bottom: 8px; font-weight: 700;">CONTOH & PENERAPAN</div>
            <ul class="concept-list">{items}</ul>
        </div>
        """

    return f"""
    <div class="handout-section" id="{sec.section_id}" style="margin-bottom: 24px;">
        <{heading_tag} style="color: #0f172a; margin-bottom: 12px; font-weight: 800; border-bottom: 1px solid #e2e8f0; padding-bottom: 6px;">{title_esc}</{heading_tag}>
        <div class="handout-body-text" style="font-size: 11pt; line-height: 1.6; color: #334155;">
            <p>{content_esc}</p>
        </div>
        {defs_html}
        {exs_html}
    </div>
    """


class HandoutExecutor(RendererExecutor):
    """Executes MasterRenderEngine for handout reading documents."""

    def __init__(self, templates_dir: Optional[Path] = None):
        self.templates_dir = (
            templates_dir
            or Path(__file__).parent.parent.parent / "rendering" / "html" / "templates"
        )

    @property
    def supported_artifact_type(self) -> str:
        return "HANDOUT"

    def execute(
        self,
        legacy_model: DocumentContent,
        output_dir: Path,
        output_filename: Optional[str] = None,
        sections_per_page: int = 2,
    ) -> RendererExecutionResult:
        """Renders DocumentContent into HTML and PDF."""
        start_time = time.time()
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        source_element_ids_rendered: List[str] = []
        pages: List[PageComposition] = []

        # 1. Distribute sections across pages
        sections = list(legacy_model.sections)
        chunk_size = max(1, sections_per_page)
        page_num = 1

        for i in range(0, len(sections), chunk_size):
            chunk = sections[i : i + chunk_size]
            page_blocks: List[CompositionBlock] = []
            page_source_ids: List[str] = []

            for sec in chunk:
                source_refs = list(sec.source_element_ids)
                page_source_ids.extend(source_refs)
                source_element_ids_rendered.extend(source_refs)

                sec_html = _render_section_html(sec)
                c_block = CompositionBlock(
                    block_id=f"cb_{sec.section_id}",
                    component_family=ComponentFamily.TEXT_BLOCK,
                    source_unit_ids=source_refs,
                    rendered_html=sec_html,
                )
                page_blocks.append(c_block)

            page = PageComposition(
                page_number=page_num,
                page_type="content_page",
                composition_type="handout_document",
                hierarchy_level=1,
                regions={
                    RegionRole.PRIMARY: PageRegion(
                        role=RegionRole.PRIMARY,
                        blocks=page_blocks,
                    )
                },
                source_unit_ids=page_source_ids,
                metadata={"section_count": len(chunk)},
            )
            pages.append(page)
            page_num += 1

        # 2. Assemble DocumentComposition
        slug = output_filename or "handout"
        composition = DocumentComposition(
            composition_id=f"comp_handout_{slug}",
            mode=DocumentMode.A4_PORTRAIT,
            format_id="a4_portrait",
            theme_reference="default",
            source_blueprint_id="bp_handout",
            pages=pages,
            metadata={"title": legacy_model.title, "format_id": "a4_portrait"},
        )

        # 3. Invoke MasterRenderEngine
        render_engine = MasterRenderEngine(
            templates_dir=self.templates_dir,
            output_dir=output_dir,
        )
        render_res = render_engine.render(composition, output_filename=slug)

        duration = (time.time() - start_time) * 1000
        html_p = output_dir / f"{slug}.html"
        pdf_p = Path(render_res.pdf_path) if render_res.pdf_path else (output_dir / f"{slug}.pdf")

        return RendererExecutionResult(
            success=render_res.success,
            artifact_type="HANDOUT",
            html_path=html_p if html_p.exists() else None,
            pdf_path=pdf_p if pdf_p.exists() else None,
            total_pages=len(pages),
            source_element_ids_rendered=tuple(dict.fromkeys(source_element_ids_rendered)),
            rendered_objects_count=len(sections),
            execution_duration_ms=round(duration, 2),
            errors=tuple(render_res.errors),
            warnings=tuple(),
            metadata={
                "document_title": legacy_model.title,
                "total_sections": len(sections),
                "outline_items_count": len(legacy_model.outline.items),
            },
        )

    def execute_from_render_artifact(
        self,
        render_artifact: RenderArtifact,
        output_dir: Path,
        output_filename: Optional[str] = None,
        **adapter_kwargs: Any,
    ) -> RendererExecutionResult:
        """Adapts RenderArtifact to DocumentContent and renders."""
        adapter = HandoutContractAdapter()
        content = adapter.adapt(render_artifact, **adapter_kwargs)
        return self.execute(content, output_dir=output_dir, output_filename=output_filename)
