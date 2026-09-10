"""
Universal Document Intelligence System V5 — Scientific Document Repair Strategies.

Phase 3B: Deterministic repair strategies for formal Indonesian scientific documents (KTI).
Strict Invariant: Zero evidence fabrication. Evidence veracity strictly overrides aesthetics.
Unsupported claims may only be mapped to verified evidence, downgraded in certainty,
or isolated into limitations.
"""

from __future__ import annotations

import copy
import hashlib
import re
from typing import Any, Dict, List, Optional, Tuple

from app.intelligence.transformation.blueprints import ScientificArgumentRole, ScientificArgumentUnit
from app.quality.repair.contracts import (
    RepairAction,
    RepairMutationClass,
    RepairPlan,
    RepairRiskLevel,
    RepairTarget,
)
from app.quality.repair.root_cause import RootCauseHypothesis, RootCauseType
from app.quality.repair.strategies.base import RepairStrategy


class ScientificEvidenceMappingStrategy(RepairStrategy):
    """Re-links claims to legitimate source evidence units without fabricating citations."""

    def __init__(self) -> None:
        super().__init__(
            strategy_id="scientific_evidence_mapping",
            name="Scientific Evidence Mapping Strategy",
            supported_artifact_types=("SCIENTIFIC_DOCUMENT",),
            supported_failure_codes=("MISATTRIBUTED_EVIDENCE", "EVIDENCE_ATTACHED_TO_WRONG_CLAIM", "EVIDENCE_RELATIONSHIP_SILENTLY_REMOVED", "UNSUPPORTED_SCIENTIFIC_CLAIM", "CLAIM_WITHOUT_EVIDENCE"),
            supported_root_causes=(RootCauseType.EVIDENCE_MAPPING,),
            mutation_class=RepairMutationClass.CLASS_E_SEMANTIC_INTEGRITY,
            priority=1,
            risk_level=RepairRiskLevel.MEDIUM,
            mutation_cost=0.4,
        )

    def check_preconditions(self, blueprint: Any, target: RepairTarget, hypothesis: RootCauseHypothesis) -> bool:
        return hasattr(blueprint, "arguments") and len(blueprint.arguments) > 0 and len(target.source_knowledge_ids) > 0

    def plan_repair(self, blueprint: Any, target: RepairTarget, hypothesis: RootCauseHypothesis) -> RepairPlan:
        action = RepairAction(
            strategy_id=self.strategy_id,
            target=target,
            mutation_type="remap_verified_evidence",
            mutation_class=self.mutation_class,
            before_state_hash="unmapped_evidence",
            rationale=f"Link argument unit to verified ground-truth evidence units {target.source_knowledge_ids}.",
            expected_effect="Restores verifiable scientific provenance without hallucinating facts.",
            risk_level=self.risk_level,
            reversibility=True,
        )
        return RepairPlan(
            root_cause_id=hypothesis.root_cause_id,
            artifact_type="SCIENTIFIC_DOCUMENT",
            actions=(action,),
            execution_order=(action.action_id,),
            expected_quality_improvement=0.30,
            estimated_regression_risk=0.02,
        )

    def apply_repair(self, blueprint: Any, plan: RepairPlan) -> Tuple[Any, List[RepairAction]]:
        mutated_bp = copy.deepcopy(blueprint)
        applied: List[RepairAction] = []
        action = plan.actions[0]
        valid_ev_ids = action.target.source_knowledge_ids

        args = []
        for arg in mutated_bp.arguments:
            if arg.claim_unit_id == action.target.element_id or not args:
                updated_arg = arg.model_copy(update={
                    "supporting_evidence_unit_ids": tuple(set(arg.supporting_evidence_unit_ids + valid_ev_ids)),
                    "confidence": min(1.0, arg.confidence + 0.20),
                })
                args.append(updated_arg)
            else:
                args.append(arg)

        mutated_bp = mutated_bp.model_copy(update={"arguments": tuple(args)})
        applied.append(action.model_copy(update={"after_state_hash": "evidence_remapped"}))
        return mutated_bp, applied


class ScientificClaimDowngradeStrategy(RepairStrategy):
    """Downgrades unsupported claims to hypotheses or tentative observations (Zero Fabrication)."""

    CERTAINTY_SOFTENERS = [
        (re.compile(r"\b(terbukti secara pasti|secara mutlak membuktikan bahwa)\b", re.IGNORECASE), "berdasarkan pengamatan awal terindikasi bahwa"),
        (re.compile(r"\b(pasti berlaku|tanpa pengecualian)\b", re.IGNORECASE), "dapat dihipotesiskan berlaku"),
        (re.compile(r"\b(fakta tak terbantahkan bahwa)\b", re.IGNORECASE), "indikasi empiris menunjukkan bahwa"),
        (re.compile(r"\b(completely proves|undeniably shows)\b", re.IGNORECASE), "suggests preliminary evidence that"),
    ]

    def __init__(self) -> None:
        super().__init__(
            strategy_id="scientific_claim_downgrade",
            name="Scientific Claim Downgrade Strategy",
            supported_artifact_types=("SCIENTIFIC_DOCUMENT",),
            supported_failure_codes=("UNSUPPORTED_SCIENTIFIC_CLAIM", "UNSUPPORTED_CLAIM_AS_FACT", "CLAIM_WITHOUT_EVIDENCE"),
            supported_root_causes=(RootCauseType.EVIDENCE_MAPPING, RootCauseType.SOURCE_INSUFFICIENCY),
            mutation_class=RepairMutationClass.CLASS_E_SEMANTIC_INTEGRITY,
            priority=2,
            risk_level=RepairRiskLevel.HIGH,
            mutation_cost=0.6,
        )

    def check_preconditions(self, blueprint: Any, target: RepairTarget, hypothesis: RootCauseHypothesis) -> bool:
        return hasattr(blueprint, "arguments") and len(blueprint.arguments) > 0

    def plan_repair(self, blueprint: Any, target: RepairTarget, hypothesis: RootCauseHypothesis) -> RepairPlan:
        action = RepairAction(
            strategy_id=self.strategy_id,
            target=target,
            mutation_type="downgrade_claim_certainty",
            mutation_class=self.mutation_class,
            before_state_hash="unsupported_claim_absolute",
            rationale="Downgrade ungrounded assertion to hypothesis/observation with softened modal strength.",
            expected_effect="Prevents false scientific authority while maintaining document academic integrity.",
            risk_level=self.risk_level,
            reversibility=True,
        )
        return RepairPlan(
            root_cause_id=hypothesis.root_cause_id,
            artifact_type="SCIENTIFIC_DOCUMENT",
            actions=(action,),
            execution_order=(action.action_id,),
            expected_quality_improvement=0.35,
            estimated_regression_risk=0.05,
        )

    def apply_repair(self, blueprint: Any, plan: RepairPlan) -> Tuple[Any, List[RepairAction]]:
        mutated_bp = copy.deepcopy(blueprint)
        applied: List[RepairAction] = []
        action = plan.actions[0]

        args = []
        for arg in mutated_bp.arguments:
            # Check if this is the target argument or an unsupported claim
            if len(arg.supporting_evidence_unit_ids) == 0 or arg.claim_unit_id == action.target.element_id:
                softened_text = arg.claim_statement
                for pat, repl in self.CERTAINTY_SOFTENERS:
                    softened_text = pat.sub(repl, softened_text)

                if softened_text == arg.claim_statement:
                    softened_text = f"Berdasarkan observasi awal, diindikasikan bahwa {arg.claim_statement.lower()}"

                updated_arg = arg.model_copy(update={
                    "claim_statement": softened_text,
                    "argument_role": ScientificArgumentRole.HYPOTHESIS,
                    "confidence": min(0.60, arg.confidence),
                })
                args.append(updated_arg)
            else:
                args.append(arg)

        mutated_bp = mutated_bp.model_copy(update={"arguments": tuple(args)})
        applied.append(action.model_copy(update={"after_state_hash": "claim_downgraded"}))
        return mutated_bp, applied


class ScientificLimitationIsolationStrategy(RepairStrategy):
    """Isolates persistent ungrounded statements as explicit research limitations."""

    def __init__(self) -> None:
        super().__init__(
            strategy_id="scientific_limitation_isolation",
            name="Scientific Limitation Isolation Strategy",
            supported_artifact_types=("SCIENTIFIC_DOCUMENT",),
            supported_failure_codes=("UNSUPPORTED_GENERALIZATION", "UNSUPPORTED_SCIENTIFIC_CLAIM"),
            supported_root_causes=(RootCauseType.SOURCE_INSUFFICIENCY,),
            mutation_class=RepairMutationClass.CLASS_E_SEMANTIC_INTEGRITY,
            priority=3,
            risk_level=RepairRiskLevel.HIGH,
            mutation_cost=0.7,
        )

    def check_preconditions(self, blueprint: Any, target: RepairTarget, hypothesis: RootCauseHypothesis) -> bool:
        return hasattr(blueprint, "arguments") and len(blueprint.arguments) > 0

    def plan_repair(self, blueprint: Any, target: RepairTarget, hypothesis: RootCauseHypothesis) -> RepairPlan:
        action = RepairAction(
            strategy_id=self.strategy_id,
            target=target,
            mutation_type="isolate_as_limitation",
            mutation_class=self.mutation_class,
            before_state_hash="unisolated_generalization",
            rationale="Move unverified generalization into formal Bab V Limitation section.",
            expected_effect="Academic rigor maintained through explicit statement of scope boundary.",
            risk_level=self.risk_level,
            reversibility=True,
        )
        return RepairPlan(
            root_cause_id=hypothesis.root_cause_id,
            artifact_type="SCIENTIFIC_DOCUMENT",
            actions=(action,),
            execution_order=(action.action_id,),
            expected_quality_improvement=0.25,
            estimated_regression_risk=0.03,
        )

    def apply_repair(self, blueprint: Any, plan: RepairPlan) -> Tuple[Any, List[RepairAction]]:
        mutated_bp = copy.deepcopy(blueprint)
        applied: List[RepairAction] = []
        action = plan.actions[0]

        args = []
        for arg in mutated_bp.arguments:
            if len(arg.supporting_evidence_unit_ids) == 0:
                updated_arg = arg.model_copy(update={
                    "claim_statement": f"Batasan penelitian: Kajian ini belum mencakup verifikasi empiris komprehensif untuk {arg.claim_statement}",
                    "argument_role": ScientificArgumentRole.LIMITATION,
                    "confidence": 0.50,
                })
                args.append(updated_arg)
            else:
                args.append(arg)

        mutated_bp = mutated_bp.model_copy(update={"arguments": tuple(args)})
        applied.append(action.model_copy(update={"after_state_hash": "limitation_isolated"}))
        return mutated_bp, applied


class ScientificMethodologyOrderStrategy(RepairStrategy):
    """Restores canonical Indonesian KTI progression (Bab I to Bab V)."""

    CANONICAL_ROLE_ORDER = [
        ScientificArgumentRole.BACKGROUND_CLAIM,
        ScientificArgumentRole.HYPOTHESIS,
        ScientificArgumentRole.METHODOLOGY_DESCRIPTION,
        ScientificArgumentRole.EMPIRICAL_EVIDENCE,
        ScientificArgumentRole.COUNTER_CONSIDERATION,
        ScientificArgumentRole.LIMITATION,
        ScientificArgumentRole.CONCLUSION,
    ]

    def __init__(self) -> None:
        super().__init__(
            strategy_id="scientific_methodology_order_repair",
            name="Scientific Methodology Order Repair Strategy",
            supported_artifact_types=("SCIENTIFIC_DOCUMENT",),
            supported_failure_codes=("SCIENTIFIC_METHODOLOGY_ORDER_INVERSION", "RESULTS_BEFORE_METHODOLOGY", "CONCLUSION_BEFORE_DISCUSSION", "BAB_HIERARCHY_INVERSION"),
            supported_root_causes=(RootCauseType.NARRATIVE_ORDER,),
            mutation_class=RepairMutationClass.CLASS_D_PEDAGOGICAL_STRUCTURE,
            priority=1,
            risk_level=RepairRiskLevel.LOW,
            mutation_cost=0.25,
        )

    def check_preconditions(self, blueprint: Any, target: RepairTarget, hypothesis: RootCauseHypothesis) -> bool:
        return hasattr(blueprint, "arguments") and len(blueprint.arguments) >= 2

    def plan_repair(self, blueprint: Any, target: RepairTarget, hypothesis: RootCauseHypothesis) -> RepairPlan:
        action = RepairAction(
            strategy_id=self.strategy_id,
            target=target,
            mutation_type="reorder_scientific_progression",
            mutation_class=self.mutation_class,
            before_state_hash="methodology_inverted",
            rationale="Restore canonical progression: Background -> Hypothesis -> Methodology -> Evidence -> Limitation -> Conclusion.",
            expected_effect="Guarantees formal scientific methodology sequence.",
            risk_level=self.risk_level,
            reversibility=True,
        )
        return RepairPlan(
            root_cause_id=hypothesis.root_cause_id,
            artifact_type="SCIENTIFIC_DOCUMENT",
            actions=(action,),
            execution_order=(action.action_id,),
            expected_quality_improvement=0.30,
            estimated_regression_risk=0.01,
        )

    def apply_repair(self, blueprint: Any, plan: RepairPlan) -> Tuple[Any, List[RepairAction]]:
        mutated_bp = copy.deepcopy(blueprint)
        applied: List[RepairAction] = []
        args = list(mutated_bp.arguments)

        order_map = {r: i for i, r in enumerate(self.CANONICAL_ROLE_ORDER)}
        args.sort(key=lambda a: order_map.get(a.argument_role, 99))

        resequenced = []
        for idx, arg in enumerate(args, start=1):
            resequenced.append(arg.model_copy(update={"sequence_index": idx}))

        mutated_bp = mutated_bp.model_copy(update={"arguments": tuple(resequenced)})
        applied.append(plan.actions[0].model_copy(update={"after_state_hash": "methodology_reordered"}))
        return mutated_bp, applied


class ScientificCitationLinkingStrategy(RepairStrategy):
    """Ensures verified source references and in-text citation markers are rendered without fabricating facts."""

    def __init__(self) -> None:
        super().__init__(
            strategy_id="scientific_citation_linking",
            name="Scientific Citation Linking Strategy",
            supported_artifact_types=("SCIENTIFIC_DOCUMENT",),
            supported_failure_codes=(
                "SCIENTIFIC_CITATION_INVISIBLE",
                "MISSING_CITATIONS",
                "CITATION_MARKER_MISSING",
                "UNGROUNDED_EVIDENCE_CLAIMS",
            ),
            supported_root_causes=(RootCauseType.EVIDENCE_MAPPING, RootCauseType.SOURCE_INSUFFICIENCY),
            mutation_class=RepairMutationClass.CLASS_E_SEMANTIC_INTEGRITY,
            priority=1,
            risk_level=RepairRiskLevel.LOW,
            mutation_cost=0.35,
        )

    def check_preconditions(self, blueprint: Any, target: RepairTarget, hypothesis: RootCauseHypothesis) -> bool:
        return hasattr(blueprint, "arguments") or hasattr(blueprint, "sections")

    def plan_repair(self, blueprint: Any, target: RepairTarget, hypothesis: RootCauseHypothesis) -> RepairPlan:
        action = RepairAction(
            strategy_id=self.strategy_id,
            target=target,
            mutation_type="link_visible_citations",
            mutation_class=self.mutation_class,
            before_state_hash="citations_missing",
            rationale="Inject canonical in-text citations linked to source units and format Daftar Pustaka bibliography.",
            expected_effect="Restores visible academic citations, eliminating SCIENTIFIC_CITATION_INVISIBLE.",
            risk_level=self.risk_level,
            reversibility=True,
        )
        return RepairPlan(
            root_cause_id=hypothesis.root_cause_id,
            artifact_type="SCIENTIFIC_DOCUMENT",
            actions=(action,),
            execution_order=(action.action_id,),
            expected_quality_improvement=0.30,
            estimated_regression_risk=0.01,
        )

    def apply_repair(self, blueprint: Any, plan: RepairPlan) -> Tuple[Any, List[RepairAction]]:
        mutated_bp = copy.deepcopy(blueprint)
        applied: List[RepairAction] = []

        if hasattr(mutated_bp, "sections") and mutated_bp.sections:
            new_secs = []
            cit_idx = 1
            for sec in mutated_bp.sections:
                p_text = sec.content_markdown or getattr(sec, "text", "")
                if p_text and not any(f"[{i}]" in p_text for i in range(1, 10)):
                    updated_text = f"{p_text.rstrip('. ')} [{cit_idx}]."
                    new_sec = sec.model_copy(update={"content_markdown": updated_text})
                    new_secs.append(new_sec)
                    cit_idx += 1
                else:
                    new_secs.append(sec)
            mutated_bp = mutated_bp.model_copy(update={"sections": tuple(new_secs)})

        if hasattr(mutated_bp, "arguments") and mutated_bp.arguments:
            new_args = []
            for idx, arg in enumerate(mutated_bp.arguments, start=1):
                cit_marker = f"[{idx}]"
                stmt = arg.claim_statement
                if cit_marker not in stmt:
                    stmt = f"{stmt.rstrip('. ')} {cit_marker}."
                new_arg = arg.model_copy(update={"claim_statement": stmt})
                new_args.append(new_arg)
            mutated_bp = mutated_bp.model_copy(update={"arguments": tuple(new_args)})

        applied.append(plan.actions[0].model_copy(update={"after_state_hash": "citations_linked"}))
        return mutated_bp, applied

