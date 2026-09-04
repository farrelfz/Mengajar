"""
KIR AI Document Intelligence — Presentation Theme.
"""

from app.design.schemas import Theme, ColorRole
from app.design.theme_manager import theme_registry

presentation_theme = Theme(
    name="presentation",
    is_dark_mode=True,
    colors={
        ColorRole.BACKGROUND: "#111827",
        ColorRole.SURFACE: "#1F2937",
        ColorRole.SURFACE_SUBTLE: "#374151",
        ColorRole.SURFACE_EMPHASIS: "#4B5563",
        ColorRole.TEXT_PRIMARY: "#F9FAFB",
        ColorRole.TEXT_SECONDARY: "#D1D5DB",
        ColorRole.TEXT_MUTED: "#9CA3AF",
        ColorRole.BORDER_SUBTLE: "#374151",
        ColorRole.BORDER_STRONG: "#6B7280",
        ColorRole.ACCENT_PRIMARY: "#3B82F6",
        ColorRole.ACCENT_SECONDARY: "#8B5CF6",
        ColorRole.ACCENT_SOFT: "#1E3A8A",
        ColorRole.SUCCESS: "#10B981",
        ColorRole.WARNING: "#F59E0B",
        ColorRole.DANGER: "#EF4444",
        ColorRole.DATA_1: "#60A5FA",
        ColorRole.DATA_2: "#34D399",
        ColorRole.DATA_3: "#FBBF24",
        ColorRole.DATA_4: "#F87171",
        ColorRole.DATA_5: "#A78BFA",
    },
    typography_fonts={
        "heading": "Montserrat, sans-serif",
        "body": "Open Sans, sans-serif",
        "mono": "Fira Code, monospace"
    }
)

theme_registry.register(presentation_theme)
