"""
Universal Design System — Worksheet Format Profile.

Phase 3B.0: Inquiry-driven activity sheet with student response spaces
and strict anti-spoiling constraints.
"""

from __future__ import annotations

from app.design_system.contracts.profiles import DesignProfile
from app.design_system.contracts.geometry import A4_PORTRAIT_CANVAS
from app.design_system.contracts.components import ComponentCategory


def get_worksheet_profile() -> DesignProfile:
    """Constructs the canonical A4 Worksheet Design Profile."""
    return DesignProfile(
        profile_id="worksheet_a4",
        artifact_type="WORKSHEET",
        canvas_spec=A4_PORTRAIT_CANVAS,
        default_theme_id="educational",
        min_heading_size_pt=12.0,
        min_body_size_pt=9.0,      # Matches PyMuPDF inspector threshold (9.0 pt)
        min_caption_size_pt=7.0,
        max_density_weight_per_page=8.0,  # Lower density to ensure sufficient response workspace
        default_font_family="Inter",
        allowed_component_categories=(
            ComponentCategory.HEADER,
            ComponentCategory.RESPONSE_WORKSPACE,  # Permitted on worksheets
            ComponentCategory.CALLOUT_BOX,
            ComponentCategory.CARD,
            ComponentCategory.PROCESS_STEP,
            ComponentCategory.TABLE,
            ComponentCategory.FOOTER,
        ),
        token_overrides={
            "typography.worksheet.title": 18.0,
            "typography.worksheet.section": 13.0,
            "typography.worksheet.prompt": 10.0,
            "typography.worksheet.guidance": 8.5,
            "spacing.workspace_min_height": 60.0,
        },
        anti_spoiling_required=True,   # Strict anti-spoiling invariant
        citation_required=False,
        description="Inquiry-based student activity worksheet with guided workspaces and anti-spoiling guards",
    )
