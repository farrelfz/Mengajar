"""Editorial composition template."""
from app.composition.templates.base import CompositionTemplate
from app.composition.schemas import RegionRole

class EditorialTemplate(CompositionTemplate):
    @property
    def name(self) -> str:
        return "editorial"
        
    @property
    def required_regions(self) -> list[RegionRole]:
        return [RegionRole.HEADER, RegionRole.PRIMARY]

    @property
    def optional_regions(self) -> list[RegionRole]:
        return [RegionRole.SECONDARY, RegionRole.SUPPORTING, RegionRole.VISUAL, RegionRole.FOOTER]
