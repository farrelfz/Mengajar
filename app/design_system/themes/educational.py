"""
Universal Design System — Educational Theme.

Phase 3B.0: Theme tailored for instructional artifacts, student engagement,
and classroom readability.
"""

from __future__ import annotations

from app.design_system.contracts.tokens import RawToken, SemanticToken
from app.design_system.themes.base import ThemeDefinition, get_base_theme


def get_educational_theme() -> ThemeDefinition:
    """Constructs the pedagogical theme for Handouts and Worksheets."""
    base = get_base_theme()

    educational_raw = [
        RawToken(name="color.indigo.600", value="#4f46e5", category="color"),
        RawToken(name="color.teal.600", value="#0d9488", category="color"),
        RawToken(name="color.amber.500", value="#f59e0b", category="color"),
        RawToken(name="color.emerald.50", value="#ecfdf5", category="color"),
    ]

    educational_semantics = [
        SemanticToken(name="color.accent.primary", raw_token_ref="color.indigo.600", role="Educational Primary Accent"),
        SemanticToken(name="color.accent.secondary", raw_token_ref="color.teal.600", role="Educational Secondary Accent"),
        SemanticToken(name="color.highlight", raw_token_ref="color.amber.500", role="Didactic Focus Callout"),
    ]

    # Combine base raw + educational raw
    combined_raw = {t.name: t for t in base.raw_tokens}
    for t in educational_raw:
        combined_raw[t.name] = t

    # Combine base semantics + educational semantics
    combined_sem = {t.name: t for t in base.semantic_tokens}
    for t in educational_semantics:
        combined_sem[t.name] = t

    return ThemeDefinition(
        theme_id="educational",
        name="Educational Theme",
        description="High-engagement, classroom-optimized color and typographic system",
        raw_tokens=list(combined_raw.values()),
        semantic_tokens=list(combined_sem.values()),
    )
