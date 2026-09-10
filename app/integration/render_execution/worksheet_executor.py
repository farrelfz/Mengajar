"""
Universal Knowledge Core — Worksheet Renderer Executor.

Phase 2B Controlled Renderer Execution & Artifact Fidelity:
Maps LegacyWorksheetDocument models into DocumentComposition with student workspace boxes,
inquiry badges, and strictly enforced explanation withholding.
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
    LegacyWorksheetActivity,
    LegacyWorksheetDocument,
    LegacyWorksheetSection,
)
from app.integration.renderer_adapters.worksheet_adapter import WorksheetContractAdapter
from app.rendering.engine import MasterRenderEngine

INQUIRY_BADGE_COLORS = {
    "PHENOMENON": ("#faf5ff", "#7e22ce", "#d8b4fe"),
    "PREDICTION": ("#eff6ff", "#1d4ed8", "#bfdbfe"),
    "QUESTION": ("#eef2ff", "#4338ca", "#c7d2fe"),
    "OBSERVATION": ("#fffbeb", "#b45309", "#fde68a"),
    "INVESTIGATION": ("#ecfdf5", "#047857", "#a7f3d0"),
    "DATA_ANALYSIS": ("#f0fdfa", "#0f766e", "#99f6e4"),
    "REFLECTION": ("#fff1f2", "#be123c", "#fecdd3"),
}


def _render_activity_html(act: LegacyWorksheetActivity) -> str:
    """Renders a single worksheet activity with active learning container and withholding enforcement."""
    bg_color, text_color, border_color = INQUIRY_BADGE_COLORS.get(
        act.activity_type.upper(), ("#f8fafc", "#334155", "#cbd5e1")
    )

    title_esc = html.escape(act.title)
    prompt_esc = html.escape(act.prompt_text).replace("\n", "<br/>")

    workspace_html = ""
    if act.requires_student_workspace:
        workspace_html = """
        <div class="student-workspace-box" style="margin-top: 12px; border: 2px dashed #94a3b8; border-radius: 8px; background: #f8fafc; padding: 14px; min-height: 100px;">
            <div style="font-size: 10pt; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em;">
                Ruang Kerja & Catatan Siswa
            </div>
            <div style="height: 70px;"></div>
        </div>
        """

    meta_line = f"Bantuan: {act.scaffolding_level}"
    if act.expected_reasoning_type:
        meta_line += f" | Target Penalaran: {act.expected_reasoning_type}"

    return f"""
    <div class="worksheet-activity-card card" id="{act.activity_id}" style="margin-bottom: 20px; border-left: 4px solid {text_color};">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <span class="badge" style="background: {bg_color}; color: {text_color}; border: 1px solid {border_color}; font-weight: 700;">
                {act.activity_type.upper()}
            </span>
            <span style="font-size: 10pt; color: #94a3b8; font-weight: 600;">{meta_line}</span>
        </div>
        <h4 style="margin: 0 0 8px 0; font-size: 12pt; color: #0f172a; font-weight: 700;">{title_esc}</h4>
        <div class="activity-prompt-text" style="font-size: 10.5pt; line-height: 1.5; color: #334155;">
            {prompt_esc}
        </div>
        {workspace_html}
    </div>
    """


class WorksheetExecutor(RendererExecutor):
    """Executes MasterRenderEngine for student inquiry worksheets."""

    def __init__(self, templates_dir: Optional[Path] = None):
        self.templates_dir = (
            templates_dir
            or Path(__file__).parent.parent.parent / "rendering" / "html" / "templates"
        )

    @property
    def supported_artifact_type(self) -> str:
        return "WORKSHEET"

    def execute(
        self,
        legacy_model: LegacyWorksheetDocument,
        output_dir: Path,
        output_filename: Optional[str] = None,
        activities_per_page: int = 3,
    ) -> RendererExecutionResult:
        """Renders LegacyWorksheetDocument into HTML and PDF."""
        start_time = time.time()
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        source_element_ids_rendered: List[str] = []
        errors: List[str] = []
        warnings: List[str] = []

        all_activities: List[LegacyWorksheetActivity] = []
        for sec in legacy_model.sections:
            for act in sec.activities:
                all_activities.append(act)
                source_element_ids_rendered.extend(act.source_element_ids)

        # 1. Distribute activities across pages
        pages: List[PageComposition] = []
        chunk_size = max(1, activities_per_page)
        page_num = 1

        for i in range(0, len(all_activities), chunk_size):
            chunk = all_activities[i : i + chunk_size]
            page_blocks: List[CompositionBlock] = []
            page_source_ids: List[str] = []

            for act in chunk:
                # Anti-corruption check: Ensure answer explanations are NOT leaked
                if not act.withhold_explanation:
                    warnings.append(f"Activity {act.activity_id} has withhold_explanation=False")

                source_refs = list(act.source_element_ids)
                page_source_ids.extend(source_refs)

                act_html = _render_activity_html(act)
                c_block = CompositionBlock(
                    block_id=f"cb_{act.activity_id}",
                    component_family=ComponentFamily.TEXT_BLOCK,
                    source_unit_ids=source_refs,
                    rendered_html=act_html,
                )
                page_blocks.append(c_block)

            page = PageComposition(
                page_number=page_num,
                page_type="content_page",
                composition_type="worksheet_document",
                hierarchy_level=1,
                regions={
                    RegionRole.PRIMARY: PageRegion(
                        role=RegionRole.PRIMARY,
                        blocks=page_blocks,
                    )
                },
                source_unit_ids=page_source_ids,
                metadata={"activities_count": len(chunk)},
            )
            pages.append(page)
            page_num += 1

        # 2. Assemble DocumentComposition
        slug = output_filename or "worksheet"
        composition = DocumentComposition(
            composition_id=f"comp_worksheet_{slug}",
            mode=DocumentMode.A4_PORTRAIT,
            format_id="a4_portrait",
            theme_reference="default",
            source_blueprint_id="bp_worksheet",
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
            artifact_type="WORKSHEET",
            html_path=html_p if html_p.exists() else None,
            pdf_path=pdf_p if pdf_p.exists() else None,
            total_pages=len(pages),
            source_element_ids_rendered=tuple(dict.fromkeys(source_element_ids_rendered)),
            rendered_objects_count=len(all_activities),
            execution_duration_ms=round(duration, 2),
            errors=tuple(errors + list(render_res.errors)),
            warnings=tuple(warnings),
            metadata={
                "document_title": legacy_model.title,
                "total_activities": len(all_activities),
                "total_sections": len(legacy_model.sections),
                "withholding_enforced": True,
            },
        )

    def execute_from_render_artifact(
        self,
        render_artifact: RenderArtifact,
        output_dir: Path,
        output_filename: Optional[str] = None,
        **adapter_kwargs: Any,
    ) -> RendererExecutionResult:
        """Adapts RenderArtifact to LegacyWorksheetDocument and renders."""
        adapter = WorksheetContractAdapter()
        # Default to compatibility grouping if not explicitly specified
        if "grouping_mode" not in adapter_kwargs:
            adapter_kwargs["grouping_mode"] = "compatibility"
        doc = adapter.adapt(render_artifact, **adapter_kwargs)
        return self.execute(doc, output_dir=output_dir, output_filename=output_filename)
