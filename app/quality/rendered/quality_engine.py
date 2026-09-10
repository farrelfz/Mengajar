"""
Universal Document Intelligence System V5 — Master Rendered Quality Engine.

Phase 3A: Unified entry point coordinating independent physical PDF and raster
inspection across all four artifact types.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

from app.quality.rendered.contracts import RenderedArtifactInspection
from app.quality.rendered.handout_quality import HandoutRenderedQualityEvaluator
from app.quality.rendered.presentation_quality import (
    PresentationRenderedQualityEvaluator,
)
from app.quality.rendered.scientific_quality import (
    ScientificRenderedQualityEvaluator,
)
from app.quality.rendered.worksheet_quality import (
    WorksheetRenderedQualityEvaluator,
)


class MasterRenderedQualityEngine:
    """Dispatches rendered PDF inspection to artifact-specific quality evaluators."""

    def __init__(self) -> None:
        self.presentation_evaluator = PresentationRenderedQualityEvaluator()
        self.handout_evaluator = HandoutRenderedQualityEvaluator()
        self.worksheet_evaluator = WorksheetRenderedQualityEvaluator()
        self.scientific_evaluator = ScientificRenderedQualityEvaluator()

    def inspect(
        self,
        pdf_path: Path | str,
        artifact_type: str,
        html_path: Path | str | None = None,
        source_metadata: Dict[str, Any] | None = None,
    ) -> RenderedArtifactInspection:
        """Independently evaluates physical rendered PDF and returns typed inspection outcome."""
        p_path = Path(pdf_path)
        h_path = Path(html_path) if html_path else None
        norm_type = artifact_type.upper()

        if not p_path.exists():
            raise FileNotFoundError(f"Rendered PDF does not exist: {p_path}")

        if norm_type == "PRESENTATION":
            return self.presentation_evaluator.evaluate(p_path, h_path, source_metadata)
        elif norm_type == "HANDOUT":
            return self.handout_evaluator.evaluate(p_path, h_path, source_metadata)
        elif norm_type == "WORKSHEET":
            return self.worksheet_evaluator.evaluate(p_path, h_path, source_metadata)
        elif norm_type == "SCIENTIFIC_DOCUMENT":
            return self.scientific_evaluator.evaluate(p_path, h_path, source_metadata)
        else:
            raise ValueError(f"Unsupported artifact type for rendered quality inspection: '{artifact_type}'")
