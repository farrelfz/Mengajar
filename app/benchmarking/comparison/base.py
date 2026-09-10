"""
Universal Document Intelligence System V5 — Base Comparison Contract.

Phase 5: Defines the base protocol for all benchmark comparisons.
"""

from typing import Any, Dict, Protocol

from app.benchmarking.golden_contracts import (
    DimensionResult,
    VariationPolicy,
    GoldenArtifactReference
)

class BenchmarkComparison(Protocol):
    """Protocol for a multi-dimensional benchmark comparison engine."""
    
    dimension_name: str
    
    def evaluate(
        self,
        generated_artifact_state: Dict[str, Any],
        golden_reference: GoldenArtifactReference
    ) -> DimensionResult:
        """
        Evaluates a specific quality dimension of the generated artifact
        against the objective golden reference.
        
        Args:
            generated_artifact_state: The actual extracted features of the generated artifact.
            golden_reference: The objective golden standard expectations.
            
        Returns:
            A DimensionResult containing normalized scores and confidence.
        """
        ...
