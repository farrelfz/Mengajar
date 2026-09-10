"""
Universal Document Intelligence System V5 — Semantic Benchmark Comparison.

Phase 5: Evaluates semantic alignment with the golden artifact.
"""

from typing import Any, Dict
from app.benchmarking.golden_contracts import (
    DimensionResult,
    VariationPolicy,
    GoldenArtifactReference
)
from app.benchmarking.comparison.base import BenchmarkComparison

class SemanticComparison(BenchmarkComparison):
    dimension_name = "SEMANTIC"
    
    def evaluate(
        self,
        generated_artifact_state: Dict[str, Any],
        golden_reference: GoldenArtifactReference
    ) -> DimensionResult:
        
        expected_semantics = golden_reference.semantic_expectations
        policy = golden_reference.acceptable_variations.get("semantic", VariationPolicy.EXACT)
        
        # In a real implementation, this would compute true knowledge-graph or embedding overlap.
        # Here we mock the structural extraction to conform to the pipeline expectations.
        gen_concepts = set(generated_artifact_state.get("concepts", []))
        expected_concepts = set(expected_semantics.get("concepts", []))
        
        if not expected_concepts:
            return DimensionResult(
                dimension=self.dimension_name,
                raw_measurements={"concept_overlap": 1.0},
                normalized_score=1.0,
                confidence=1.0,
                applicability=0.0,
                comparison_mode=policy
            )
            
        overlap = len(gen_concepts.intersection(expected_concepts))
        total = len(expected_concepts)
        ratio = overlap / total if total > 0 else 0.0
        
        score = ratio
        if policy == VariationPolicy.TOLERANT:
            score = min(1.0, ratio * 1.1)  # forgiving curve
        elif policy == VariationPolicy.FUNCTIONAL_EQUIVALENCE:
            # We care if the core is represented, even if specific concepts vary slightly
            score = min(1.0, ratio * 1.25)
            
        return DimensionResult(
            dimension=self.dimension_name,
            raw_measurements={
                "expected_concepts": len(expected_concepts),
                "generated_concepts": len(gen_concepts),
                "overlap": overlap,
                "ratio": ratio
            },
            normalized_score=score,
            confidence=0.9,
            applicability=1.0,
            evidence=f"Matched {overlap} out of {total} expected concepts.",
            comparison_mode=policy
        )
