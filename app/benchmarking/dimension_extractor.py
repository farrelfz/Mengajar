"""
Universal Document Intelligence System V5 — Benchmark Dimension Extractor.

Phase 5: Canonical adapter extracting orthogonal benchmark dimension results from
production outputs, blueprints, and UnifiedQualityReports against Golden References.
Does NOT create a competing quality authority; strictly acts as an observational consumer.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from app.benchmarking.comparison import (
    SemanticComparison,
    StructuralComparison,
    VisualComparison,
    create_pedagogical_comparison,
    create_scientific_comparison,
)
from app.benchmarking.golden_contracts import (
    DimensionResult,
    ExpectedInvariants,
    GoldenArtifactReference,
    VariationPolicy,
)
from app.quality.contracts.authority import UnifiedQualityReport


class BenchmarkDimensionExtractor:
    """Extracts standardized multi-dimensional benchmark results from production artifacts."""

    @classmethod
    def extract_dimensions(
        cls,
        artifact_type: str,
        artifact_data: Dict[str, Any],
        golden_reference: GoldenArtifactReference,
        quality_report: Optional[UnifiedQualityReport] = None,
    ) -> Tuple[Dict[str, DimensionResult], Dict[str, bool]]:
        """
        Extracts benchmark dimension results and hard invariant results.
        
        Args:
            artifact_type: PRESENTATION, HANDOUT, WORKSHEET, or SCIENTIFIC_DOCUMENT.
            artifact_data: Dictionary of extracted artifact features/states.
            golden_reference: The authoritative benchmark reference.
            quality_report: Optional UnifiedQualityReport from Level-0 production evaluation.
            
        Returns:
            Tuple of (dimension_results, hard_invariant_results).
        """
        dim_results: Dict[str, DimensionResult] = {}
        invariant_results: Dict[str, bool] = {}

        # 1. SEMANTIC DIMENSION
        sem_comp = SemanticComparison()
        dim_results["SEMANTIC"] = sem_comp.evaluate(artifact_data, golden_reference)

        # 2. STRUCTURAL DIMENSION
        struct_comp = StructuralComparison()
        dim_results["STRUCTURAL"] = struct_comp.evaluate(artifact_data, golden_reference)

        # 3. VISUAL DIMENSION
        vis_comp = VisualComparison()
        dim_results["VISUAL"] = vis_comp.evaluate(artifact_data, golden_reference)

        # 4. ARTIFACT-SPECIFIC DIMENSIONS
        if artifact_type == "WORKSHEET":
            ped_comp = create_pedagogical_comparison()
            dim_results["PEDAGOGICAL"] = ped_comp.evaluate(artifact_data, golden_reference)
        elif artifact_type == "SCIENTIFIC_DOCUMENT":
            sci_comp = create_scientific_comparison()
            dim_results["SCIENTIFIC"] = sci_comp.evaluate(artifact_data, golden_reference)

        # 5. INTEGRATE LEVEL-0 UNIFIED QUALITY AUTHORITY SIGNALS (IF PRESENT)
        if quality_report is not None:
            # Reconcile with UQA domain scores without overriding authority
            uqa_overall = quality_report.overall_quality_score
            has_blockers = len(quality_report.hard_blockers) > 0

            # UQA Physical / Rendered Quality
            rendered_score = quality_report.domain_scores.get("rendered_quality", 1.0)
            dim_results["PHYSICAL_RENDER"] = DimensionResult(
                dimension="PHYSICAL_RENDER",
                raw_measurements={"uqa_rendered_score": rendered_score},
                normalized_score=rendered_score,
                confidence=0.95,
                applicability=1.0,
                evidence=f"UnifiedQualityAuthority rendered quality: {rendered_score:.3f}",
                comparison_mode=VariationPolicy.TOLERANT,
            )

        # 6. EXTRACT HARD INVARIANTS
        inv = golden_reference.hard_invariants
        # Invariant: No fabricated claims
        invariant_results["no_fabricated_claims"] = not artifact_data.get("has_fabricated_claims", False)
        # Invariant: No unsupported evidence
        invariant_results["no_unsupported_evidence"] = not artifact_data.get("has_unsupported_evidence", False)
        # Invariant: No text clipping
        invariant_results["no_text_clipping"] = not artifact_data.get("has_text_clipping", False)
        # Invariant: No element collision
        invariant_results["no_element_collision"] = not artifact_data.get("has_element_collision", False)
        # Invariant: Artifact type preserved
        actual_type = str(artifact_data.get("artifact_type", artifact_type)).upper()
        invariant_results["artifact_type_preserved"] = (actual_type == artifact_type.upper())

        # Specific: Worksheet anti-spoiling / answer leak
        if artifact_type == "WORKSHEET":
            leaks = artifact_data.get("has_answer_leak", False)
            invariant_results["no_answer_leak"] = not leaks

        # Specific: Scientific citation integrity
        if artifact_type == "SCIENTIFIC_DOCUMENT":
            citation_broken = artifact_data.get("has_broken_citations", False)
            invariant_results["citation_integrity_preserved"] = not citation_broken

        # If UQA reported hard blockers, record them as invariant failures
        if quality_report and quality_report.hard_blockers:
            invariant_results["production_hard_blockers_free"] = False
        else:
            invariant_results["production_hard_blockers_free"] = True

        return dim_results, invariant_results
