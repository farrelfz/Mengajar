"""
KIR AI Document Intelligence — Design Tokens.

Provides centralized mappings of semantic scales to abstract sizes,
allowing for resolution at render time.
"""

from app.design.schemas import TypographyScale, SpacingScale, RadiusScale, BorderScale, ElevationScale


def get_typography_scale_value(scale: TypographyScale) -> str:
    """Returns an abstract relative size token for typography."""
    mapping = {
        TypographyScale.DISPLAY: "var(--text-display)",
        TypographyScale.HERO: "var(--text-hero)",
        TypographyScale.HEADLINE: "var(--text-headline)",
        TypographyScale.TITLE: "var(--text-title)",
        TypographyScale.SECTION: "var(--text-section)",
        TypographyScale.SUBSECTION: "var(--text-subsection)",
        TypographyScale.BODY_LARGE: "var(--text-body-large)",
        TypographyScale.BODY: "var(--text-body)",
        TypographyScale.BODY_SMALL: "var(--text-body-small)",
        TypographyScale.SUPPORTING: "var(--text-supporting)",
        TypographyScale.CAPTION: "var(--text-caption)",
        TypographyScale.LABEL: "var(--text-label)",
        TypographyScale.MICRO: "var(--text-micro)",
    }
    return mapping.get(scale, "var(--text-body)")


def get_spacing_scale_value(scale: SpacingScale) -> str:
    """Returns an abstract relative spacing token."""
    mapping = {
        SpacingScale.NONE: "0",
        SpacingScale.XXS: "var(--spacing-xxs)",
        SpacingScale.XS: "var(--spacing-xs)",
        SpacingScale.SM: "var(--spacing-sm)",
        SpacingScale.MD: "var(--spacing-md)",
        SpacingScale.LG: "var(--spacing-lg)",
        SpacingScale.XL: "var(--spacing-xl)",
        SpacingScale.XXL: "var(--spacing-2xl)",
        SpacingScale.XXXL: "var(--spacing-3xl)",
        SpacingScale.XXXXL: "var(--spacing-4xl)",
    }
    return mapping.get(scale, "var(--spacing-md)")
