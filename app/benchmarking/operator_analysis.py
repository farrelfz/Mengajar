"""
Universal Document Intelligence System V5 — Operator Applicability Envelope & Evidence Analyzer.

Phase 4.1: Evaluates empirical evidence strength for each repair operator, builds
applicability envelopes, and prevents overclaiming generalization based on sparse successes.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple

from app.benchmarking.contracts import (
    BenchmarkExecutionOutcome,
    OperatorApplicabilityEnvelope,
)
from app.benchmarking.taxonomy import CorpusCategory, CorpusSplit, EvidenceStrength

logger = logging.getLogger("benchmarking.operator_analysis")


class OperatorEvidenceAnalyzer:
    """Analyzes execution outcomes across the corpus to synthesize evidence-backed envelopes."""

    @classmethod
    def evaluate_operators(
        cls,
        outcomes: Sequence[BenchmarkExecutionOutcome],
    ) -> Dict[str, OperatorApplicabilityEnvelope]:
        """Aggregates per-operator evidence across all benchmark jobs."""
        operator_fixtures: Dict[str, Set[str]] = {}
        operator_artifacts: Dict[str, Set[str]] = {}
        operator_unseen_attempts: Dict[str, int] = {}
        operator_unseen_successes: Dict[str, int] = {}
        operator_regressions: Dict[str, int] = {}
        operator_total_commits: Dict[str, int] = {}
        operator_signatures: Dict[str, Set[str]] = {}

        for o in outcomes:
            all_ops = set(o.operators_attempted) | set(o.operators_committed)
            for op in all_ops:
                operator_fixtures.setdefault(op, set()).add(o.fixture_id)
                operator_artifacts.setdefault(op, set()).add(o.artifact_type)
                operator_signatures.setdefault(op, set()).add(f"{o.corpus_category.value}:{o.artifact_type}")

            for op in o.operators_committed:
                operator_total_commits[op] = operator_total_commits.get(op, 0) + 1
                if o.split == CorpusSplit.UNSEEN_GENERALIZATION:
                    operator_unseen_successes[op] = operator_unseen_successes.get(op, 0) + 1

            for op in o.operators_attempted:
                if o.split == CorpusSplit.UNSEEN_GENERALIZATION:
                    operator_unseen_attempts[op] = operator_unseen_attempts.get(op, 0) + 1

            for op in o.operators_rolled_back:
                operator_regressions[op] = operator_regressions.get(op, 0) + 1

        envelopes: Dict[str, OperatorApplicabilityEnvelope] = {}

        # Canonical known root causes per operator (grounded in architecture)
        CANONICAL_ROOT_CAUSES: Dict[str, Tuple[str, ...]] = {
            "presentation_component_reflow": ("ELEMENT_COLLISION", "BOUNDING_BOX_OVERFLOW"),
            "presentation_formula_recomposition": ("FORMULA_CONTAINMENT", "OVERFLOW_HORIZONTAL"),
            "presentation_composition_actuator": ("ELEMENT_COLLISION", "LAYOUT_OVERCROWDING"),
            "presentation_slide_split_actuator": ("ELEMENT_COLLISION", "CARD_OVERLOAD", "PAGE_OVERFLOW"),
            "presentation_diversity_actuator": ("LAYOUT_MONOTONY", "TEMPLATE_REPETITION"),
            "worksheet_inquiry_recomposition": ("INQUIRY_STRUCTURE", "REPETITION_STREAK", "LAYOUT_MONOTONY"),
            "typography_constraint_actuator": ("TEXT_TOO_SMALL", "OVERFLOW_VERTICAL", "LINE_BUDGET_OVERRUN"),
            "scientific_citation_visibility": ("SCIENTIFIC_CITATION_INVISIBLE", "MISSING_BIBLIOGRAPHY"),
            "scientific_evidence_layout": ("UNSUPPORTED_CLAIM", "EVIDENCE_DISCONNECT"),
            "handout_density_reflow": ("CONTENT_DENSITY", "LINE_BUDGET_OVERRUN"),
            "handout_section_balance": ("LAYOUT_MONOTONY", "ASYMMETRIC_WHITESPACE"),
        }

        # Canonical supported artifacts per operator
        CANONICAL_ARTIFACTS: Dict[str, Tuple[str, ...]] = {
            "presentation_component_reflow": ("PRESENTATION",),
            "presentation_formula_recomposition": ("PRESENTATION",),
            "presentation_composition_actuator": ("PRESENTATION",),
            "presentation_slide_split_actuator": ("PRESENTATION",),
            "presentation_diversity_actuator": ("PRESENTATION",),
            "worksheet_inquiry_recomposition": ("WORKSHEET",),
            "typography_constraint_actuator": ("PRESENTATION", "WORKSHEET", "HANDOUT", "SCIENTIFIC_DOCUMENT"),
            "scientific_citation_visibility": ("SCIENTIFIC_DOCUMENT",),
            "scientific_evidence_layout": ("SCIENTIFIC_DOCUMENT",),
            "handout_density_reflow": ("HANDOUT",),
            "handout_section_balance": ("HANDOUT",),
        }

        all_operator_ids = set(CANONICAL_ROOT_CAUSES.keys()) | set(operator_fixtures.keys())

        for op_id in sorted(all_operator_ids):
            fixtures = operator_fixtures.get(op_id, set())
            artifacts = operator_artifacts.get(op_id, set())
            signatures = operator_signatures.get(op_id, set())
            unseen_att = operator_unseen_attempts.get(op_id, 0)
            unseen_succ = operator_unseen_successes.get(op_id, 0)
            regressions = operator_regressions.get(op_id, 0)
            commits = operator_total_commits.get(op_id, 0)

            unseen_rate = unseen_succ / max(1, unseen_att) if unseen_att > 0 else (1.0 if commits > 0 else 0.0)
            reg_rate = regressions / max(1, (commits + regressions))

            # Determine Evidence Strength
            if len(fixtures) < 3 or commits < 2:
                strength = EvidenceStrength.INSUFFICIENT
            elif regressions == 0 and unseen_succ >= 2 and len(fixtures) >= 6 and len(signatures) >= 2:
                strength = EvidenceStrength.STRONG
            elif len(fixtures) >= 5 and len(signatures) >= 2:
                strength = EvidenceStrength.MODERATE
            else:
                strength = EvidenceStrength.LIMITED

            supported_arts = CANONICAL_ARTIFACTS.get(op_id, tuple(artifacts))
            supported_rcs = CANONICAL_ROOT_CAUSES.get(op_id, ("UNKNOWN",))

            # Unsupported signatures derived by exclusion
            all_known_cats = {"CONCEPT_HEAVY", "EXPERIMENT_HEAVY", "NARRATIVE_HEAVY", "SCIENTIFIC_HEAVY", "PATHOLOGICAL"}
            valid_cats = {s.split(":")[0] for s in signatures if ":" in s}
            unsupported = tuple(sorted(all_known_cats - valid_cats)) if valid_cats else ("PATHOLOGICAL",)

            envelopes[op_id] = OperatorApplicabilityEnvelope(
                operator_id=op_id,
                supported_artifact_types=supported_arts,
                supported_root_causes=supported_rcs,
                validated_structural_signatures=tuple(sorted(signatures)),
                unsupported_signatures=unsupported,
                evidence_strength=strength,
                unseen_success_rate=round(unseen_rate, 4),
                regression_rate=round(reg_rate, 4),
                fixture_diversity_count=len(fixtures),
                notes=f"Validated across {len(fixtures)} fixtures and {len(signatures)} distinct structural signatures."
            )

        return envelopes
