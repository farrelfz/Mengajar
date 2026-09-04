"""
KIR AI Document Intelligence — Research Traceability Engine.

Constructs and validates the canonical KTI traceability graph:
PROBLEM → QUESTION → OBJECTIVE → METHOD → DATA → FINDING → INTERPRETATION → CONCLUSION → RECOMMENDATION
"""

from __future__ import annotations

from app.core.logging import get_logger
from app.intelligence.schemas import (
    ConclusionTrace,
    ContentRelationship,
    ContentType,
    ContentUnit,
    KtiBab,
    RecommendationBasis,
    RelationshipType,
    ResearchTraceability,
    TraceabilityWarning,
)

log = get_logger(__name__)


class ResearchTraceabilityEngine:
    """Builds and validates the research traceability graph for KTI documents."""

    def build_traceability(
        self,
        units: list[ContentUnit],
        relationships: list[ContentRelationship],
    ) -> ResearchTraceability:
        """Analyze units and relationships to build a validated ResearchTraceability map.

        Parameters
        ----------
        units:
            All classified ContentUnits.
        relationships:
            All detected semantic relationships.

        Returns
        -------
        ResearchTraceability
            Structured map with coverage, conclusion traces, recommendation bases, and warnings.
        """
        # 1. Detect presence of core research components
        unit_types = {u.research_role or u.content_type for u in units}
        
        has_problem = ContentType.RESEARCH_PROBLEM in unit_types or ContentType.PROBLEM in unit_types
        has_question = ContentType.RESEARCH_QUESTION in unit_types or ContentType.QUESTION in unit_types
        has_objective = ContentType.RESEARCH_OBJECTIVE in unit_types or ContentType.OBJECTIVE in unit_types
        has_hypothesis = ContentType.RESEARCH_HYPOTHESIS in unit_types or ContentType.HYPOTHESIS in unit_types
        has_theory = ContentType.THEORETICAL_FOUNDATION in unit_types or ContentType.THEORY in unit_types
        has_prior = ContentType.RESEARCH_PRIOR in unit_types or ContentType.PRIOR_RESEARCH in unit_types
        has_method = ContentType.RESEARCH_METHOD in unit_types or ContentType.METHOD in unit_types or ContentType.RESEARCH_PROCEDURE in unit_types
        has_results = ContentType.RESEARCH_RESULT in unit_types or ContentType.DATA in unit_types or ContentType.RESULT in unit_types or ContentType.RESEARCH_FINDING in unit_types
        has_discussion = ContentType.RESEARCH_DISCUSSION in unit_types or ContentType.DISCUSSION in unit_types or ContentType.RESEARCH_INTERPRETATION in unit_types or ContentType.INTERPRETATION in unit_types
        has_conclusion = ContentType.RESEARCH_CONCLUSION in unit_types or ContentType.CONCLUSION in unit_types
        has_recommendation = ContentType.RESEARCH_RECOMMENDATION in unit_types or ContentType.RECOMMENDATION in unit_types

        # 2. Detect BAB coverage
        detected_babs: set[KtiBab] = set()
        for u in units:
            if u.kti_bab:
                detected_babs.add(u.kti_bab)
        
        # Heuristic BAB detection from roles if kti_bab not explicitly set
        if has_problem or has_question or has_objective:
            detected_babs.add(KtiBab.BAB_1)
        if has_theory or has_prior:
            detected_babs.add(KtiBab.BAB_2)
        if has_method:
            detected_babs.add(KtiBab.BAB_3)
        if has_results or has_discussion:
            detected_babs.add(KtiBab.BAB_4)
        if has_conclusion or has_recommendation:
            detected_babs.add(KtiBab.BAB_5)

        # Sort BAB coverage
        bab_order = [KtiBab.BAB_1, KtiBab.BAB_2, KtiBab.BAB_3, KtiBab.BAB_4, KtiBab.BAB_5]
        sorted_babs = [b for b in bab_order if b in detected_babs]

        # 3. Missing critical components
        missing: list[str] = []
        if not has_problem:
            missing.append("RESEARCH_PROBLEM")
        if not has_objective and not has_question:
            missing.append("RESEARCH_OBJECTIVE/QUESTION")
        if not has_method:
            missing.append("RESEARCH_METHOD")
        if not has_results:
            missing.append("RESEARCH_RESULT")
        if not has_conclusion:
            missing.append("RESEARCH_CONCLUSION")

        # 4. Warnings and Traces
        warnings: list[TraceabilityWarning] = []
        
        # Check BAB coverage completeness
        if len(sorted_babs) < 3 and len(units) > 5:
            warnings.append(TraceabilityWarning.MISSING_BAB_COVERAGE)

        # 5. Build Conclusion Traces
        conclusion_units = [
            u for u in units if (u.research_role == ContentType.RESEARCH_CONCLUSION or u.content_type == ContentType.CONCLUSION)
        ]
        question_uids = {
            u.unit_id for u in units if (u.research_role == ContentType.RESEARCH_QUESTION or u.content_type == ContentType.QUESTION)
        }
        objective_uids = {
            u.unit_id for u in units if (u.research_role == ContentType.RESEARCH_OBJECTIVE or u.content_type == ContentType.OBJECTIVE)
        }
        finding_uids = {
            u.unit_id for u in units if (u.research_role in (ContentType.RESEARCH_FINDING, ContentType.RESEARCH_RESULT) or u.content_type in (ContentType.FINDING, ContentType.RESULT))
        }

        conclusion_traces: list[ConclusionTrace] = []
        for cu in conclusion_units:
            trace = ConclusionTrace(conclusion_unit_id=cu.unit_id)
            # Check relationships originating from or targeting this conclusion
            for r in relationships:
                if r.source_unit_id == cu.unit_id and r.relationship_type in (RelationshipType.ANSWERS, RelationshipType.ADDRESSES):
                    if r.target_unit_id in question_uids:
                        trace.answers_question_unit_id = r.target_unit_id
                    elif r.target_unit_id in objective_uids:
                        trace.achieves_objective_unit_id = r.target_unit_id
                elif (
                    r.relationship_type in (RelationshipType.CONCLUDES_FROM, RelationshipType.BASED_ON, RelationshipType.DERIVED_FROM)
                    and r.target_unit_id in finding_uids
                    and r.source_unit_id == cu.unit_id
                ):
                    trace.based_on_finding_unit_ids.append(r.target_unit_id)
                elif (
                    r.target_unit_id == cu.unit_id
                    and r.relationship_type in (RelationshipType.SUPPORTS, RelationshipType.PRODUCED_BY)
                    and r.source_unit_id in finding_uids
                ):
                    trace.based_on_finding_unit_ids.append(r.source_unit_id)

            # Check if conclusion is orphan
            if (
                not trace.answers_question_unit_id
                and not trace.achieves_objective_unit_id
                and not trace.based_on_finding_unit_ids
                and (question_uids or objective_uids)
                and TraceabilityWarning.CONCLUSION_WITHOUT_OBJECTIVE_TRACE not in warnings
            ):
                warnings.append(TraceabilityWarning.CONCLUSION_WITHOUT_OBJECTIVE_TRACE)

            conclusion_traces.append(trace)

        # 6. Build Recommendation Bases
        rec_units = [
            u for u in units if (u.research_role == ContentType.RESEARCH_RECOMMENDATION or u.content_type == ContentType.RECOMMENDATION)
        ]
        limitation_uids = {
            u.unit_id for u in units if (u.research_role == ContentType.RESEARCH_LIMITATION or u.content_type == ContentType.LIMITATION)
        }
        implication_uids = {
            u.unit_id for u in units if (u.research_role == ContentType.RESEARCH_IMPLICATION or u.content_type == ContentType.IMPLICATION)
        }

        recommendation_bases: list[RecommendationBasis] = []
        for ru in rec_units:
            basis = RecommendationBasis(recommendation_unit_id=ru.unit_id)
            for r in relationships:
                if r.source_unit_id == ru.unit_id:
                    if r.target_unit_id in finding_uids:
                        basis.based_on_finding_unit_ids.append(r.target_unit_id)
                    elif r.target_unit_id in limitation_uids:
                        basis.based_on_limitation_unit_ids.append(r.target_unit_id)
                    elif r.target_unit_id in implication_uids:
                        basis.based_on_implication_unit_ids.append(r.target_unit_id)
                elif r.target_unit_id == ru.unit_id:
                    if r.source_unit_id in limitation_uids:
                        basis.based_on_limitation_unit_ids.append(r.source_unit_id)
                    elif r.source_unit_id in finding_uids:
                        basis.based_on_finding_unit_ids.append(r.source_unit_id)

            basis.is_grounded = bool(
                basis.based_on_finding_unit_ids or basis.based_on_limitation_unit_ids or basis.based_on_implication_unit_ids
            )
            if not basis.is_grounded and (finding_uids or limitation_uids) and TraceabilityWarning.RECOMMENDATION_WITHOUT_BASIS not in warnings:
                warnings.append(TraceabilityWarning.RECOMMENDATION_WITHOUT_BASIS)

            recommendation_bases.append(basis)

        # 7. Check Data vs Interpretation integrity
        interp_uids = {
            u.unit_id
            for u in units
            if (
                u.research_role in (ContentType.RESEARCH_INTERPRETATION, ContentType.RESEARCH_DISCUSSION)
                or u.content_type in (ContentType.INTERPRETATION, ContentType.DISCUSSION)
            )
        }

        if finding_uids and not interp_uids and len(units) > 10 and TraceabilityWarning.FINDING_WITHOUT_INTERPRETATION not in warnings:
            warnings.append(TraceabilityWarning.FINDING_WITHOUT_INTERPRETATION)

        return ResearchTraceability(
            has_research_problem=has_problem,
            has_research_question=has_question,
            has_research_objective=has_objective,
            has_hypothesis=has_hypothesis,
            has_theoretical_foundation=has_theory,
            has_prior_research=has_prior,
            has_research_method=has_method,
            has_results=has_results,
            has_discussion=has_discussion,
            has_conclusion=has_conclusion,
            has_recommendation=has_recommendation,
            detected_bab_coverage=sorted_babs,
            missing_critical_components=missing,
            traceability_warnings=warnings,
            conclusion_traces=conclusion_traces,
            recommendation_bases=recommendation_bases,
        )
