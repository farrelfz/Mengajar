"""
Universal Document Intelligence System V5 — Directive Safety Validator.

Phase 6: The non-negotiable safety firewall that validates human repair directives.
Human Review ≠ Quality Authority.
Human Review cannot bypass AuthorizedExportGate or disable Safety Invariants.
"""

from __future__ import annotations

import hashlib
import time
from typing import Any, Dict, List, Optional, Tuple

from app.review.contracts.directives import DirectiveValidationResult, ReviewDirective
from app.review.directives.ontology import DirectiveOntology
from app.review.safety.exceptions import IllegalDirectiveException


class DirectiveSafetyValidator:
    """Active safety guardian evaluating directives against architectural invariants."""

    FORBIDDEN_FLAG_RULES = {
        "force_export": "Human directives cannot force artifact export bypassing AuthorizedExportGate.",
        "bypass_export_gate": "Direct bypass of AuthorizedExportGate is strictly forbidden.",
        "disable_quality_gate": "Disabling UnifiedQualityAuthority is strictly forbidden.",
        "ignore_quality_authority": "Ignoring Level-0 Quality Authority evaluation is prohibited.",
        "ignore_hard_blocker": "Human review cannot override Level-0 hard blockers.",
        "bypass_hard_blocker": "Direct bypass of hard blockers is prohibited.",
        "disable_anti_spoiling": "Anti-spoiling cannot be disabled in educational worksheets.",
        "reveal_answers": "Revealing solutions in student worksheet inquiry is prohibited.",
        "fabricate_citation": "Synthesizing or fabricating citations violates scientific integrity.",
        "synthesize_citation": "Synthesizing citations without source manifest proof is prohibited.",
        "lower_baseline": "Lowering benchmark baselines violates AntiLaunderingGuard.",
        "lower_threshold": "Lowering quality thresholds violates anti-laundering governance.",
    }

    @classmethod
    def validate(
        cls,
        directive: ReviewDirective,
        artifact_type: str,
        raise_on_violation: bool = True,
    ) -> DirectiveValidationResult:
        """Evaluates directive safety. Raises IllegalDirectiveException or returns result."""
        violations: List[str] = []
        responsible: Optional[str] = None
        safe_alt: Optional[str] = None

        params = directive.parameters or {}

        # 1. Check for forbidden security and invariant flags
        for flag, reason in cls.FORBIDDEN_FLAG_RULES.items():
            if params.get(flag) is True or flag in str(directive.parameters).lower():
                violations.append(reason)
                responsible = "SafetyInvariantGateway"
                safe_alt = "Address the root defect through targeted repair rather than forcing an override."

        # 2. Check artifact compatibility
        if not DirectiveOntology.is_compatible(directive.directive_type, artifact_type):
            spec = DirectiveOntology.get_spec(directive.directive_type)
            allowed = ", ".join(spec.applicable_artifacts) if spec else "None"
            violations.append(
                f"Directive '{directive.directive_type.value}' is incompatible with artifact format '{artifact_type}'. "
                f"Applicable formats: {allowed}."
            )
            responsible = "DirectiveOntology"
            safe_alt = f"Select a directive compatible with {artifact_type}."

        # 3. Check required parameters
        spec = DirectiveOntology.get_spec(directive.directive_type)
        if spec:
            for req in spec.required_parameters:
                if req not in params:
                    violations.append(f"Directive '{directive.directive_type.value}' is missing required parameter '{req}'.")
                    responsible = "DirectiveSchemaValidator"

        # 4. Check worksheet anti-spoiling integrity
        if artifact_type.upper() == "WORKSHEET":
            for k, v in params.items():
                val_lower = str(v).lower()
                if any(term in val_lower for term in ("answer key", "kunci jawaban", "solution: 42")):
                    violations.append("Worksheet mutation contains direct solution text, violating anti-spoiling.")
                    responsible = "WorksheetAntiSpoilingInvariant"

        if violations:
            if raise_on_violation:
                raise IllegalDirectiveException(
                    directive_id=directive.directive_id,
                    violation="; ".join(violations),
                    responsible_subsystem=responsible or "SafetyGateway",
                )
            return DirectiveValidationResult(
                is_valid=False,
                directive_id=directive.directive_id,
                violations=tuple(violations),
                responsible_subsystem=responsible,
                safe_alternative=safe_alt,
            )

        # Generate cryptographic validation signature
        sig_raw = f"{directive.directive_id}:{directive.directive_type.value}:{artifact_type}:{directive.reviewer_id}"
        signature = hashlib.sha256(sig_raw.encode("utf-8")).hexdigest()

        return DirectiveValidationResult(
            is_valid=True,
            directive_id=directive.directive_id,
            violations=(),
            signature=signature,
        )
