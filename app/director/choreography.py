"""
Pedagogical Choreography Engine.

Transforms an abstract LearningJourney into ordered, typed CapabilityRequirements
specifying taxonomy constraints (intent, role, family, visual grammar, density) for Resolver V2.
"""

from __future__ import annotations

from typing import Any

from app.capabilities.taxonomy import (
    CapabilityFamily,
    DensityProfile,
    PedagogicalRole,
    SemanticIntent,
    VisualGrammar,
)
from app.director.contracts import (
    CapabilityRequirement,
    DensityBudget,
    LearningJourney,
    LearningStage,
    LearningStageType,
)


STAGE_TAXONOMY_MAP: dict[LearningStageType, dict[str, Any]] = {
    LearningStageType.HOOK: {
        "intent": SemanticIntent.HOOK,
        "role": PedagogicalRole.HOOK,
        "family": CapabilityFamily.TITLE_FRAMING,
        "grammar": VisualGrammar.HERO,
        "density": DensityProfile.MINIMAL,
        "fallback_intents": [SemanticIntent.INTRODUCE],
    },
    LearningStageType.SURFACE_INTUITION: {
        "intent": SemanticIntent.EXPLAIN,
        "role": PedagogicalRole.EXPLANATION,
        "family": CapabilityFamily.CONCEPT_STRUCTURE,
        "grammar": VisualGrammar.CONCEPT_PANEL,
        "density": DensityProfile.MINIMAL,
        "fallback_intents": [SemanticIntent.INTRODUCE],
    },
    LearningStageType.MISCONCEPTION: {
        "intent": SemanticIntent.COMPARE,
        "role": PedagogicalRole.MISCONCEPTION,
        "family": CapabilityFamily.COMPARATIVE_REASONING,
        "grammar": VisualGrammar.COMPARISON,
        "density": DensityProfile.FOCUSED,
        "fallback_intents": [SemanticIntent.EVALUATE],
    },
    LearningStageType.CONCEPTUAL_CONFLICT: {
        "intent": SemanticIntent.COMPARE,
        "role": PedagogicalRole.ANALYSIS,
        "family": CapabilityFamily.COMPARATIVE_REASONING,
        "grammar": VisualGrammar.COMPARISON,
        "density": DensityProfile.FOCUSED,
        "fallback_intents": [SemanticIntent.ARGUE],
    },
    LearningStageType.CONCRETE_EXPERIENCE: {
        "intent": SemanticIntent.EXPLAIN,
        "role": PedagogicalRole.EXPLANATION,
        "family": CapabilityFamily.PROCESS_VISUALIZATION,
        "grammar": VisualGrammar.PROCESS_FLOW,
        "density": DensityProfile.FOCUSED,
        "fallback_intents": [SemanticIntent.SEQUENCE],
    },
    LearningStageType.CONCEPT_FORMALIZATION: {
        "intent": SemanticIntent.SEQUENCE,
        "role": PedagogicalRole.EXPLANATION,
        "family": CapabilityFamily.PROCESS_VISUALIZATION,
        "grammar": VisualGrammar.PROCESS_FLOW,
        "density": DensityProfile.FOCUSED,
        "fallback_intents": [SemanticIntent.EXPLAIN, SemanticIntent.CLASSIFY],
    },
    LearningStageType.REPRESENTATION: {
        "intent": SemanticIntent.EXPLAIN,
        "role": PedagogicalRole.EXPLANATION,
        "family": CapabilityFamily.PROCESS_VISUALIZATION,
        "grammar": VisualGrammar.PROCESS_FLOW,
        "density": DensityProfile.FOCUSED,
        "fallback_intents": [SemanticIntent.RELATE],
    },
    LearningStageType.MATHEMATICAL_DERIVATION: {
        "intent": SemanticIntent.DERIVE,
        "role": PedagogicalRole.EXPLANATION,
        "family": CapabilityFamily.QUANTITATIVE_ANALYSIS,
        "grammar": VisualGrammar.EQUATION_CHAIN,
        "density": DensityProfile.ANALYTICAL,
        "fallback_intents": [SemanticIntent.EXPLAIN],
    },
    LearningStageType.WORKED_EXAMPLE: {
        "intent": SemanticIntent.DERIVE,
        "role": PedagogicalRole.EXPLANATION,
        "family": CapabilityFamily.STEPWISE_REASONING,
        "grammar": VisualGrammar.EQUATION_CHAIN,
        "density": DensityProfile.FOCUSED,
        "fallback_intents": [SemanticIntent.EXPLAIN],
    },
    LearningStageType.GUIDED_PRACTICE: {
        "intent": SemanticIntent.INVESTIGATE,
        "role": PedagogicalRole.SCAFFOLD,
        "family": CapabilityFamily.STEPWISE_REASONING,
        "grammar": VisualGrammar.CHECKPOINT_CARD,
        "density": DensityProfile.FOCUSED,
        "fallback_intents": [SemanticIntent.ASSESS],
    },
    LearningStageType.INDEPENDENT_PRACTICE: {
        "intent": SemanticIntent.INVESTIGATE,
        "role": PedagogicalRole.PRACTICE,
        "family": CapabilityFamily.STEPWISE_REASONING,
        "grammar": VisualGrammar.CHECKPOINT_CARD,
        "density": DensityProfile.FOCUSED,
        "fallback_intents": [SemanticIntent.ASSESS],
    },
    LearningStageType.CHALLENGE: {
        "intent": SemanticIntent.SYNTHESIZE,
        "role": PedagogicalRole.ASSESSMENT,
        "family": CapabilityFamily.CONCEPT_STRUCTURE,
        "grammar": VisualGrammar.CHECKPOINT_CARD,
        "density": DensityProfile.ANALYTICAL,
        "fallback_intents": [SemanticIntent.INVESTIGATE],
    },
    LearningStageType.REFLECTION: {
        "intent": SemanticIntent.ASSESS,
        "role": PedagogicalRole.ASSESSMENT,
        "family": CapabilityFamily.CONCEPT_STRUCTURE,
        "grammar": VisualGrammar.CHECKPOINT_CARD,
        "density": DensityProfile.MINIMAL,
        "fallback_intents": [SemanticIntent.SYNTHESIZE],
    },
    LearningStageType.SUMMARY: {
        "intent": SemanticIntent.SYNTHESIZE,
        "role": PedagogicalRole.SYNTHESIS,
        "family": CapabilityFamily.CONCEPT_STRUCTURE,
        "grammar": VisualGrammar.CONCEPT_PANEL,
        "density": DensityProfile.MINIMAL,
        "fallback_intents": [SemanticIntent.INTRODUCE],
    },
    LearningStageType.CONTEXT: {
        "intent": SemanticIntent.INTRODUCE,
        "role": PedagogicalRole.INTRODUCTION,
        "family": CapabilityFamily.CONCEPT_STRUCTURE,
        "grammar": VisualGrammar.CONCEPT_PANEL,
        "density": DensityProfile.MINIMAL,
        "fallback_intents": [SemanticIntent.HOOK],
    },
    LearningStageType.PROBLEM_STATEMENT: {
        "intent": SemanticIntent.NARROW_SCOPE,
        "role": PedagogicalRole.SCAFFOLD,
        "family": CapabilityFamily.CONCEPT_STRUCTURE,
        "grammar": VisualGrammar.CONCEPT_MAP,
        "density": DensityProfile.FOCUSED,
        "fallback_intents": [SemanticIntent.ARGUE],
    },
    LearningStageType.RESEARCH_GAP: {
        "intent": SemanticIntent.COMPARE,
        "role": PedagogicalRole.ANALYSIS,
        "family": CapabilityFamily.COMPARATIVE_REASONING,
        "grammar": VisualGrammar.COMPARISON,
        "density": DensityProfile.FOCUSED,
        "fallback_intents": [SemanticIntent.EVALUATE],
    },
    LearningStageType.VARIABLE_MAPPING: {
        "intent": SemanticIntent.RELATE,
        "role": PedagogicalRole.ANALYSIS,
        "family": CapabilityFamily.RELATIONSHIP_MAPPING,
        "grammar": VisualGrammar.ANNOTATED_DIAGRAM,
        "density": DensityProfile.ANALYTICAL,
        "fallback_intents": [SemanticIntent.EXPLAIN],
    },
    LearningStageType.HYPOTHESIS: {
        "intent": SemanticIntent.ARGUE,
        "role": PedagogicalRole.EXPLANATION,
        "family": CapabilityFamily.EVIDENCE_ANALYSIS,
        "grammar": VisualGrammar.REASONING_FLOW,
        "density": DensityProfile.FOCUSED,
        "fallback_intents": [SemanticIntent.COMPARE],
    },
    LearningStageType.METHODOLOGY: {
        "intent": SemanticIntent.EXPLAIN,
        "role": PedagogicalRole.REFERENCE,
        "family": CapabilityFamily.QUANTITATIVE_ANALYSIS,
        "grammar": VisualGrammar.TABLE,
        "density": DensityProfile.DENSE_REFERENCE,
        "fallback_intents": [SemanticIntent.SEQUENCE],
    },
    LearningStageType.EVIDENCE_ANALYSIS: {
        "intent": SemanticIntent.ARGUE,
        "role": PedagogicalRole.SYNTHESIS,
        "family": CapabilityFamily.EVIDENCE_ANALYSIS,
        "grammar": VisualGrammar.REASONING_FLOW,
        "density": DensityProfile.ANALYTICAL,
        "fallback_intents": [SemanticIntent.EVALUATE],
    },
    LearningStageType.SYNTHESIS: {
        "intent": SemanticIntent.SYNTHESIZE,
        "role": PedagogicalRole.SYNTHESIS,
        "family": CapabilityFamily.CONCEPT_STRUCTURE,
        "grammar": VisualGrammar.CONCEPT_PANEL,
        "density": DensityProfile.FOCUSED,
        "fallback_intents": [SemanticIntent.EXPLAIN],
    },
    LearningStageType.CALL_TO_ACTION: {
        "intent": SemanticIntent.SYNTHESIZE,
        "role": PedagogicalRole.SYNTHESIS,
        "family": CapabilityFamily.CONCEPT_STRUCTURE,
        "grammar": VisualGrammar.HERO,
        "density": DensityProfile.MINIMAL,
        "fallback_intents": [SemanticIntent.HOOK],
    },
}


class PedagogicalChoreographer:
    """Translates high-level LearningJourneys into typed, resolvable CapabilityRequirements."""

    def choreograph(
        self,
        journey: LearningJourney,
        density_budget: DensityBudget | None = None,
    ) -> list[CapabilityRequirement]:
        """Convert all stages in the journey to CapabilityRequirements."""
        requirements: list[CapabilityRequirement] = []
        budget = density_budget or DensityBudget()

        for stage in journey.stages:
            req = self.choreograph_stage(stage, budget)
            requirements.append(req)

        return requirements

    def choreograph_stage(
        self,
        stage: LearningStage,
        budget: DensityBudget,
    ) -> CapabilityRequirement:
        """Create a single CapabilityRequirement from a LearningStage."""
        mapping = STAGE_TAXONOMY_MAP.get(
            stage.stage_type,
            {
                "intent": SemanticIntent.EXPLAIN,
                "role": PedagogicalRole.EXPLANATION,
                "family": CapabilityFamily.CONCEPT_STRUCTURE,
                "grammar": VisualGrammar.CONCEPT_PANEL,
                "density": budget.preferred_density_profile,
                "fallback_intents": [],
            },
        )

        return CapabilityRequirement(
            stage_type=stage.stage_type,
            primary_intent=mapping["intent"],
            pedagogical_role=mapping["role"],
            preferred_family=mapping.get("family"),
            preferred_visual_grammar=mapping.get("grammar"),
            density=mapping.get("density", budget.preferred_density_profile),
            candidate_tags=list(stage.target_concepts),
            fallback_intents=mapping.get("fallback_intents", []),
            stage_title=stage.title,
            stage_content=stage.purpose,
        )
