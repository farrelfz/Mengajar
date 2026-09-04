"""
KIR AI Document Intelligence — Canonical Format Presets.
"""
from __future__ import annotations

from app.formats.contracts import ArtifactFormat
from app.intelligence.schemas import DocumentMode

# 1. A4 Portrait (210mm x 297mm -> 595.28 pt x 841.89 pt)
A4_PORTRAIT = ArtifactFormat(
    id="a4_portrait",
    display_name="A4 Portrait",
    width_mm=210.0,
    height_mm=297.0,
    orientation="portrait",
    category="document",
    paginated=True,
    css_page_size="210mm 297mm",
    page_class="page-a4-portrait",
    playwright_format="A4",
    playwright_landscape=False,
    legacy_document_mode=DocumentMode.A4_PORTRAIT,
)

# 2. A4 Landscape (297mm x 210mm -> 841.89 pt x 595.28 pt)
A4_LANDSCAPE = ArtifactFormat(
    id="a4_landscape",
    display_name="A4 Landscape",
    width_mm=297.0,
    height_mm=210.0,
    orientation="landscape",
    category="document",
    paginated=True,
    css_page_size="297mm 210mm",
    page_class="page-a4-landscape",
    playwright_format="A4",
    playwright_landscape=True,
    legacy_document_mode=DocumentMode.A4_LANDSCAPE,
)

# 3. Presentation 16:9 (13.333in x 7.5in -> 338.67mm x 190.5mm -> 960 pt x 540 pt)
PRESENTATION_16_9 = ArtifactFormat(
    id="presentation_16_9",
    display_name="Presentation 16:9",
    width_mm=338.667,
    height_mm=190.5,
    orientation="landscape",
    category="presentation",
    paginated=True,
    css_page_size="13.333in 7.5in",
    page_class="page-presentation",
    playwright_format="16:9",
    playwright_landscape=False,
    playwright_width="13.333in",
    playwright_height="7.5in",
    legacy_document_mode=DocumentMode.PRESENTATION_16_9,
)

CANONICAL_PRESETS: dict[str, ArtifactFormat] = {
    A4_PORTRAIT.id: A4_PORTRAIT,
    A4_LANDSCAPE.id: A4_LANDSCAPE,
    PRESENTATION_16_9.id: PRESENTATION_16_9,
}
