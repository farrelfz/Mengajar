"""
Universal Knowledge Core — KnowledgeCompiler Master Orchestrator.

Orchestrates the canonical 9-stage knowledge compilation pipeline:
RawSource -> StructuralExtractor -> UnitNormalizer -> LocalClassifier -> AmbiguityResolver ->
PayloadBuilder -> ClaimEvidenceExtractor -> RelationshipInferencer -> ImportanceAnalyzer -> ManifestAssembler -> Immutable UniversalKnowledgeManifest.
"""

from __future__ import annotations

import asyncio
import time
from typing import List, Optional

from app.intelligence.pipeline.ambiguity_resolver import AmbiguityResolver, SemanticResolutionProvider
from app.intelligence.pipeline.claim_evidence_extractor import ClaimEvidenceExtractor
from app.intelligence.pipeline.importance_analyzer import ImportanceAnalyzer
from app.intelligence.pipeline.local_classifier import LocalClassifier
from app.intelligence.pipeline.manifest_assembler import ManifestAssembler
from app.intelligence.pipeline.payload_builder import PayloadBuilder
from app.intelligence.pipeline.relationship_inferencer import RelationshipInferencer
from app.intelligence.pipeline.structural_extractor import StructuralExtractor
from app.intelligence.pipeline.unit_normalizer import UnitNormalizer
from app.intelligence.schemas import AudienceProfile, UniversalKnowledgeManifest


class KnowledgeCompiler:
    """Master Orchestrator executing the canonical 9-Stage Knowledge Compilation Pipeline."""

    def __init__(
        self,
        resolution_provider: SemanticResolutionProvider | None = None,
    ) -> None:
        self.stage1_extractor = StructuralExtractor()
        self.stage2_normalizer = UnitNormalizer()
        self.stage3_classifier = LocalClassifier()
        self.stage4_resolver = AmbiguityResolver(provider=resolution_provider)
        self.stage5_builder = PayloadBuilder()
        self.stage6_claim_extractor = ClaimEvidenceExtractor()
        self.stage7_inferencer = RelationshipInferencer()
        self.stage8_analyzer = ImportanceAnalyzer()
        self.stage9_assembler = ManifestAssembler()

    async def compile(
        self,
        raw_text: str,
        source_filename: str = "input.md",
        domain: str = "general_science",
        audience: AudienceProfile | None = None,
    ) -> UniversalKnowledgeManifest:
        """Executes canonical 9-stage compilation pipeline asynchronously."""
        # STAGE 1: Structural Extraction
        structural_tree = self.stage1_extractor.extract(raw_text, source_filename=source_filename)

        # STAGE 2: Unit Normalization
        candidate_units = self.stage2_normalizer.normalize(structural_tree)

        # STAGE 3: Local Rule Classification
        classified_units = self.stage3_classifier.classify(candidate_units)

        # STAGE 4: Selective Ambiguity Resolution (Async AI Gateway / Offline Mock)
        resolved_units = await self.stage4_resolver.resolve(classified_units)

        # STAGE 5: Atomic Typed Payload Construction
        atomic_units = self.stage5_builder.build_units(resolved_units)

        # STAGE 6: Claim & Evidence Extraction
        claim_evidence = self.stage6_claim_extractor.extract(atomic_units)

        # STAGE 7: Relationship Inference
        relationships = self.stage7_inferencer.infer(atomic_units, claim_evidence)

        # STAGE 8: Domain-Intrinsic Importance Analysis
        importance_units = self.stage8_analyzer.analyze(atomic_units, relationships)

        # STAGE 9: Manifest Assembly & Immutability Lock
        ambiguity_count = sum(1 for ru in resolved_units if ru.ai_resolved)
        ambiguity_ratio = ambiguity_count / max(1, len(resolved_units))

        manifest_id = f"man_{structural_tree.source_fingerprint[:12]}"
        manifest = self.stage9_assembler.assemble(
            manifest_id=manifest_id,
            document_title=structural_tree.title,
            domain=domain,
            audience=audience,
            units=importance_units,
            relationships=relationships,
            total_sections=len(structural_tree.sections),
            total_raw_blocks=structural_tree.total_blocks_count,
            ambiguity_ratio=round(ambiguity_ratio, 3),
        )

        return manifest

    def compile_sync(
        self,
        raw_text: str,
        source_filename: str = "input.md",
        domain: str = "general_science",
        audience: AudienceProfile | None = None,
    ) -> UniversalKnowledgeManifest:
        """Synchronous wrapper for offline / blocking pipeline calls."""
        return asyncio.run(self.compile(raw_text, source_filename=source_filename, domain=domain, audience=audience))
