"""
KIR AI Document Intelligence — Content Intelligence Agent.

Orchestrates the entire intelligence pipeline (normalization -> segmentation
-> classification -> relationships -> importance -> visual intent -> traceability)
for a document.
"""

from __future__ import annotations

from app.agents.base import BaseAgent
from app.intelligence.classifier import SemanticClassifier
from app.intelligence.importance_scorer import ImportanceScorer
from app.intelligence.normalizer import InputNormalizer, NormalizedDocument
from app.intelligence.relationship_extractor import RelationshipExtractor
from app.intelligence.research_role_detector import ResearchRoleDetector
from app.intelligence.schemas import (
    AnalysisResult,
    ContentUnit,
    DocumentGenre,
    ResearchTraceability,
)
from app.intelligence.segmenter import ContentSegmenter
from app.intelligence.traceability_engine import ResearchTraceabilityEngine
from app.intelligence.visual_intent_detector import VisualIntentDetector


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
    ) -> AnalysisResult:
        self.log_start(job_id=job_id, source_hint=source_hint, genre=document_genre.value)
        
        try:
            # 1. Normalize
            norm_doc: NormalizedDocument = self.normalizer.normalize(raw_input, source_hint, job_id)
            
            # 2. Segment
            seg_result = self.segmenter.segment(norm_doc, job_id)
            units: list[ContentUnit] = seg_result.content_units
            
            # 3. Classify (General + Research roles)
            for i, unit in enumerate(units):
                ctx_before = "\n".join(u.normalized_text for u in units[max(0, i-2):i])
                ctx_after = "\n".join(u.normalized_text for u in units[i+1:min(len(units), i+3)])
                
                # General type
                class_res = await self.classifier.classify(unit, ctx_before, ctx_after, job_id)
                unit.content_type = class_res.content_type
                
                # KTI role if applicable
                if document_genre == DocumentGenre.RESEARCH_REPORT:
                    role_res = await self.research_role_detector.detect(unit, ctx_before, ctx_after, job_id)
                    unit.research_role = role_res.research_role
                    unit.kti_bab = role_res.kti_bab
                    unit.is_core_component = role_res.is_core_component

            # 4. Relationships (Traceability Graph)
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
