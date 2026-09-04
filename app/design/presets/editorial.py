"""
KIR AI Document Intelligence — Editorial Hybrid Theme (DEFAULT).
"""

from app.design.schemas import Theme, ColorRole
from app.design.theme_manager import theme_registry

editorial_hybrid_theme = Theme(
    name="editorial_hybrid",
    is_dark_mode=False,
    colors={
        ColorRole.BACKGROUND: "#FDFDFD",
        ColorRole.SURFACE: "#FFFFFF",
        ColorRole.SURFACE_SUBTLE: "#F5F7FA",
        ColorRole.SURFACE_EMPHASIS: "#E4E7EB",
        ColorRole.TEXT_PRIMARY: "#1A202C",
        ColorRole.TEXT_SECONDARY: "#4A5568",
        ColorRole.TEXT_MUTED: "#718096",
        ColorRole.BORDER_SUBTLE: "#EDF2F7",
        ColorRole.BORDER_STRONG: "#E2E8F0",
        ColorRole.ACCENT_PRIMARY: "#2B6CB0",
        ColorRole.ACCENT_SECONDARY: "#319795",
        ColorRole.ACCENT_SOFT: "#EBF8FF",
        ColorRole.SUCCESS: "#38A169",
        ColorRole.WARNING: "#D69E2E",
        ColorRole.DANGER: "#E53E3E",
        ColorRole.DATA_1: "#4299E1",
        ColorRole.DATA_2: "#48BB78",
        ColorRole.DATA_3: "#ECC94B",
        ColorRole.DATA_4: "#ED8936",
        ColorRole.DATA_5: "#9F7AEA",
    },
    typography_fonts={
        "heading": "Inter, sans-serif",
        "body": "Merriweather, serif",
        "mono": "JetBrains Mono, monospace"
    }
)

theme_registry.register(editorial_hybrid_theme)
