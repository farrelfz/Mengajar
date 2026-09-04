"""A4 Portrait format constraints."""
from app.formats.schemas import FormatConfig
from app.intelligence.schemas import DocumentMode

a4_portrait_config = FormatConfig(
    mode=DocumentMode.A4_PORTRAIT,
    max_words_per_page=550,
    preferred_regions=["header", "primary", "secondary", "footer"],
    supports_multi_column=True,
    aggressively_splits_content=False,
)
