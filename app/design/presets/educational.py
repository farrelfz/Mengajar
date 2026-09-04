"""
KIR AI Document Intelligence — Educational Theme.
"""

from app.design.schemas import Theme, ColorRole
from app.design.theme_manager import theme_registry

educational_theme = Theme(
    name="educational",
    is_dark_mode=False,
    colors={
        ColorRole.BACKGROUND: "#FFFFFF",
        ColorRole.SURFACE: "#F8FAFC",
        ColorRole.SURFACE_SUBTLE: "#F1F5F9",
        ColorRole.SURFACE_EMPHASIS: "#E2E8F0",
        ColorRole.TEXT_PRIMARY: "#0F172A",
        ColorRole.TEXT_SECONDARY: "#334155",
        ColorRole.TEXT_MUTED: "#64748B",
        ColorRole.BORDER_SUBTLE: "#F1F5F9",
        ColorRole.BORDER_STRONG: "#CBD5E1",
        ColorRole.ACCENT_PRIMARY: "#0EA5E9",
        ColorRole.ACCENT_SECONDARY: "#10B981",
        ColorRole.ACCENT_SOFT: "#E0F2FE",
        ColorRole.SUCCESS: "#22C55E",
        ColorRole.WARNING: "#EAB308",
        ColorRole.DANGER: "#EF4444",
        ColorRole.DATA_1: "#38BDF8",
        ColorRole.DATA_2: "#34D399",
        ColorRole.DATA_3: "#FACC15",
        ColorRole.DATA_4: "#FB923C",
        ColorRole.DATA_5: "#A78BFA",
    },
    typography_fonts={
        "heading": "Outfit, sans-serif",
        "body": "Nunito, sans-serif",
        "mono": "Fira Code, monospace"
    }
)

theme_registry.register(educational_theme)
