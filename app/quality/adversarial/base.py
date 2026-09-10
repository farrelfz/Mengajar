"""
Universal Document Intelligence System V5 — Base Adversary Class.

Phase 2C: Provides deterministic mutation engine for artifact adversaries.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Tuple
from copy import deepcopy

from app.quality.adversarial.mutation_contract import ArtifactMutation


class BaseArtifactAdversary(ABC):
    """Abstract base class for artifact-specific adversaries."""

    @property
    @abstractmethod
    def supported_artifact_type(self) -> str:
        """The target artifact type (PRESENTATION, HANDOUT, WORKSHEET, SCIENTIFIC_DOCUMENT)."""
        pass

    @abstractmethod
    def list_mutations(self) -> List[ArtifactMutation]:
        """Returns all registered mutations for this artifact adversary."""
        pass

    @abstractmethod
    def apply_mutation(self, artifact: Any, mutation_id: str) -> Tuple[Any, ArtifactMutation]:
        """Applies a specific mutation to the artifact and returns (mutated_artifact, mutation)."""
        pass
