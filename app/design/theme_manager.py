"""
KIR AI Document Intelligence — Theme Manager.

Manages theme registration and provides theme lookups.
"""

from app.design.schemas import Theme


class ThemeRegistry:
    """Central registry for all available design themes."""

    def __init__(self):
        self._themes: dict[str, Theme] = {}

    def register(self, theme: Theme) -> None:
        """Registers a new theme."""
        self._themes[theme.name.lower()] = theme

    def get_theme(self, name: str) -> Theme:
        """Retrieves a theme by name. Raises KeyError if not found."""
        try:
            return self._themes[name.lower()]
        except KeyError:
            raise KeyError(f"Theme '{name}' not found. Available: {list(self._themes.keys())}")
    
    def get_default_theme(self) -> Theme:
        """Returns the default editorial theme."""
        if "editorial_hybrid" in self._themes:
            return self._themes["editorial_hybrid"]
        if self._themes:
            return next(iter(self._themes.values()))
        raise RuntimeError("No themes registered.")

# Global registry instance
theme_registry = ThemeRegistry()

# Import presets to auto-register default themes
import app.design.presets.editorial  # noqa: F401
import app.design.presets.educational  # noqa: F401
import app.design.presets.presentation  # noqa: F401

