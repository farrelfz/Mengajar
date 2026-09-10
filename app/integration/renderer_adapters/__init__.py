"""
Universal Knowledge Core — Renderer Contract Adapters Module.

Phase 2A Controlled Renderer Adapter Integration:
Translates renderer-neutral RenderArtifact contracts into legacy intermediate models
without modifying existing renderers.
"""

from app.integration.renderer_adapters.base import RendererContractAdapter
from app.integration.renderer_adapters.contracts import (
    DocumentContent,
    DocumentContentSection,
    DocumentOutline,
    DocumentOutlineItem,
    LegacyKtiBabSection,
    LegacyPresentationDeck,
    LegacyScientificDocument,
    LegacyScientificEvidence,
    LegacyScientificSubsection,
    LegacyWorksheetActivity,
    LegacyWorksheetDocument,
    LegacyWorksheetSection,
    SlideBlueprint,
)
from app.integration.renderer_adapters.presentation_adapter import PresentationContractAdapter
from app.integration.renderer_adapters.handout_adapter import HandoutContractAdapter
from app.integration.renderer_adapters.worksheet_adapter import WorksheetContractAdapter
from app.integration.renderer_adapters.scientific_document_adapter import ScientificDocumentContractAdapter
from app.integration.renderer_adapters.adapter_validator import (
    AdapterTraceabilityValidator,
    AdapterValidationReport,
    FragmentationRiskAnalyzer,
    FragmentationRiskReport,
)

__all__ = [
    "RendererContractAdapter",
    "PresentationContractAdapter",
    "HandoutContractAdapter",
    "WorksheetContractAdapter",
    "ScientificDocumentContractAdapter",
    "AdapterTraceabilityValidator",
    "AdapterValidationReport",
    "FragmentationRiskAnalyzer",
    "FragmentationRiskReport",
    "SlideBlueprint",
    "LegacyPresentationDeck",
    "DocumentOutlineItem",
    "DocumentOutline",
    "DocumentContentSection",
    "DocumentContent",
    "LegacyWorksheetActivity",
    "LegacyWorksheetSection",
    "LegacyWorksheetDocument",
    "LegacyScientificEvidence",
    "LegacyScientificSubsection",
    "LegacyKtiBabSection",
    "LegacyScientificDocument",
]
