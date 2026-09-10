"""
Universal Design System — Scientific Document Format Profile.

Phase 3B.0: Formal academic paper profile following Indonesian KTI guidelines
(Bab I–V, mandatory evidence citation, compact typography).
"""

from __future__ import annotations

from app.design_system.contracts.profiles import DesignProfile
from app.design_system.contracts.geometry import A4_PORTRAIT_CANVAS
from app.design_system.contracts.components import ComponentCategory


def get_scientific_document_profile() -> DesignProfile:
    """Constructs the canonical A4 Scientific Document (KTI) Design Profile."""
    return DesignProfile(
        profile_id="scientific_kti_a4",
        artifact_type="SCIENTIFIC_DOCUMENT",
        canvas_spec=A4_PORTRAIT_CANVAS,
        default_theme_id="scientific",
        min_heading_size_pt=12.0,
        min_body_size_pt=8.0,      # Matches PyMuPDF inspector threshold (8.0 pt)
        min_caption_size_pt=6.5,
        max_density_weight_per_page=14.0,  # Academic compact density
        default_font_family="Merriweather", # Formal academic serif
        allowed_component_categories=(
            ComponentCategory.HEADER,
            ComponentCategory.EVIDENCE_CARD,  # Permitted on scientific docs
            ComponentCategory.TABLE,
            ComponentCategory.FORMULA_BLOCK,
            ComponentCategory.FOOTER,
        ),
        token_overrides={
            "typography.scientific.bab_title": 14.0,
            "typography.scientific.sub_bab": 11.0,
            "typography.scientific.body": 9.0,
            "typography.scientific.claim": 9.0,
            "typography.scientific.citation": 7.5,
            "typography.scientific.footnote": 7.0,
            "spacing.paragraph_indent": 18.0,
        },
        anti_spoiling_required=False,
        citation_required=True,       # Strict scientific evidence requirement
        description="Formal Indonesian KTI academic profile with citation enforcement and compact serif typesetting",
    )
