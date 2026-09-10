"""
Universal Document Intelligence System V5 — Visual Benchmark Comparison.

Phase 5: Evaluates visual/physical quality alignment (e.g. typography, density, rhythm).
"""

from typing import Any, Dict
from app.benchmarking.golden_contracts import (
    DimensionResult,
    VariationPolicy,
    GoldenArtifactReference
)
from app.benchmarking.comparison.base import BenchmarkComparison

class VisualComparison(BenchmarkComparison):
    dimension_name = "VISUAL"
    
    def evaluate(
        self,
        generated_artifact_state: Dict[str, Any],
        golden_reference: GoldenArtifactReference
    ) -> DimensionResult:
        
        expected_visual = golden_reference.visual_expectations
        policy = golden_reference.acceptable_variations.get("visual", VariationPolicy.EXACT)
        
        gen_density = generated_artifact_state.get("visual_density", 0.0)
        expected_density = expected_visual.get("visual_density", 0.0)
        
        if expected_density == 0.0:
            return DimensionResult(
                dimension=self.dimension_name,
                raw_measurements={"density_diff": 0.0},
                normalized_score=1.0,
                confidence=1.0,
                applicability=0.0,
                comparison_mode=policy
            )
            
        diff = abs(gen_density - expected_density)
        
        # A density difference of 0.1 is 10% bounding box area difference.
        if policy == VariationPolicy.EXACT:
            score = max(0.0, 1.0 - (diff * 5.0)) # Highly sensitive
        elif policy == VariationPolicy.TOLERANT:
            score = 1.0 if diff <= 0.15 else max(0.0, 1.0 - ((diff - 0.15) * 5.0))
        elif policy == VariationPolicy.FUNCTIONAL_EQUIVALENCE:
            score = 1.0 if diff <= 0.25 else max(0.0, 1.0 - ((diff - 0.25) * 4.0))
        else:
            score = max(0.0, 1.0 - (diff * 2.0))
            
        return DimensionResult(
            dimension=self.dimension_name,
            raw_measurements={
                "expected_density": expected_density,
                "generated_density": gen_density,
                "diff": diff
            },
            normalized_score=score,
            confidence=0.9,
            applicability=1.0,
            evidence=f"Visual density difference is {diff:.2f} ({policy.value}).",
            comparison_mode=policy
        )
