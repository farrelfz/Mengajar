"""
Universal Document Intelligence System V5 — Structural Benchmark Comparison.

Phase 5: Evaluates structural alignment (e.g., flow, hierarchy, chunking).
"""

from typing import Any, Dict
from app.benchmarking.golden_contracts import (
    DimensionResult,
    VariationPolicy,
    GoldenArtifactReference
)
from app.benchmarking.comparison.base import BenchmarkComparison

class StructuralComparison(BenchmarkComparison):
    dimension_name = "STRUCTURAL"
    
    def evaluate(
        self,
        generated_artifact_state: Dict[str, Any],
        golden_reference: GoldenArtifactReference
    ) -> DimensionResult:
        
        expected_struct = golden_reference.structural_expectations
        policy = golden_reference.acceptable_variations.get("structural", VariationPolicy.EXACT)
        
        gen_blocks = generated_artifact_state.get("block_count", 0)
        expected_blocks = expected_struct.get("block_count", 0)
        
        if expected_blocks == 0:
            return DimensionResult(
                dimension=self.dimension_name,
                raw_measurements={"block_diff": 0},
                normalized_score=1.0,
                confidence=1.0,
                applicability=0.0,
                comparison_mode=policy
            )
            
        diff = abs(gen_blocks - expected_blocks)
        ratio = diff / expected_blocks
        
        if policy == VariationPolicy.EXACT:
            score = 1.0 if diff == 0 else max(0.0, 1.0 - ratio)
        elif policy == VariationPolicy.TOLERANT:
            # Tolerant allows +/- 20% deviation without penalty
            score = 1.0 if ratio <= 0.2 else max(0.0, 1.0 - (ratio - 0.2))
        elif policy == VariationPolicy.OPEN_VARIATION:
            # Highly permissive structure
            score = 1.0 if ratio <= 0.5 else max(0.0, 1.0 - (ratio - 0.5))
        else:
            score = max(0.0, 1.0 - ratio)
            
        return DimensionResult(
            dimension=self.dimension_name,
            raw_measurements={
                "expected_blocks": expected_blocks,
                "generated_blocks": gen_blocks,
                "diff": diff
            },
            normalized_score=score,
            confidence=0.85,
            applicability=1.0,
            evidence=f"Structure has {gen_blocks} blocks vs expected {expected_blocks} ({policy.value}).",
            comparison_mode=policy
        )
