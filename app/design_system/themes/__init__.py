"""Universal Design System Themes Export."""

from app.design_system.themes.base import ThemeDefinition, get_base_theme
from app.design_system.themes.educational import get_educational_theme
from app.design_system.themes.scientific import get_scientific_theme
from app.design_system.themes.neutral import get_neutral_theme

__all__ = [
    "ThemeDefinition",
    "get_base_theme",
    "get_educational_theme",
    "get_scientific_theme",
    "get_neutral_theme",
]
