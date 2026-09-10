"""
Universal Document Intelligence System V5 — Quality Signal Adapters Package.

Phase 3A.1: Ingest adapters for all legacy and specialized quality signal providers.
"""

from app.quality.adapters.base import BaseSignalAdapter
from app.quality.adapters.calibration import CalibrationSignalAdapter
from app.quality.adapters.fidelity import FidelitySignalAdapter
from app.quality.adapters.legacy_document import LegacyDocumentQualitySignalAdapter
from app.quality.adapters.presentation import PresentationQualitySignalAdapter
from app.quality.adapters.rendered import RenderedQualitySignalAdapter

__all__ = [
    "BaseSignalAdapter",
    "CalibrationSignalAdapter",
    "FidelitySignalAdapter",
    "LegacyDocumentQualitySignalAdapter",
    "PresentationQualitySignalAdapter",
    "RenderedQualitySignalAdapter",
]
