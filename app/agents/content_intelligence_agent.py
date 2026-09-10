"""
KIR AI Document Intelligence — Content Intelligence Agent.

Orchestrates the entire intelligence pipeline (normalization -> segmentation
-> classification -> relationships -> importance -> visual intent -> traceability)
for a document.
"""

from __future__ import annotations
import asyncio
import time
from typing import Any

from app.agents.base import BaseAgent
from app.intelligence.classifier import SemanticClassifier
from app.intelligence.importance_scorer import ImportanceScorer
from app.intelligence.normalizer import InputNormalizer, NormalizedDocument
from app.intelligence.relationship_extractor import RelationshipExtractor
from app.intelligence.research_role_detector import ResearchRoleDetector
from app.intelligence.schemas import (
    AnalysisResult,
    ContentType,
    ContentUnit,
    DocumentGenre,
    ResearchTraceability,
)
from app.intelligence.segmenter import ContentSegmenter
from app.intelligence.traceability_engine import ResearchTraceabilityEngine
from app.intelligence.visual_intent_detector import VisualIntentDetector
from app.orchestration.stage_registry import TOTAL_PIPELINE_STAGES, PipelineStageRegistry, ProgressEvent


class ContentIntelligenceAgent(BaseAgent):
    """
    Agent responsible for transforming raw text into a fully classified
    AnalysisResult via the intelligence pipeline.
    """

    def __init__(
        self,
        normalizer: InputNormalizer | None = None,
        segmenter: ContentSegmenter | None = None,
        classifier: SemanticClassifier | None = None,
        research_role_detector: ResearchRoleDetector | None = None,
        relationship_extractor: RelationshipExtractor | None = None,
        importance_scorer: ImportanceScorer | None = None,
        visual_intent_detector: VisualIntentDetector | None = None,
        traceability_engine: ResearchTraceabilityEngine | None = None,
    ) -> None:
        self.normalizer = normalizer or InputNormalizer()
        self.segmenter = segmenter or ContentSegmenter()
        self.classifier = classifier or SemanticClassifier()
        self.research_role_detector = research_role_detector or ResearchRoleDetector()
        self.relationship_extractor = relationship_extractor or RelationshipExtractor()
        self.importance_scorer = importance_scorer or ImportanceScorer()
        self.visual_intent_detector = visual_intent_detector or VisualIntentDetector()
        self.traceability_engine = traceability_engine or ResearchTraceabilityEngine()

    @property
    def name(self) -> str:
        return "content_intelligence"

    @property
    def responsibility(self) -> str:
        return "Transform unstructured content into a classified semantic model."

    async def execute(
        self,
        raw_input: str | bytes,
        source_hint: str,
        document_genre: DocumentGenre,
        job_id: str,
        progress_callback: Any = None,
    ) -> AnalysisResult:
        import inspect

        async def _notify(stage_idx: int, title: str, status: str, detail: str = "") -> None:
            if progress_callback:
                try:
                    stage_def = PipelineStageRegistry.get_stage(stage_idx)
                    event = ProgressEvent(
                        stage_number=stage_def.number,
                        total_stages=TOTAL_PIPELINE_STAGES,
                        stage_key=stage_def.key,
                        title=stage_def.name,
                        status=status,
                        detail=detail,
                        timestamp=time.time(),
                    )
                    sig = inspect.signature(progress_callback)
                    if len(sig.parameters) == 1:
                        res = progress_callback(event)
                    else:
                        res = progress_callback(stage_def.number, TOTAL_PIPELINE_STAGES, stage_def.name, status, detail)
                    if inspect.iscoroutine(res):
                        await res
                except Exception:
                    pass

        self.log_start(job_id=job_id, source_hint=source_hint, genre=document_genre.value)
        
        try:
            # 1. Normalize
            await _notify(1, "Structural Parsing & Source Integrity", "start", f"Membaca & menganalisis teks sumber ({source_hint})...")
            norm_doc: NormalizedDocument = self.normalizer.normalize(raw_input, source_hint, job_id)
            
            # 2. Segment
            seg_result = self.segmenter.segment(norm_doc, job_id)
            units: list[ContentUnit] = seg_result.content_units
            await _notify(1, "Structural Parsing & Source Integrity", "done", f"Teks dinormalisasi: {len(units)} unit semantik ({norm_doc.detected_format})")
            
            # 3. Classify: Rules First, Selective AI for Ambiguous Units
            await _notify(2, "Local Semantic Classification", "start", f"Menerapkan taksonomi struktural & rule-based pada {len(units)} unit...")
            from app.intelligence.rule_classifier import RuleClassifier
            from app.intelligence.selective_reasoner import SelectiveReasoner

            rule_engine = RuleClassifier()
            selective_reasoner = SelectiveReasoner()

            ambiguous_units: list[ContentUnit] = []
            for u in units:
                local_res = rule_engine.classify_unit(u, parent_heading=u.title or "")
                u.content_type = local_res.content_type
                if local_res.is_ambiguous:
                    ambiguous_units.append(u)

            await _notify(2, "Local Semantic Classification", "done", f"{len(units) - len(ambiguous_units)}/{len(units)} terklasifikasi lokal, {len(ambiguous_units)} ambigu")

            # 4. Selective AI Reasoning for Ambiguous Units
            if ambiguous_units:
                await _notify(3, "Selective AI Reasoning", "start", f"Menyelesaikan {len(ambiguous_units)} unit ambigu via AI Gateway (1 batched call)...")
                resolved_map = await selective_reasoner.resolve_ambiguous_blocks(
                    ambiguous_units=ambiguous_units,
                    document_title=source_hint,
                    domain=document_genre.value,
                    job_id=job_id,
                )
                for u in ambiguous_units:
                    if u.unit_id in resolved_map:
                        u.content_type = resolved_map[u.unit_id].content_type
                await _notify(3, "Selective AI Reasoning", "done", f"{len(ambiguous_units)} unit ambigu berhasil diinferensi secara batched")
            else:
                await _notify(3, "Selective AI Reasoning", "done", "Semua unit terklasifikasi 100% lokal, 0 panggilan AI diperlukan")

            # 5. Relationships (Traceability Graph)
            await _notify(4, "Content Manifest & Coverage Planning", "start", "Mendeteksi keterhubungan materi & perancangan visual intent...")
            rel_res = await self.relationship_extractor.extract_relationships(units, job_id)
            relationships = rel_res.relationships

            # 5. Importance Scoring (Heuristic)
            importance_scores = {}
            for unit in units:
                score = self.importance_scorer.score_unit(unit, relationships)
                unit.density_score = score.final_score  # Update density
                importance_scores[unit.unit_id] = score

            # 6. Visual Intent Detection
            intent_res = await self.visual_intent_detector.detect_intents(units, job_id)
            visual_intents = {res.unit_id: res for res in intent_res.intents}

            # 7. Research Traceability Map
            research_traceability: ResearchTraceability | None = None
            if document_genre == DocumentGenre.RESEARCH_REPORT:
                research_traceability = self.traceability_engine.build_traceability(
                    units=units,
                    relationships=relationships,
                )

            # 8. Assemble AnalysisResult
            analysis = AnalysisResult(
                job_id=job_id,
                source_file=source_hint,
                content_units=units,
                relationships=relationships,
                importance_scores=importance_scores,
                visual_intents=visual_intents,
                document_genre=document_genre,
                research_traceability=research_traceability,
                pipeline_warnings=norm_doc.normalization_warnings + seg_result.segmentation_warnings,
            )
            
            self.log_complete(job_id=job_id, units=len(units))
            return analysis
            
        except Exception as exc:
            self.log_failure(exc, job_id=job_id)
            raise
