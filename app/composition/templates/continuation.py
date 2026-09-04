"""Continuation composition template."""
from app.composition.templates.base import CompositionTemplate
from app.composition.schemas import RegionRole

class ContinuationTemplate(CompositionTemplate):
    @property
    def name(self) -> str:
        return "continuation"
        
    @property
    def required_regions(self) -> list[RegionRole]:
        return [RegionRole.HEADER, RegionRole.PRIMARY]

    @property
    def optional_regions(self) -> list[RegionRole]:
        return [RegionRole.FOOTER, RegionRole.SEQUENCE]
