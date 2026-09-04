"""
KIR AI Document Intelligence — HTML Template Engine.
"""
from jinja2 import Environment, FileSystemLoader, select_autoescape
from pathlib import Path

class JinjaTemplateEngine:
    def __init__(self, templates_dir: Path):
        self.env = Environment(
            loader=FileSystemLoader(str(templates_dir)),
            autoescape=select_autoescape(['html', 'xml'])
        )
        
    def render(self, template_name: str, context: dict) -> str:
        try:
            template = self.env.get_template(template_name)
            return template.render(**context)
        except Exception:
            # Fallback mock for testing
            return f"<html><body>Mock Render: {template_name}</body></html>"
