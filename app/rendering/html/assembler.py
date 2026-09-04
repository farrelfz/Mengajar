"""
KIR AI Document Intelligence — HTML Assembler.
"""
from pathlib import Path
from app.composition.schemas import DocumentComposition
from app.intelligence.schemas import DocumentMode
from app.rendering.schemas import AssetMetadata
from app.rendering.html.template_engine import JinjaTemplateEngine


from app.formats import resolve_format, get_format


class HTMLAssembler:
    def __init__(self, templates_dir: Path):
        self.engine = JinjaTemplateEngine(templates_dir)
        
    def assemble(
        self, 
        composition: DocumentComposition, 
        assets: list[AssetMetadata], 
        output_dir: Path,
        filename: str = "document.html"
    ) -> Path:
        # Determine CSS page size and class from authoritative format contract
        resolved_fmt = resolve_format(
            explicit_format=getattr(composition, "format_id", None) or composition.metadata.get("format_id"),
            fallback=get_format(composition.mode),
        )
        page_size_css = resolved_fmt.css_page_size
        page_class = resolved_fmt.page_class

        html_content = self.engine.render("document.html", {
            "composition": composition,
            "assets": assets,
            "page_size_css": page_size_css,
            "page_class": page_class,
        })
        
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / filename
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        # Also maintain document.html for backward compatibility
        if filename != "document.html":
            fallback_path = output_dir / "document.html"
            with open(fallback_path, "w", encoding="utf-8") as f:
                f.write(html_content)
            
        return output_path
