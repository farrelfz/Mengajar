"""
Universal Document Intelligence System V5 — Artifact-Specific Benchmark Comparison.

Phase 5: Evaluates dimensions unique to specific artifact types
(e.g., Pedagogical for Worksheets, Scientific for KTI).
"""

from typing import Any, Dict
from app.benchmarking.golden_contracts import (
    DimensionResult,
    VariationPolicy,
    GoldenArtifactReference
)
from app.benchmarking.comparison.base import BenchmarkComparison

class ArtifactSpecificComparison(BenchmarkComparison):
    def __init__(self, dimension_name: str, keys_to_check: list[str], dict_name: str):
        self.dimension_name = dimension_name
        self.keys_to_check = keys_to_check
        self.dict_name = dict_name
        
    def evaluate(
        self,
        generated_artifact_state: Dict[str, Any],
        golden_reference: GoldenArtifactReference
    ) -> DimensionResult:
        
        expected_dict = getattr(golden_reference, self.dict_name, {})
        policy = golden_reference.acceptable_variations.get(self.dimension_name.lower(), VariationPolicy.EXACT)
        
        if not expected_dict or not self.keys_to_check:
            return DimensionResult(
                dimension=self.dimension_name,
                raw_measurements={},
                normalized_score=1.0,
                confidence=1.0,
                applicability=0.0,
                comparison_mode=policy
            )
            
        matches = 0
        total = 0
        measurements = {}
        
        for key in self.keys_to_check:
            if key in expected_dict:
                total += 1
                gen_val = generated_artifact_state.get(key)
                exp_val = expected_dict[key]
                measurements[key] = {"expected": exp_val, "generated": gen_val}
                if gen_val == exp_val:
                    matches += 1
                    
        ratio = matches / total if total > 0 else 1.0
        
        score = ratio
        if policy == VariationPolicy.TOLERANT and ratio >= 0.8:
            score = 1.0
            
        return DimensionResult(
            dimension=self.dimension_name,
            raw_measurements=measurements,
            normalized_score=score,
            confidence=0.9,
            applicability=1.0 if total > 0 else 0.0,
            evidence=f"Matched {matches} of {total} {self.dimension_name.lower()} expectations.",
            comparison_mode=policy
        )

# Factory for convenience
def create_pedagogical_comparison() -> BenchmarkComparison:
    return ArtifactSpecificComparison(
        dimension_name="PEDAGOGICAL",
        keys_to_check=["inquiry_arc_complete", "observation_before_explanation"],
        dict_name="pedagogical_expectations"
    )

def create_scientific_comparison() -> BenchmarkComparison:
    return ArtifactSpecificComparison(
        dimension_name="SCIENTIFIC",
        keys_to_check=["citation_density", "evidence_linkage_intact"],
        dict_name="scientific_expectations"
    )
