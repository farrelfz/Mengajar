"""
Universal Design System — Scientific Theme.

Phase 3B.0: Formal academic theme tailored for Indonesian Karya Tulis Ilmiah (KTI)
and rigorous scientific documentation.
"""

from __future__ import annotations

from app.design_system.contracts.tokens import RawToken, SemanticToken
from app.design_system.themes.base import ThemeDefinition, get_base_theme


def get_scientific_theme() -> ThemeDefinition:
    """Constructs the formal scientific theme for academic documents."""
    base = get_base_theme()

    scientific_raw = [
        RawToken(name="color.navy.800", value="#1e3a8a", category="color"),
        RawToken(name="color.navy.900", value="#0f172a", category="color"),
        RawToken(name="color.formal.gray", value="#475569", category="color"),
        RawToken(name="color.citation.bg", value="#f8fafc", category="color"),
    ]

    scientific_semantics = [
        SemanticToken(name="color.accent.primary", raw_token_ref="color.navy.800", role="Academic Primary Heading"),
        SemanticToken(name="color.accent.secondary", raw_token_ref="color.formal.gray", role="Academic Subtitle"),
        SemanticToken(name="color.citation.border", raw_token_ref="color.slate.300", role="Formal Citation Border"),
    ]

    combined_raw = {t.name: t for t in base.raw_tokens}
    for t in scientific_raw:
        combined_raw[t.name] = t

    combined_sem = {t.name: t for t in base.semantic_tokens}
    for t in scientific_semantics:
        combined_sem[t.name] = t

    return ThemeDefinition(
        theme_id="scientific",
        name="Scientific Theme",
        description="Rigorous, formal academic theme adhering to Indonesian KTI publishing conventions",
        raw_tokens=list(combined_raw.values()),
        semantic_tokens=list(combined_sem.values()),
    )
