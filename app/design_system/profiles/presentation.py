"""
Universal Design System — Presentation Format Profile.

Phase 3B.0: 16:9 widescreen canvas, high-legibility typography,
and cognitive load density constraints for slide decks.
"""

from __future__ import annotations

from app.design_system.contracts.profiles import DesignProfile
from app.design_system.contracts.geometry import PRESENTATION_16_9_CANVAS
from app.design_system.contracts.components import ComponentCategory


def get_presentation_profile() -> DesignProfile:
    """Constructs the canonical 16:9 Presentation Design Profile."""
    return DesignProfile(
        profile_id="presentation_16_9",
        artifact_type="PRESENTATION",
        canvas_spec=PRESENTATION_16_9_CANVAS,
        default_theme_id="base",
        min_heading_size_pt=14.0,
        min_body_size_pt=11.0,     # Matches PyMuPDF inspector threshold (11.0 pt)
        min_caption_size_pt=8.0,
        max_density_weight_per_page=6.0,
        default_font_family="Inter",
        allowed_component_categories=(
            ComponentCategory.HEADER,
            ComponentCategory.CARD,
            ComponentCategory.STAT_CALLOUT,
            ComponentCategory.PROCESS_STEP,
            ComponentCategory.COMPARISON_COLUMN,
            ComponentCategory.TIMELINE_ITEM,
            ComponentCategory.KEY_TAKEAWAY,
            ComponentCategory.TABLE,
            ComponentCategory.FOOTER,
        ),
        token_overrides={
            "typography.presentation.title": 28.0,
            "typography.presentation.subtitle": 16.0,
            "typography.presentation.card_title": 14.0,
            "typography.presentation.body": 11.5,
            "typography.presentation.stat_number": 32.0,
            "typography.presentation.caption": 8.5,
            "spacing.card_gap": 16.0,
        },
        anti_spoiling_required=False,
        citation_required=False,
        description="16:9 Widescreen slide deck profile prioritizing distance legibility and cognitive pacing",
    )
