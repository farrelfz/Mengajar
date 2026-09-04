"""
KIR AI Document Intelligence — Hybrid Rendering Engine.
"""
from pathlib import Path
import shutil
import asyncio
from app.composition.schemas import DocumentComposition
from app.core.naming import sanitize_filename
from app.formats import resolve_format, get_format
from app.intelligence.schemas import DocumentMode
from app.rendering.schemas import RenderResult, RenderTarget
from app.rendering.planner import HybridRenderPlanner
from app.rendering.assets.manager import AssetManager
from app.rendering.html.assembler import HTMLAssembler
from app.rendering.reportlab.renderer import ReportLabRenderer
from app.rendering.visuals.matplotlib_renderer import MatplotlibRenderer
from app.rendering.playwright.pdf_exporter import PlaywrightRenderer
from app.rendering.validation.pdf_validator import PDFValidator


class MasterRenderEngine:
    def __init__(self, templates_dir: Path, output_dir: Path):
        self.output_dir = output_dir
        self.asset_manager = AssetManager(output_dir / "assets")
        self.planner = HybridRenderPlanner()
        self.html_assembler = HTMLAssembler(templates_dir)
        self.reportlab_renderer = ReportLabRenderer(self.asset_manager)
        self.visual_renderer = MatplotlibRenderer(self.asset_manager)
        self.playwright = PlaywrightRenderer()
        self.validator = PDFValidator()
        
    def render(self, composition: DocumentComposition, output_filename: str | None = None) -> RenderResult:
        result = RenderResult(success=False)
        
        # 1. Determine contextual filename slug
        slug = sanitize_filename(
            output_filename 
            or composition.metadata.get("title") 
            or composition.source_blueprint_id 
            or "document"
        )
        
        # 2. Create plan
        plan = self.planner.create_plan(composition)
        
        # 3. Render assets
        for item in plan.items:
            if item.target == RenderTarget.REPORTLAB:
                self.reportlab_renderer.render_component(item.source_block_id, item.component_family, {})
            elif item.target == RenderTarget.PYTHON_VISUAL:
                self.visual_renderer.render_component(item.source_block_id, item.component_family, {})
                
        # 4. Assemble HTML
        html_path = self.html_assembler.assemble(
            composition, 
            self.asset_manager.registry.get_all(), 
            self.output_dir,
            filename=f"{slug}.html"
        )
        
        # 5. Authoritative Physical Format Resolution
        resolved_fmt = resolve_format(
            explicit_format=getattr(composition, "format_id", None) or composition.metadata.get("format_id"),
            fallback=get_format(composition.mode),
        )
        is_landscape = resolved_fmt.playwright_landscape
        fmt = resolved_fmt.playwright_format or "A4"
        width = resolved_fmt.playwright_width
        height = resolved_fmt.playwright_height
        
        pdf_path = self.output_dir / f"{slug}.pdf"
        
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                pool.submit(
                    asyncio.run, 
                    self.playwright.export_pdf(
                        html_path, 
                        pdf_path, 
                        is_landscape=is_landscape, 
                        format=fmt,
                        width=width,
                        height=height,
                    )
                ).result()
        else:
            asyncio.run(
                self.playwright.export_pdf(
                    html_path, 
                    pdf_path, 
                    is_landscape=is_landscape, 
                    format=fmt,
                    width=width,
                    height=height,
                )
            )
        
        # Maintain final.pdf for backwards compatibility
        if pdf_path.name != "final.pdf":
            try:
                shutil.copyfile(pdf_path, self.output_dir / "final.pdf")
            except Exception:
                pass

        # 6. Validate with format awareness
        validation_result = self.validator.validate(pdf_path, expected_format=resolved_fmt)
        if not validation_result.get("valid", False) or validation_result.get("errors"):
            result.errors = validation_result.get("errors", ["Unknown PDF validation error"])
            return result
            
        result.success = True
        result.pdf_path = str(pdf_path)
        result.assets_generated = len(self.asset_manager.registry.get_all())
        result.pages = validation_result.get("page_count", len(composition.pages))
        return result
