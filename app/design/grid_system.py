"""
KIR AI Document Intelligence — Grid System and Document Modes.
"""

from app.intelligence.schemas import DocumentMode


class GridFamily:
    """Abstract Grid definition."""
    def __init__(self, name: str, columns: int, description: str):
        self.name = name
        self.columns = columns
        self.description = description


class GridRegistry:
    """Registry for available abstract grids."""
    def __init__(self):
        self._grids: dict[DocumentMode, dict[str, GridFamily]] = {
            DocumentMode.A4_PORTRAIT: {},
            DocumentMode.A4_LANDSCAPE: {},
            DocumentMode.A4_TUTORIAL: {},
            DocumentMode.PRESENTATION_16_9: {}
        }

    def register(self, mode: DocumentMode, grid: GridFamily) -> None:
        if mode not in self._grids:
            self._grids[mode] = {}
        self._grids[mode][grid.name] = grid
        
    def get_grids_for_mode(self, mode: DocumentMode) -> dict[str, GridFamily]:
        return self._grids.get(mode, self._grids.get(DocumentMode.A4_TUTORIAL, {}))

grid_registry = GridRegistry()

# A4 Grids (Portrait, Landscape, Tutorial)
for a4_mode in [DocumentMode.A4_PORTRAIT, DocumentMode.A4_LANDSCAPE, DocumentMode.A4_TUTORIAL]:
    grid_registry.register(a4_mode, GridFamily("single_column", 1, "Standard reading flow"))
    grid_registry.register(a4_mode, GridFamily("two_column", 2, "Balanced split content"))
    grid_registry.register(a4_mode, GridFamily("three_column", 3, "Dense data or parallel points"))
    grid_registry.register(a4_mode, GridFamily("main_sidebar", 3, "Main content with a 1/3 sidebar (metadata/hints)"))
    grid_registry.register(a4_mode, GridFamily("asymmetric_editorial", 4, "Magazine-style flexible columns"))

# 16:9 Presentation Grids
grid_registry.register(DocumentMode.PRESENTATION_16_9, GridFamily("hero_composition", 1, "Large centered title or key message"))
grid_registry.register(DocumentMode.PRESENTATION_16_9, GridFamily("two_column", 2, "Comparison or narrative + visual"))
grid_registry.register(DocumentMode.PRESENTATION_16_9, GridFamily("visual_dominant", 3, "1/3 text, 2/3 visual"))
grid_registry.register(DocumentMode.PRESENTATION_16_9, GridFamily("narrative_visual", 3, "2/3 text, 1/3 visual"))
grid_registry.register(DocumentMode.PRESENTATION_16_9, GridFamily("comparison_split", 2, "Strict 50/50 split"))
grid_registry.register(DocumentMode.PRESENTATION_16_9, GridFamily("timeline_horizontal", 4, "4-column sequence layout"))

def get_default_grid(mode: DocumentMode) -> str:
    if mode in (DocumentMode.A4_PORTRAIT, DocumentMode.A4_LANDSCAPE, DocumentMode.A4_TUTORIAL):
        return "single_column"
    return "hero_composition"
