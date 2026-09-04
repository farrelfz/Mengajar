"""
KIR AI Document Intelligence — Orchestration Pipeline.

Ties together the agents into the Batch 2 master workflow:
Input -> Content Intelligence -> Document Planner -> Quality Critic
"""

from __future__ import annotations

from datetime import UTC, datetime

from app.agents.content_intelligence_agent import ContentIntelligenceAgent
from app.agents.document_planner import DocumentPlanner
from app.agents.quality_critic import QualityCritic
from app.core.logging import get_logger
from app.intelligence.schemas import (
    DocumentGenre,
    DocumentMode,
    FailureCategory,
    JobState,
    PipelineJob,
)

log = get_logger(__name__)


class IntelligencePipeline:
    """Master pipeline orchestrating Batch 2 agents."""

    def __init__(
        self,
        intelligence_agent: ContentIntelligenceAgent | None = None,
        planner_agent: DocumentPlanner | None = None,
        critic_agent: QualityCritic | None = None,
    ) -> None:
        self.intelligence_agent = intelligence_agent or ContentIntelligenceAgent()
        self.planner_agent = planner_agent or DocumentPlanner()
        self.critic_agent = critic_agent or QualityCritic()

    async def run(
        self,
        raw_input: str | bytes,
        source_hint: str,
        document_genre: DocumentGenre = DocumentGenre.GENERAL,
        document_mode: DocumentMode = DocumentMode.A4_TUTORIAL,
    ) -> PipelineJob:
        """Run the full intelligence pipeline.

        Parameters
        ----------
        raw_input:
            The raw text/markdown/bytes to analyze.
        source_hint:
            A descriptive name for logging (e.g. filename).
        document_genre:
            Whether this is a TUTORIAL, RESEARCH_REPORT, etc.
        document_mode:
            The target output mode.

        Returns
        -------
        PipelineJob
            The state and results of the job.
        """
        job = PipelineJob(
            source_file=source_hint,
            document_mode=document_mode,
            state=JobState.RUNNING,
        )
        
        log.info(
            "pipeline.start",
            job_id=job.job_id,
            source=source_hint,
            genre=document_genre.value,
        )
        
        try:
            # 1. Content Intelligence (Semantic Analysis)
            analysis = await self.intelligence_agent.execute(
                raw_input=raw_input,
                source_hint=source_hint,
                document_genre=document_genre,
                job_id=job.job_id,
            )
            analysis.recommended_mode = document_mode
            job.analysis_result = analysis

            # 2. Document Planning (Content-to-Blueprint)
            blueprint = await self.planner_agent.plan(analysis)
            job.blueprint_proposal = blueprint

            # 3. Quality Critique (Enforcement)
            critique = await self.critic_agent.critique_blueprint(blueprint, job.job_id)
            
            if not critique.is_acceptable:
                blueprint.blueprint_warnings.extend(critique.critical_issues)
                log.warning(
                    "pipeline.critique_failed",
                    job_id=job.job_id,
                    issues=critique.critical_issues,
                )

            # Success
            job.state = JobState.COMPLETE
            job.completed_at = datetime.now(UTC).isoformat()
            
            log.info("pipeline.complete", job_id=job.job_id)
            
        except Exception as exc:
            # Determine failure category heuristically
            cat = FailureCategory.INPUT_FAILURE
            if "Timeout" in str(type(exc)):
                cat = FailureCategory.MODEL_TIMEOUT
            elif "Unavailable" in str(type(exc)):
                cat = FailureCategory.MODEL_UNAVAILABLE
                
            job.state = JobState.FAILED
            job.failure_category = cat
            job.failure_message = str(exc)
            job.completed_at = datetime.now(UTC).isoformat()
            
            log.error(
                "pipeline.failed",
                job_id=job.job_id,
                error=str(exc),
                category=cat.value,
            )
            
        return job
