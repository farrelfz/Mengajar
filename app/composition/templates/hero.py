"""Hero composition template."""
from app.composition.templates.base import CompositionTemplate
from app.composition.schemas import RegionRole

class HeroTemplate(CompositionTemplate):
    @property
    def name(self) -> str:
        return "hero"
        
    @property
    def required_regions(self) -> list[RegionRole]:
        return [RegionRole.PRIMARY]

    @property
    def optional_regions(self) -> list[RegionRole]:
        return [RegionRole.HEADER, RegionRole.FOOTER, RegionRole.SUPPORTING]
