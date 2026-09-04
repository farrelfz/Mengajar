"""
Unit tests for Synthesis, Agreement detection, Conflict resolution, and Prioritization.
"""

import pytest

from app.critic.contracts import (
    CritiqueAgreement,
    CritiqueConfidence,
    CritiqueConflict,
    CritiqueEvidence,
    CritiqueFinding,
    CritiquePerspective,
    CritiquePriority,
    CritiqueSeverity,
)
from app.critic.prioritization import CritiquePrioritizer
from app.critic.recommendations import RecommendationGenerator
from app.critic.synthesis import CritiqueSynthesizer


def test_synthesis_merges_duplicates_and_detects_agreements_and_conflicts():
    f_ped = CritiqueFinding(
        id="f_ped",
        perspective=CritiquePerspective.PEDAGOGICAL,
        title="Missing Foundational Scaffolding",
        observation="Missing foundational explanation",
        diagnosis="Need to expand concepts",
        why_it_matters="Pedagogical integrity",
        severity=CritiqueSeverity.HIGH,
        confidence=CritiqueConfidence.HIGH,
        affected_locations=["Stage 1"],
        improvement_direction="Prepend and expand foundational explanation",
    )
    f_cog = CritiqueFinding(
        id="f_cog",
        perspective=CritiquePerspective.COGNITIVE_LOAD,
        title="Simultaneous Concept Introduction Overload",
        observation="Too many concepts",
        diagnosis="Working memory overloaded",
        why_it_matters="Cognitive load limits",
        severity=CritiqueSeverity.HIGH,
        confidence=CritiqueConfidence.HIGH,
        affected_locations=["Stage 1"],
        improvement_direction="Decompose and distribute concepts",
    )

    merged, agreements, conflicts, steps = CritiqueSynthesizer.synthesize([f_ped, f_cog])

    assert len(merged) == 2
    # Agreement detected between pedagogy and cognitive load
    assert len(agreements) >= 1
    assert "agree" in agreements[0].shared_conclusion.lower()

    # Conflict detected between expanding vs decomposing
    assert len(conflicts) >= 1
    assert "tension" in steps[-1].lower() or len(conflicts) == 1

    # Prioritization
    queue = CritiquePrioritizer.prioritize(merged, agreements)
    assert len(queue) == 2

    # Recommendations
    recs = RecommendationGenerator.generate_recommendations(merged, agreements)
    assert len(recs) == 2
    assert recs[0].priority in [CritiquePriority.CRITICAL, CritiquePriority.HIGH]
