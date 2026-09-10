"""
Universal Knowledge Core — Render Execution Integration.

Phase 2B Controlled Renderer Execution & Artifact Fidelity:
Provides controlled execution wrappers around existing legacy renderers
(SlideGenerator, MasterRenderEngine, HTMLAssembler, Playwright) to validate
uncompromised visual rendering across all four artifact types.
"""

from app.integration.render_execution.execution_contract import RendererExecutor
from app.integration.render_execution.handout_executor import HandoutExecutor
from app.integration.render_execution.presentation_executor import PresentationExecutor
from app.integration.render_execution.renderer_result import RendererExecutionResult
from app.integration.render_execution.scientific_document_executor import (
    ScientificDocumentExecutor,
)
from app.integration.render_execution.worksheet_executor import WorksheetExecutor

__all__ = [
    "RendererExecutor",
    "RendererExecutionResult",
    "PresentationExecutor",
    "HandoutExecutor",
    "WorksheetExecutor",
    "ScientificDocumentExecutor",
]
