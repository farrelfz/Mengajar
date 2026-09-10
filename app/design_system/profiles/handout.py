"""
Universal Design System — Handout Format Profile.

Phase 3B.0: A4 continuous educational reading profile with monotonic typographic hierarchy.
"""

from __future__ import annotations

from app.design_system.contracts.profiles import DesignProfile
from app.design_system.contracts.geometry import A4_PORTRAIT_CANVAS
from app.design_system.contracts.components import ComponentCategory


def get_handout_profile() -> DesignProfile:
    """Constructs the canonical A4 Handout Design Profile."""
    return DesignProfile(
        profile_id="handout_a4",
        artifact_type="HANDOUT",
        canvas_spec=A4_PORTRAIT_CANVAS,
        default_theme_id="educational",
        min_heading_size_pt=12.0,
        min_body_size_pt=8.5,      # Matches PyMuPDF inspector threshold (8.5 pt)
        min_caption_size_pt=7.0,
        max_density_weight_per_page=12.0,
        default_font_family="Inter",
        allowed_component_categories=(
            ComponentCategory.HEADER,
            ComponentCategory.CALLOUT_BOX,
            ComponentCategory.EVIDENCE_CARD,
            ComponentCategory.PROCESS_STEP,
            ComponentCategory.TIMELINE_ITEM,
            ComponentCategory.KEY_TAKEAWAY,
            ComponentCategory.TABLE,
            ComponentCategory.FOOTER,
        ),
        token_overrides={
            "typography.handout.h1": 20.0,
            "typography.handout.h2": 15.0,
            "typography.handout.h3": 12.0,
            "typography.handout.body": 9.5,
            "typography.handout.caption": 7.5,
            "spacing.paragraph_gap": 10.0,
        },
        anti_spoiling_required=False,
        citation_required=False,
        description="A4 continuous student reading material with structured monotonic hierarchy",
    )
