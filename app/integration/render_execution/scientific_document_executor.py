"""
Universal Knowledge Core — Scientific Document Renderer Executor.

Phase 2B Controlled Renderer Execution & Artifact Fidelity:
Maps LegacyScientificDocument models into DocumentComposition adhering to standard
Indonesian KTI chapters (BAB I - BAB V), explicit evidence citation grounding,
and limitation demarcation.
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
from app.integration.renderer_adapters.contracts import (
    LegacyKtiBabSection,
    LegacyScientificDocument,
    LegacyScientificSubsection,
)
from app.integration.renderer_adapters.scientific_document_adapter import (
    ScientificDocumentContractAdapter,
)
from app.rendering.engine import MasterRenderEngine


def _render_subsection_html(sub: LegacyScientificSubsection) -> str:
    """Renders a single KTI subsection with claims, evidence items, and limitations."""
    title_esc = html.escape(sub.title)

    # 1. Claims
    claims_html = ""
    for c in sub.claims:
        c_esc = html.escape(c).replace("\n", "<br/>")
        # Add inline citation tags if evidence IDs exist
        cite_str = ""
        if sub.evidence_ids:
            cites = ", ".join(f"Bukti: {eid}" for eid in sub.evidence_ids)
            cite_str = f' <span style="font-size: 8.5pt; color: #0284c7; font-weight: 600;">[{cites}]</span>'
        claims_html += f'<p style="font-size: 10pt; line-height: 1.6; color: #1e293b; margin-bottom: 8px;">{c_esc}{cite_str}</p>'

    # 2. Evidence items
    evidence_html = ""
    if sub.evidence_items:
        items = ""
        for ev in sub.evidence_items:
            rel_str = f' <span style="color: #64748b; font-style: italic;">(Rel: {ev.relationship_id})</span>' if ev.relationship_id else ""
            items += f"""
            <div style="font-size: 9pt; color: #0c4a6e; margin-bottom: 6px;">
                <span class="badge" style="background: #e0f2fe; color: #0369a1; font-weight: 700; padding: 2px 8px; margin-right: 6px;">
                    {ev.evidence_id}
                </span>
                <span>{html.escape(ev.evidence_text)}</span>
                {rel_str}
            </div>
            """
        evidence_html = f"""
        <div class="card subcard" style="margin-top: 10px; border-left: 4px solid #0284c7; background: #f0f9ff; padding: 12px 16px;">
            <div style="font-size: 8.5pt; font-weight: 800; color: #0369a1; text-transform: uppercase; margin-bottom: 6px;">
                Landasan Bukti Empiris
            </div>
            {items}
        </div>
        """

    # 3. Limitations
    limits_html = ""
    if sub.limitations:
        items = "".join(f"<li>{html.escape(lim)}</li>" for lim in sub.limitations)
        limits_html = f"""
        <div class="card subcard" style="margin-top: 10px; border-left: 4px solid #f59e0b; background: #fffbeb; padding: 12px 16px;">
            <div style="font-size: 8.5pt; font-weight: 800; color: #b45309; text-transform: uppercase; margin-bottom: 6px;">
                Batasan Penelitian & Validitas
            </div>
            <ul class="concept-list">{items}</ul>
        </div>
        """

    # 4. Critical Considerations
    counter_html = ""
    if sub.counter_considerations:
        items = "".join(f"<li>{html.escape(cc)}</li>" for cc in sub.counter_considerations)
        counter_html = f"""
        <div class="card subcard" style="margin-top: 10px; border-left: 4px solid #6366f1; background: #eef2ff; padding: 12px 16px;">
            <div style="font-size: 8.5pt; font-weight: 800; color: #4338ca; text-transform: uppercase; margin-bottom: 6px;">
                Pertimbangan Kritis Alternatif
            </div>
            <ul class="concept-list">{items}</ul>
        </div>
        """

    # 5. Unsupported claims notice
    unsupported_html = ""
    if sub.unsupported_claims:
        unsupported_html = """
        <div style="margin-top: 10px; padding: 8px 12px; background: #fef2f2; border: 1px solid #fecaca; border-radius: 6px; font-size: 8.5pt; color: #b91c1c;">
            <strong>Catatan Integritas Ilmiah:</strong> Klaim ini belum memiliki dukungan bukti empiris langsung dan diklasifikasikan sebagai hipotesis terbuka.
        </div>
        """

    return f"""
    <div class="scientific-subsection" id="{sub.subsection_id}" style="margin-bottom: 22px;">
        <h3 style="color: #0369a1; font-size: 11.5pt; font-weight: 700; margin: 0 0 10px 0; border-bottom: 1px solid #e2e8f0; padding-bottom: 4px;">
            {title_esc}
        </h3>
        {claims_html}
        {evidence_html}
        {limits_html}
        {counter_html}
        {unsupported_html}
    </div>
    """


class ScientificDocumentExecutor(RendererExecutor):
    """Executes MasterRenderEngine for scientific documents (KTI)."""

    def __init__(self, templates_dir: Optional[Path] = None):
        self.templates_dir = (
            templates_dir
            or Path(__file__).parent.parent.parent / "rendering" / "html" / "templates"
        )

    @property
    def supported_artifact_type(self) -> str:
        return "SCIENTIFIC_DOCUMENT"

    def execute(
        self,
        legacy_model: LegacyScientificDocument,
        output_dir: Path,
        output_filename: Optional[str] = None,
        subsections_per_page: int = 2,
    ) -> RendererExecutionResult:
        """Renders LegacyScientificDocument into HTML and PDF."""
        start_time = time.time()
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        source_element_ids_rendered: List[str] = []
        errors: List[str] = []
        warnings: List[str] = []

        pages: List[PageComposition] = []
        page_num = 1
        total_subsections = 0

        for bab in legacy_model.babs:
            if not bab.subsections:
                continue

            subs = list(bab.subsections)
            total_subsections += len(subs)
            chunk_size = max(1, subsections_per_page)

            for i in range(0, len(subs), chunk_size):
                chunk = subs[i : i + chunk_size]
                page_blocks: List[CompositionBlock] = []
                page_source_ids: List[str] = []

                # Add Bab title header on first chunk of the Bab
                if i == 0:
                    bab_header_html = f"""
                    <div class="kti-bab-header" style="margin-bottom: 18px; border-bottom: 2px solid #0284c7; padding-bottom: 8px;">
                        <h2 style="color: #0f172a; font-size: 14pt; font-weight: 800; margin: 0; letter-spacing: 0.02em;">
                            {html.escape(bab.title)}
                        </h2>
                    </div>
                    """
                    header_block = CompositionBlock(
                        block_id=f"header_{bab.bab.value}",
                        component_family=ComponentFamily.TEXT_BLOCK,
                        source_unit_ids=list(bab.source_element_ids),
                        rendered_html=bab_header_html,
                    )
                    page_blocks.append(header_block)

                for sub in chunk:
                    source_refs = list(sub.source_element_ids)
                    page_source_ids.extend(source_refs)
                    source_element_ids_rendered.extend(source_refs)

                    sub_html = _render_subsection_html(sub)
                    c_block = CompositionBlock(
                        block_id=f"cb_{sub.subsection_id}",
                        component_family=ComponentFamily.TEXT_BLOCK,
                        source_unit_ids=source_refs,
                        rendered_html=sub_html,
                    )
                    page_blocks.append(c_block)

                page = PageComposition(
                    page_number=page_num,
                    page_type="content_page",
                    composition_type="scientific_kti_document",
                    hierarchy_level=1,
                    regions={
                        RegionRole.PRIMARY: PageRegion(
                            role=RegionRole.PRIMARY,
                            blocks=page_blocks,
                        )
                    },
                    source_unit_ids=page_source_ids,
                    metadata={"bab": bab.bab.value, "subsections_count": len(chunk)},
                )
                pages.append(page)
                page_num += 1

        # Fallback if empty babs
        if not pages:
            fallback_block = CompositionBlock(
                block_id="empty_kti",
                component_family=ComponentFamily.TEXT_BLOCK,
                source_unit_ids=[],
                rendered_html="<h2>Karya Tulis Ilmiah</h2><p>Dokumen belum memiliki konten terstruktur.</p>",
            )
            pages.append(
                PageComposition(
                    page_number=1,
                    page_type="content_page",
                    composition_type="scientific_kti_document",
                    regions={RegionRole.PRIMARY: PageRegion(role=RegionRole.PRIMARY, blocks=[fallback_block])},
                )
            )

        # 2. Assemble DocumentComposition
        slug = output_filename or "scientific_document"
        composition = DocumentComposition(
            composition_id=f"comp_sci_{slug}",
            mode=DocumentMode.A4_PORTRAIT,
            format_id="a4_portrait",
            theme_reference="default",
            source_blueprint_id="bp_scientific",
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
            success=render_res.success and len(errors) == 0,
            artifact_type="SCIENTIFIC_DOCUMENT",
            html_path=html_p if html_p.exists() else None,
            pdf_path=pdf_p if pdf_p.exists() else None,
            total_pages=len(pages),
            source_element_ids_rendered=tuple(dict.fromkeys(source_element_ids_rendered)),
            rendered_objects_count=total_subsections,
            execution_duration_ms=round(duration, 2),
            errors=tuple(errors + list(render_res.errors)),
            warnings=tuple(warnings),
            metadata={
                "document_title": legacy_model.title,
                "total_babs": len(legacy_model.babs),
                "total_subsections": total_subsections,
                "total_evidence_links": legacy_model.total_evidence_links,
            },
        )

    def execute_from_render_artifact(
        self,
        render_artifact: RenderArtifact,
        output_dir: Path,
        output_filename: Optional[str] = None,
        **adapter_kwargs: Any,
    ) -> RendererExecutionResult:
        """Adapts RenderArtifact to LegacyScientificDocument and renders."""
        adapter = ScientificDocumentContractAdapter()
        if "grouping_mode" not in adapter_kwargs:
            adapter_kwargs["grouping_mode"] = "compatibility"
        doc = adapter.adapt(render_artifact, **adapter_kwargs)
        return self.execute(doc, output_dir=output_dir, output_filename=output_filename)
