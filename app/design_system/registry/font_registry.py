"""
Universal Design System — Font Registry.

Phase 3B.0: Cross-renderer font face registration, alias resolution,
and deterministic fallback (INV-DESIGN-001, INV-DESIGN-004).
"""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple
from app.design_system.contracts.typography import FontFace


class FontRegistry:
    """Central authority for cross-renderer font definitions and fallbacks."""

    def __init__(self) -> None:
        self._faces: Dict[Tuple[str, int, str], FontFace] = {}
        self._aliases: Dict[str, str] = {}
        self._initialize_defaults()

    def _initialize_defaults(self) -> None:
        """Pre-populates canonical standard cross-renderer fonts."""
        default_faces = [
            # Inter / Standard Sans-Serif
            FontFace(
                family="Inter",
                weight=400,
                style="normal",
                html_family="'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif",
                reportlab_name="Helvetica",
            ),
            FontFace(
                family="Inter",
                weight=700,
                style="normal",
                html_family="'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif",
                reportlab_name="Helvetica-Bold",
            ),
            FontFace(
                family="Inter",
                weight=400,
                style="italic",
                html_family="'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif",
                reportlab_name="Helvetica-Oblique",
            ),
            FontFace(
                family="Inter",
                weight=700,
                style="italic",
                html_family="'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif",
                reportlab_name="Helvetica-BoldOblique",
            ),

            # Merriweather / Formal Serif (Scientific Document / KTI)
            FontFace(
                family="Merriweather",
                weight=400,
                style="normal",
                html_family="'Merriweather', 'Times New Roman', Times, Georgia, serif",
                reportlab_name="Times-Roman",
            ),
            FontFace(
                family="Merriweather",
                weight=700,
                style="normal",
                html_family="'Merriweather', 'Times New Roman', Times, Georgia, serif",
                reportlab_name="Times-Bold",
            ),
            FontFace(
                family="Merriweather",
                weight=400,
                style="italic",
                html_family="'Merriweather', 'Times New Roman', Times, Georgia, serif",
                reportlab_name="Times-Italic",
            ),
            FontFace(
                family="Merriweather",
                weight=700,
                style="italic",
                html_family="'Merriweather', 'Times New Roman', Times, Georgia, serif",
                reportlab_name="Times-BoldItalic",
            ),

            # JetBrains Mono / Monospace (Code, Formulas, Data)
            FontFace(
                family="JetBrains Mono",
                weight=400,
                style="normal",
                html_family="'JetBrains Mono', 'Courier New', Courier, monospace",
                reportlab_name="Courier",
            ),
            FontFace(
                family="JetBrains Mono",
                weight=700,
                style="normal",
                html_family="'JetBrains Mono', 'Courier New', Courier, monospace",
                reportlab_name="Courier-Bold",
            ),
        ]

        for face in default_faces:
            self.register_face(face)

        # Standard Aliases
        self.register_alias("sans", "Inter")
        self.register_alias("sans-serif", "Inter")
        self.register_alias("serif", "Merriweather")
        self.register_alias("times", "Merriweather")
        self.register_alias("mono", "JetBrains Mono")
        self.register_alias("monospace", "JetBrains Mono")

    def register_face(self, face: FontFace) -> None:
        """Registers a font face with specific family, weight, and style."""
        key = (face.family.lower(), face.weight, face.style.lower())
        self._faces[key] = face

    def register_alias(self, alias: str, canonical_family: str) -> None:
        """Registers a family alias."""
        self._aliases[alias.lower()] = canonical_family

    def resolve_family_name(self, family: str) -> str:
        """Resolves an alias to canonical family name."""
        return self._aliases.get(family.lower(), family)

    def get_face(
        self, family: str, weight: int = 400, style: str = "normal"
    ) -> Optional[FontFace]:
        """Retrieves exact font face if registered."""
        canon = self.resolve_family_name(family)
        return self._faces.get((canon.lower(), weight, style.lower()))

    def resolve_font(
        self, family: str, weight: int = 400, style: str = "normal"
    ) -> Tuple[FontFace, bool]:
        """
        Deterministically resolves a font face.
        If the exact match is not found, falls back gracefully to:
        1. Same family with weight=400, style='normal'
        2. Default 'Inter' with specified weight/style
        3. Default 'Inter' normal
        Returns (resolved_face, fallback_applied).
        """
        exact = self.get_face(family, weight, style)
        if exact:
            return exact, False

        # Fallback 1: Same family normal weight/style
        canon = self.resolve_family_name(family)
        fallback_normal = self._faces.get((canon.lower(), 400, "normal"))
        if fallback_normal:
            return fallback_normal, True

        # Fallback 2: Inter with requested weight/style
        fallback_inter = self._faces.get(("inter", weight, style.lower()))
        if fallback_inter:
            return fallback_inter, True

        # Fallback 3: Inter normal
        base_fallback = self._faces[("inter", 400, "normal")]
        return base_fallback, True

    def list_faces(self) -> List[FontFace]:
        """Returns all registered font faces."""
        return list(self._faces.values())
