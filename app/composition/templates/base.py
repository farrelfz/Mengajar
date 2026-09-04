"""
KIR AI Document Intelligence — Composition Templates.
"""
from abc import ABC, abstractmethod
from app.composition.schemas import RegionRole


class CompositionTemplate(ABC):
    """Abstract base class for all deterministic page compositions."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        pass
        
    @property
    @abstractmethod
    def required_regions(self) -> list[RegionRole]:
        pass

    @property
    @abstractmethod
    def optional_regions(self) -> list[RegionRole]:
        pass
