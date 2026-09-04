"""
KIR AI Document Intelligence — Content-to-Blueprint Algorithm.

Transforms a fully classified AnalysisResult into a BlueprintProposal.
Groups semantically related ContentUnits into BlueprintCandidates.
"""

from __future__ import annotations

from app.core.exceptions import BlueprintError
from app.core.logging import get_logger
from app.intelligence.schemas import (
    AnalysisResult,
    BlueprintCandidateType,
    BlueprintProposal,
    ContentDensity,
    ContentGroup,
    ContentType,
    VisualIntent,
)

log = get_logger(__name__)


class BlueprintProposer:
    """Algorithm that transforms semantic intelligence into a document blueprint."""

    def propose(self, analysis: AnalysisResult) -> BlueprintProposal:
        """Create a BlueprintProposal from an AnalysisResult.

        Groups units based on headings, semantic continuity, and relationship.

        Parameters
        ----------
        analysis:
            The complete AnalysisResult from the intelligence pipeline.

        Returns
        -------
        BlueprintProposal
            The blueprint-ready model.

        Raises
        ------
        BlueprintError
            If a blueprint cannot be constructed.
        """
        log.debug("blueprint_proposer.start", job_id=analysis.job_id)

        try:
            content_groups = self._group_units(analysis)
            
            density = self._estimate_overall_density(content_groups)

            proposal = BlueprintProposal(
                source_analysis_id=analysis.job_id,
                document_title=self._extract_title(analysis),
                document_genre=analysis.document_genre,
                recommended_mode=analysis.recommended_mode,
                content_groups=content_groups,
                total_estimated_density=density,
                research_traceability=analysis.research_traceability,
                traceability_warnings=[
                    w.value for w in getattr(analysis.research_traceability, "traceability_warnings", [])
                ] if analysis.research_traceability else [],
            )
            
            log.info(
                "blueprint_proposer.complete",
                job_id=analysis.job_id,
                group_count=len(content_groups),
                density=density.value,
            )
            
            return proposal
            
        except Exception as exc:
            raise BlueprintError(
                f"Failed to propose blueprint: {exc}",
                job_id=analysis.job_id,
                step="blueprint_proposal",
            ) from exc

    def _group_units(self, analysis: AnalysisResult) -> list[ContentGroup]:
        """Group units heuristically based on heading boundaries and semantic continuity."""
        groups: list[ContentGroup] = []
        current_group: ContentGroup | None = None
        
        # Helper to finalize and append a group
        def _close_group():
            nonlocal current_group
            if current_group and current_group.unit_ids:
                # Assign blueprint candidate type heuristically
                self._assign_candidate_type(current_group, analysis)
                groups.append(current_group)
            current_group = None

        for unit in analysis.content_units:
            # Headings start a new group
            if unit.content_type == ContentType.TITLE:
                _close_group()
                current_group = ContentGroup(
                    title=unit.title or unit.normalized_text[:50],
                    kti_bab=unit.kti_bab,
                )
                current_group.unit_ids.append(unit.unit_id)
                continue
                
            # If no group exists yet, create one
            if not current_group:
                current_group = ContentGroup()
                
            # Check for strong semantic boundaries that force a new group
            # (e.g. moving from Data to Interpretation)
            if unit.research_role in (
                ContentType.RESEARCH_RESULT,
                ContentType.RESEARCH_INTERPRETATION,
                ContentType.RESEARCH_CONCLUSION,
            ):
                _close_group()
                current_group = ContentGroup(kti_bab=unit.kti_bab)
                
            current_group.unit_ids.append(unit.unit_id)
            
        _close_group()
        
        # Link dependencies
        for i in range(1, len(groups)):
            groups[i].previous_group_dependency = groups[i-1].group_id
            groups[i-1].next_group_dependency = groups[i].group_id
            groups[i-1].continuation_required = True
            
        return groups

    def _assign_candidate_type(self, group: ContentGroup, analysis: AnalysisResult) -> None:
        """Heuristically assign a BlueprintCandidateType to a group."""
        types_in_group = [
            u.research_role or u.content_type 
            for u in analysis.content_units 
            if u.unit_id in group.unit_ids
        ]
        
        if ContentType.TITLE in types_in_group and len(types_in_group) == 1:
            group.blueprint_candidate = BlueprintCandidateType.TITLE_BLOCK
        elif (
            ContentType.RESEARCH_RESULT in types_in_group
            or ContentType.DATA in types_in_group
            or ContentType.DATA_POINT in types_in_group
        ):
            group.blueprint_candidate = BlueprintCandidateType.RESEARCH_RESULT_BLOCK
        elif ContentType.RESEARCH_CONCLUSION in types_in_group or ContentType.CONCLUSION in types_in_group:
            group.blueprint_candidate = BlueprintCandidateType.CONCLUSION_BLOCK
        elif ContentType.RESEARCH_METHOD in types_in_group or ContentType.PROCEDURE in types_in_group:
            group.blueprint_candidate = BlueprintCandidateType.PROCESS_SEQUENCE
        else:
            group.blueprint_candidate = BlueprintCandidateType.GENERIC_CONTENT

        # Promote highest intent
        intents = [
            analysis.visual_intents.get(uid) 
            for uid in group.unit_ids 
            if uid in analysis.visual_intents
        ]
        if intents:
            # Just take the first non-text intent if available
            for intent_res in intents:
                if intent_res.primary_intent != VisualIntent.TEXT_FOCUSED:
                    group.primary_visual_intent = intent_res.primary_intent
                    break

    def _estimate_overall_density(self, groups: list[ContentGroup]) -> ContentDensity:
        """Estimate the overall document density."""
        if len(groups) > 20:
            return ContentDensity.HIGH
        elif len(groups) > 10:
            return ContentDensity.MEDIUM
        return ContentDensity.LOW

    def _extract_title(self, analysis: AnalysisResult) -> str:
        for unit in analysis.content_units:
            if unit.content_type == ContentType.TITLE and unit.depth == 1:
                return unit.normalized_text
        return "Untitled Document"
