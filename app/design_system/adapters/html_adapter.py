"""
Universal Design System — HTML / CSS Adapter.

Phase 3B.0: Deterministic CSS variable and stylesheet generation for HTML renderers.
"""

from __future__ import annotations

from typing import Optional
from app.design_system.contracts.geometry import CanvasSpec, pt_to_mm, pt_to_inch
from app.design_system.contracts.profiles import DesignProfile
from app.design_system.registry.profile_registry import ProfileRegistry
from app.design_system.registry.font_registry import FontRegistry
from app.design_system.themes.base import ThemeDefinition, get_base_theme
from app.design_system.profiles import get_standard_profile_registry


class HtmlDesignAdapter:
    """Generates scoped CSS custom properties and document stylesheets."""

    def __init__(
        self,
        profile_registry: Optional[ProfileRegistry] = None,
        font_registry: Optional[FontRegistry] = None,
    ) -> None:
        self.profile_registry = profile_registry or get_standard_profile_registry()
        self.font_registry = font_registry or FontRegistry()

    def generate_css_variables(self, theme: Optional[ThemeDefinition] = None) -> str:
        """Generates standard CSS custom properties from raw and semantic tokens."""
        th = theme or get_base_theme()
        lines = [":root {"]

        # Raw Tokens
        for raw in th.raw_tokens:
            css_var_name = "--ds-" + raw.name.replace(".", "-")
            val_str = f"{raw.value}pt" if isinstance(raw.value, (int, float)) and raw.category in ("space", "font", "radius") else str(raw.value)
            lines.append(f"  {css_var_name}: {val_str};")

        # Semantic Tokens
        for sem in th.semantic_tokens:
            css_sem_name = "--ds-" + sem.name.replace(".", "-")
            css_raw_ref = "var(--ds-" + sem.raw_token_ref.replace(".", "-") + ")"
            lines.append(f"  {css_sem_name}: {css_raw_ref};")

        lines.append("}")
        return "\n".join(lines)

    def generate_canvas_css(self, artifact_type: str) -> str:
        """Generates print and screen dimensions for the given artifact."""
        profile = self.profile_registry.get_profile_for_artifact(artifact_type)
        if not profile:
            return ""

        canvas = profile.canvas_spec
        lines = []

        if artifact_type.upper() == "PRESENTATION":
            lines.append(".document-canvas.artifact-presentation {")
            lines.append(f"  width: {canvas.width_pt}pt;")
            lines.append(f"  min-height: {canvas.height_pt}pt;")
            lines.append(f"  padding: {canvas.safe_margin_top_pt}pt {canvas.safe_margin_right_pt}pt {canvas.safe_margin_bottom_pt}pt {canvas.safe_margin_left_pt}pt;")
            lines.append("  box-sizing: border-box;")
            lines.append("  aspect-ratio: 16 / 9;")
            lines.append("}")
        else:
            width_mm = pt_to_mm(canvas.width_pt)
            height_mm = pt_to_mm(canvas.height_pt)
            lines.append(f".document-canvas.artifact-{artifact_type.lower()} {{")
            lines.append(f"  width: {width_mm:.2f}mm;")
            lines.append(f"  min-height: {height_mm:.2f}mm;")
            lines.append(f"  padding: {pt_to_mm(canvas.safe_margin_top_pt):.2f}mm {pt_to_mm(canvas.safe_margin_right_pt):.2f}mm {pt_to_mm(canvas.safe_margin_bottom_pt):.2f}mm {pt_to_mm(canvas.safe_margin_left_pt):.2f}mm;")
            lines.append("  box-sizing: border-box;")
            lines.append("}")

        return "\n".join(lines)

    def generate_stylesheet(self, artifact_type: str, theme: Optional[ThemeDefinition] = None) -> str:
        """Produces a unified CSS block combining variables, font stacks, and canvas specs."""
        vars_css = self.generate_css_variables(theme)
        canvas_css = self.generate_canvas_css(artifact_type)
        
        font_face = self.font_registry.resolve_font("Inter")[0]
        base_font_css = f"body {{ font-family: {font_face.html_family}; -webkit-print-color-adjust: exact; }}"

        return f"{vars_css}\n\n{base_font_css}\n\n{canvas_css}"
