"""
Personalization Trace and Explainability Auditing.
"""

from __future__ import annotations

import json
from typing import Any
from app.personalization.contracts import PersonalizationReport, PersonalizationTrace


class PersonalizationTraceAuditor:
    """Provides machine-readable serialization and forensic inspection of personalization decisions."""

    @classmethod
    def serialize_trace(cls, report: PersonalizationReport) -> dict[str, Any]:
        return {
            "profile_id": report.learner_profile.profile_id,
            "knowledge_level": report.learner_profile.knowledge_level.value,
            "policy": report.adaptation_policy.value,
            "target_complexity": report.adaptation_plan.target_complexity_level,
            "sequence_strategy": report.adaptation_plan.sequence_strategy,
            "scaffolding": report.adaptation_plan.scaffolding_strategy.value,
            "density_modifier": report.adaptation_plan.density_modifier,
            "decisions_count": len(report.trace.decisions),
            "decisions": [d.model_dump() for d in report.trace.decisions],
            "constraints": report.trace.constraints_enforced,
        }
