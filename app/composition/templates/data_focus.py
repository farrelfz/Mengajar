"""Data focus composition template."""
from app.composition.templates.base import CompositionTemplate
from app.composition.schemas import RegionRole

class DataFocusTemplate(CompositionTemplate):
    @property
    def name(self) -> str:
        return "data_focus"
        
    @property
    def required_regions(self) -> list[RegionRole]:
        return [RegionRole.HEADER, RegionRole.PRIMARY, RegionRole.VISUAL]

    @property
    def optional_regions(self) -> list[RegionRole]:
        return [RegionRole.SUPPORTING, RegionRole.FOOTER]
