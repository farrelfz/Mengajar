"""
Universal Document Intelligence System V5 — Adversarial Fixture Provider.

Phase 2C: Helper functions to obtain clean baseline models for all four artifact types
and apply deterministic adversarial mutations for calibration and unit testing.
"""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any, Dict, Tuple

from app.intelligence.pipeline import KnowledgeCompiler, OfflineMockResolutionProvider
from app.intelligence.schemas import UniversalKnowledgeManifest
from app.intelligence.transformation import (
    ArtifactType,
    HandoutTransformer,
    KnowledgeSelectionEngine,
    PresentationTransformer,
    ScientificDocumentTransformer,
    WorksheetTransformer,
    get_default_intent,
)
from app.integration.artifact_bridge import (
    HandoutBlueprintBridge,
    PresentationBlueprintBridge,
    RenderArtifact,
    ScientificDocumentBlueprintBridge,
    WorksheetBlueprintBridge,
)
from app.integration.renderer_adapters import (
    HandoutContractAdapter,
    PresentationContractAdapter,
    ScientificDocumentContractAdapter,
    WorksheetContractAdapter,
)
from app.integration.renderer_adapters.contracts import (
    DocumentContent,
    LegacyPresentationDeck,
    LegacyScientificDocument,
    LegacyWorksheetDocument,
)

ROOT_DIR = Path(__file__).parent.parent.parent.parent
DEFAULT_FIXTURE_PATH = ROOT_DIR / "tests" / "fixtures" / "oobleck_experiment.md"


def get_baseline_manifest(fixture_path: Path | None = None) -> UniversalKnowledgeManifest:
    """Compiles a fixture markdown file into UniversalKnowledgeManifest deterministically."""
    target_path = fixture_path or DEFAULT_FIXTURE_PATH
    content = target_path.read_text(encoding="utf-8")
    compiler = KnowledgeCompiler(resolution_provider=OfflineMockResolutionProvider())
    return asyncio.run(compiler.compile(content, source_filename=target_path.name))


def get_baseline_artifacts(
    fixture_path: Path | None = None,
) -> Tuple[LegacyPresentationDeck, DocumentContent, LegacyWorksheetDocument, LegacyScientificDocument]:
    """Builds clean baseline legacy models for all 4 artifact types from source."""
    manifest = get_baseline_manifest(fixture_path)
    selector = KnowledgeSelectionEngine()

    # 1. Presentation
    pres_intent = get_default_intent(ArtifactType.PRESENTATION)
    pres_ctx = selector.select(manifest, pres_intent)
    pres_bp = PresentationTransformer().transform(manifest, pres_ctx, pres_intent)
    pres_ra = PresentationBlueprintBridge().bridge(pres_bp)
    pres_deck = PresentationContractAdapter().adapt(pres_ra)

    # 2. Handout
    handout_intent = get_default_intent(ArtifactType.HANDOUT)
    handout_ctx = selector.select(manifest, handout_intent)
    handout_bp = HandoutTransformer().transform(manifest, handout_ctx, handout_intent)
    handout_ra = HandoutBlueprintBridge().bridge(handout_bp)
    handout_doc = HandoutContractAdapter().adapt(handout_ra)

    # 3. Worksheet
    ws_intent = get_default_intent(ArtifactType.WORKSHEET)
    ws_ctx = selector.select(manifest, ws_intent)
    ws_bp = WorksheetTransformer().transform(manifest, ws_ctx, ws_intent)
    ws_ra = WorksheetBlueprintBridge().bridge(ws_bp)
    ws_doc = WorksheetContractAdapter().adapt(ws_ra, grouping_mode="compatibility")

    # 4. Scientific Document
    sci_intent = get_default_intent(ArtifactType.SCIENTIFIC_DOCUMENT)
    sci_ctx = selector.select(manifest, sci_intent)
    sci_bp = ScientificDocumentTransformer().transform(manifest, sci_ctx, sci_intent)
    sci_ra = ScientificDocumentBlueprintBridge().bridge(sci_bp)
    sci_doc = ScientificDocumentContractAdapter().adapt(sci_ra)

    return pres_deck, handout_doc, ws_doc, sci_doc
