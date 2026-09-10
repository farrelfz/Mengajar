"""
Universal Document Intelligence System V5 — Adversarial Quality Testing Package.

Phase 2C: Adversarial mutations representing realistic failure modes across
Presentation, Handout, Worksheet, and Scientific Document.
"""

from __future__ import annotations

from app.quality.adversarial.mutation_contract import ArtifactMutation
from app.quality.adversarial.base import BaseArtifactAdversary
from app.quality.adversarial.presentation_adversary import PresentationAdversary
from app.quality.adversarial.handout_adversary import HandoutAdversary
from app.quality.adversarial.worksheet_adversary import WorksheetAdversary
from app.quality.adversarial.scientific_adversary import ScientificDocumentAdversary
from app.quality.adversarial.adversarial_fixture import (
    get_baseline_artifacts,
    get_baseline_manifest,
)

__all__ = [
    "ArtifactMutation",
    "BaseArtifactAdversary",
    "PresentationAdversary",
    "HandoutAdversary",
    "WorksheetAdversary",
    "ScientificDocumentAdversary",
    "get_baseline_artifacts",
    "get_baseline_manifest",
]
