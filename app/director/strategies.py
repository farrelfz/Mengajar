"""
Material Strategy Library.

Defines the 12 canonical pedagogical and rhetorical strategy profiles,
specifying stage sequences, cognitive trajectories, family recommendations, and forbidden orderings.
"""

from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field

from app.capabilities.taxonomy import CapabilityFamily, DensityProfile
from app.director.contracts import CognitiveLevel, LearningStageType, MaterialStrategyType


class MaterialStrategyDefinition(BaseModel):
    """Configuration profile for a canonical material strategy."""
    strategy_type: MaterialStrategyType
    display_name: str
    description: str
    preferred_stages: list[LearningStageType] = Field(default_factory=list)
    forbidden_orderings: list[tuple[LearningStageType, LearningStageType]] = Field(default_factory=list)
    recommended_families: list[CapabilityFamily] = Field(default_factory=list)
    default_density: DensityProfile = DensityProfile.FOCUSED
    suitable_formats: list[str] = Field(default_factory=list)
    cognitive_trajectory: list[CognitiveLevel] = Field(default_factory=list)


STRATEGY_REGISTRY: dict[MaterialStrategyType, MaterialStrategyDefinition] = {
    MaterialStrategyType.CONCRETE_TO_ABSTRACT: MaterialStrategyDefinition(
        strategy_type=MaterialStrategyType.CONCRETE_TO_ABSTRACT,
        display_name="Concrete to Abstract Formalization",
        description="Grounds understanding in tangible physical intuition before introducing mathematical models",
        preferred_stages=[
            LearningStageType.HOOK,
            LearningStageType.SURFACE_INTUITION,
            LearningStageType.CONCRETE_EXPERIENCE,
            LearningStageType.REPRESENTATION,
            LearningStageType.CONCEPT_FORMALIZATION,
            LearningStageType.WORKED_EXAMPLE,
            LearningStageType.GUIDED_PRACTICE,
            LearningStageType.SUMMARY,
        ],
        forbidden_orderings=[
            (LearningStageType.MATHEMATICAL_DERIVATION, LearningStageType.CONCRETE_EXPERIENCE),
            (LearningStageType.SUMMARY, LearningStageType.HOOK),
        ],
        recommended_families=[
            CapabilityFamily.PROCESS_VISUALIZATION,
            CapabilityFamily.COMPARATIVE_REASONING,
            CapabilityFamily.STEPWISE_REASONING,
        ],
        default_density=DensityProfile.FOCUSED,
        suitable_formats=["a4_portrait", "presentation_16_9", "a4_landscape"],
        cognitive_trajectory=[
            CognitiveLevel.RECOGNIZE,
            CognitiveLevel.UNDERSTAND,
            CognitiveLevel.APPLY,
        ],
    ),
    MaterialStrategyType.MISCONCEPTION_CORRECTION: MaterialStrategyDefinition(
        strategy_type=MaterialStrategyType.MISCONCEPTION_CORRECTION,
        display_name="Misconception Elicitation & Correction",
        description="Surfaces intuitive fallacies, creates cognitive conflict, and provides principled scientific correction",
        preferred_stages=[
            LearningStageType.HOOK,
            LearningStageType.SURFACE_INTUITION,
            LearningStageType.MISCONCEPTION,
            LearningStageType.CONCEPTUAL_CONFLICT,
            LearningStageType.CONCEPT_FORMALIZATION,
            LearningStageType.WORKED_EXAMPLE,
            LearningStageType.GUIDED_PRACTICE,
            LearningStageType.REFLECTION,
        ],
        forbidden_orderings=[
            (LearningStageType.CONCEPT_FORMALIZATION, LearningStageType.MISCONCEPTION),
            (LearningStageType.SUMMARY, LearningStageType.HOOK),
        ],
        recommended_families=[
            CapabilityFamily.COMPARATIVE_REASONING,
            CapabilityFamily.EVIDENCE_ANALYSIS,
            CapabilityFamily.STEPWISE_REASONING,
        ],
        default_density=DensityProfile.FOCUSED,
        suitable_formats=["a4_portrait", "presentation_16_9", "a4_landscape"],
        cognitive_trajectory=[
            CognitiveLevel.RECOGNIZE,
            CognitiveLevel.ANALYZE,
            CognitiveLevel.EVALUATE,
        ],
    ),
    MaterialStrategyType.CONCEPTUAL_DISCOVERY: MaterialStrategyDefinition(
        strategy_type=MaterialStrategyType.CONCEPTUAL_DISCOVERY,
        display_name="Guided Conceptual Discovery",
        description="Encourages inductive discovery through observation, pattern recognition, and conceptual synthesis",
        preferred_stages=[
            LearningStageType.HOOK,
            LearningStageType.CONCRETE_EXPERIENCE,
            LearningStageType.REPRESENTATION,
            LearningStageType.CONCEPT_FORMALIZATION,
            LearningStageType.CHALLENGE,
            LearningStageType.REFLECTION,
        ],
        forbidden_orderings=[
            (LearningStageType.CONCEPT_FORMALIZATION, LearningStageType.CONCRETE_EXPERIENCE),
        ],
        recommended_families=[
            CapabilityFamily.CONCEPT_STRUCTURE,
            CapabilityFamily.PROCESS_VISUALIZATION,
        ],
        default_density=DensityProfile.FOCUSED,
        suitable_formats=["presentation_16_9", "a4_landscape"],
        cognitive_trajectory=[
            CognitiveLevel.UNDERSTAND,
            CognitiveLevel.ANALYZE,
            CognitiveLevel.CREATE,
        ],
    ),
    MaterialStrategyType.WORKED_EXAMPLE_PROGRESSIVE: MaterialStrategyDefinition(
        strategy_type=MaterialStrategyType.WORKED_EXAMPLE_PROGRESSIVE,
        display_name="Scaffolded Worked Example to Mastery",
        description="Direct instruction starting with an expert model, fading scaffolding into independent mastery",
        preferred_stages=[
            LearningStageType.CONTEXT,
            LearningStageType.CONCEPT_FORMALIZATION,
            LearningStageType.WORKED_EXAMPLE,
            LearningStageType.GUIDED_PRACTICE,
            LearningStageType.INDEPENDENT_PRACTICE,
            LearningStageType.CHALLENGE,
            LearningStageType.SUMMARY,
        ],
        forbidden_orderings=[
            (LearningStageType.INDEPENDENT_PRACTICE, LearningStageType.WORKED_EXAMPLE),
            (LearningStageType.CHALLENGE, LearningStageType.CONCEPT_FORMALIZATION),
        ],
        recommended_families=[
            CapabilityFamily.STEPWISE_REASONING,
            CapabilityFamily.QUANTITATIVE_ANALYSIS,
        ],
        default_density=DensityProfile.FOCUSED,
        suitable_formats=["a4_portrait", "worksheet"],
        cognitive_trajectory=[
            CognitiveLevel.UNDERSTAND,
            CognitiveLevel.APPLY,
            CognitiveLevel.ANALYZE,
        ],
    ),
    MaterialStrategyType.RESEARCH_METHOD_TUTORIAL: MaterialStrategyDefinition(
        strategy_type=MaterialStrategyType.RESEARCH_METHOD_TUTORIAL,
        display_name="Research Methodology & Problem Formulation",
        description="Guides researchers from broad domain challenges down to operational empirical designs",
        preferred_stages=[
            LearningStageType.CONTEXT,
            LearningStageType.PROBLEM_STATEMENT,
            LearningStageType.RESEARCH_GAP,
            LearningStageType.VARIABLE_MAPPING,
            LearningStageType.HYPOTHESIS,
            LearningStageType.METHODOLOGY,
            LearningStageType.SYNTHESIS,
        ],
        forbidden_orderings=[
            (LearningStageType.METHODOLOGY, LearningStageType.PROBLEM_STATEMENT),
            (LearningStageType.HYPOTHESIS, LearningStageType.CONTEXT),
        ],
        recommended_families=[
            CapabilityFamily.CONCEPT_STRUCTURE,
            CapabilityFamily.COMPARATIVE_REASONING,
            CapabilityFamily.RELATIONSHIP_MAPPING,
            CapabilityFamily.PROCESS_VISUALIZATION,
        ],
        default_density=DensityProfile.ANALYTICAL,
        suitable_formats=["a4_portrait", "a4_landscape"],
        cognitive_trajectory=[
            CognitiveLevel.ANALYZE,
            CognitiveLevel.EVALUATE,
            CognitiveLevel.CREATE,
        ],
    ),
    MaterialStrategyType.ARGUMENTATION_BUILDING: MaterialStrategyDefinition(
        strategy_type=MaterialStrategyType.ARGUMENTATION_BUILDING,
        display_name="Scholarly Argumentation & Essay Logic",
        description="Develops persuasive thesis structures, counterargument refutations, and paragraph coherence",
        preferred_stages=[
            LearningStageType.CONTEXT,
            LearningStageType.PROBLEM_STATEMENT,
            LearningStageType.REPRESENTATION,
            LearningStageType.EVIDENCE_ANALYSIS,
            LearningStageType.CHALLENGE,
            LearningStageType.SYNTHESIS,
            LearningStageType.CALL_TO_ACTION,
        ],
        forbidden_orderings=[
            (LearningStageType.CALL_TO_ACTION, LearningStageType.CONTEXT),
        ],
        recommended_families=[
            CapabilityFamily.EVIDENCE_ANALYSIS,
            CapabilityFamily.COMPARATIVE_REASONING,
            CapabilityFamily.PROCESS_VISUALIZATION,
        ],
        default_density=DensityProfile.FOCUSED,
        suitable_formats=["a4_portrait", "presentation_16_9"],
        cognitive_trajectory=[
            CognitiveLevel.UNDERSTAND,
            CognitiveLevel.ANALYZE,
            CognitiveLevel.EVALUATE,
        ],
    ),
    MaterialStrategyType.SCIENTIFIC_REASONING: MaterialStrategyDefinition(
        strategy_type=MaterialStrategyType.SCIENTIFIC_REASONING,
        display_name="Empirical Scientific Inquiry",
        description="Formalizes empirical inquiry from observation to hypothesis testing and claim synthesis",
        preferred_stages=[
            LearningStageType.HOOK,
            LearningStageType.SURFACE_INTUITION,
            LearningStageType.HYPOTHESIS,
            LearningStageType.METHODOLOGY,
            LearningStageType.EVIDENCE_ANALYSIS,
            LearningStageType.SYNTHESIS,
        ],
        forbidden_orderings=[
            (LearningStageType.EVIDENCE_ANALYSIS, LearningStageType.HOOK),
        ],
        recommended_families=[
            CapabilityFamily.EVIDENCE_ANALYSIS,
            CapabilityFamily.PROCESS_VISUALIZATION,
            CapabilityFamily.RELATIONSHIP_MAPPING,
        ],
        default_density=DensityProfile.FOCUSED,
        suitable_formats=["a4_portrait", "presentation_16_9"],
        cognitive_trajectory=[
            CognitiveLevel.UNDERSTAND,
            CognitiveLevel.ANALYZE,
            CognitiveLevel.EVALUATE,
        ],
    ),
    MaterialStrategyType.QUICK_EXPLANATION: MaterialStrategyDefinition(
        strategy_type=MaterialStrategyType.QUICK_EXPLANATION,
        display_name="Concise High-Impact Explanation",
        description="Direct, concise concept delivery for executive summaries or quick classroom hooks",
        preferred_stages=[
            LearningStageType.HOOK,
            LearningStageType.CONCEPT_FORMALIZATION,
            LearningStageType.REPRESENTATION,
            LearningStageType.WORKED_EXAMPLE,
            LearningStageType.SUMMARY,
        ],
        forbidden_orderings=[
            (LearningStageType.SUMMARY, LearningStageType.HOOK),
        ],
        recommended_families=[
            CapabilityFamily.CONCEPT_STRUCTURE,
            CapabilityFamily.PROCESS_VISUALIZATION,
        ],
        default_density=DensityProfile.MINIMAL,
        suitable_formats=["presentation_16_9", "poster"],
        cognitive_trajectory=[
            CognitiveLevel.RECOGNIZE,
            CognitiveLevel.UNDERSTAND,
        ],
    ),
    MaterialStrategyType.DEEP_DIVE_TUTORIAL: MaterialStrategyDefinition(
        strategy_type=MaterialStrategyType.DEEP_DIVE_TUTORIAL,
        display_name="Comprehensive Technical Tutorial",
        description="Exhaustive reference tutorial including full mathematical proofs and derivations",
        preferred_stages=[
            LearningStageType.CONTEXT,
            LearningStageType.ACTIVATE_PRIOR_KNOWLEDGE,
            LearningStageType.CONCEPT_FORMALIZATION,
            LearningStageType.MATHEMATICAL_DERIVATION,
            LearningStageType.WORKED_EXAMPLE,
            LearningStageType.GUIDED_PRACTICE,
            LearningStageType.INDEPENDENT_PRACTICE,
            LearningStageType.REFLECTION,
            LearningStageType.SUMMARY,
        ],
        forbidden_orderings=[
            (LearningStageType.INDEPENDENT_PRACTICE, LearningStageType.CONCEPT_FORMALIZATION),
        ],
        recommended_families=[
            CapabilityFamily.QUANTITATIVE_ANALYSIS,
            CapabilityFamily.STEPWISE_REASONING,
            CapabilityFamily.COMPARATIVE_REASONING,
        ],
        default_density=DensityProfile.DENSE_REFERENCE,
        suitable_formats=["a4_portrait"],
        cognitive_trajectory=[
            CognitiveLevel.UNDERSTAND,
            CognitiveLevel.APPLY,
            CognitiveLevel.ANALYZE,
            CognitiveLevel.EVALUATE,
        ],
    ),
    MaterialStrategyType.PRESENTATION_STORY: MaterialStrategyDefinition(
        strategy_type=MaterialStrategyType.PRESENTATION_STORY,
        display_name="Dramatic Narrative Presentation Arc",
        description="Storytelling arc transitioning from problem tension to vision and call to action",
        preferred_stages=[
            LearningStageType.HOOK,
            LearningStageType.CONTEXT,
            LearningStageType.PROBLEM_STATEMENT,
            LearningStageType.CONCRETE_EXPERIENCE,
            LearningStageType.CONCEPT_FORMALIZATION,
            LearningStageType.SUMMARY,
            LearningStageType.CALL_TO_ACTION,
        ],
        forbidden_orderings=[
            (LearningStageType.CALL_TO_ACTION, LearningStageType.HOOK),
        ],
        recommended_families=[
            CapabilityFamily.CONCEPT_STRUCTURE,
            CapabilityFamily.PROCESS_VISUALIZATION,
        ],
        default_density=DensityProfile.MINIMAL,
        suitable_formats=["presentation_16_9"],
        cognitive_trajectory=[
            CognitiveLevel.RECOGNIZE,
            CognitiveLevel.UNDERSTAND,
            CognitiveLevel.EVALUATE,
        ],
    ),
    MaterialStrategyType.PROBLEM_BASED_LEARNING: MaterialStrategyDefinition(
        strategy_type=MaterialStrategyType.PROBLEM_BASED_LEARNING,
        display_name="Problem-Based Learning Inquiry",
        description="Authentic problem framing motivating research inquiry and multi-variable solutions",
        preferred_stages=[
            LearningStageType.PROBLEM_STATEMENT,
            LearningStageType.CONTEXT,
            LearningStageType.HYPOTHESIS,
            LearningStageType.METHODOLOGY,
            LearningStageType.EVIDENCE_ANALYSIS,
            LearningStageType.SYNTHESIS,
            LearningStageType.REFLECTION,
        ],
        forbidden_orderings=[
            (LearningStageType.SYNTHESIS, LearningStageType.PROBLEM_STATEMENT),
        ],
        recommended_families=[
            CapabilityFamily.EVIDENCE_ANALYSIS,
            CapabilityFamily.RELATIONSHIP_MAPPING,
        ],
        default_density=DensityProfile.FOCUSED,
        suitable_formats=["a4_portrait", "a4_landscape"],
        cognitive_trajectory=[
            CognitiveLevel.UNDERSTAND,
            CognitiveLevel.ANALYZE,
            CognitiveLevel.CREATE,
        ],
    ),
    MaterialStrategyType.EXAM_PREPARATION: MaterialStrategyDefinition(
        strategy_type=MaterialStrategyType.EXAM_PREPARATION,
        display_name="Exam & Mastery Preparation",
        description="Targeted problem solving, common pitfall analysis, and timed practice sets",
        preferred_stages=[
            LearningStageType.CONTEXT,
            LearningStageType.CONCEPT_FORMALIZATION,
            LearningStageType.MISCONCEPTION,
            LearningStageType.WORKED_EXAMPLE,
            LearningStageType.GUIDED_PRACTICE,
            LearningStageType.INDEPENDENT_PRACTICE,
            LearningStageType.SUMMARY,
        ],
        forbidden_orderings=[
            (LearningStageType.INDEPENDENT_PRACTICE, LearningStageType.CONCEPT_FORMALIZATION),
        ],
        recommended_families=[
            CapabilityFamily.STEPWISE_REASONING,
            CapabilityFamily.COMPARATIVE_REASONING,
        ],
        default_density=DensityProfile.FOCUSED,
        suitable_formats=["a4_portrait", "worksheet"],
        cognitive_trajectory=[
            CognitiveLevel.UNDERSTAND,
            CognitiveLevel.APPLY,
            CognitiveLevel.EVALUATE,
        ],
    ),
}


def get_strategy_definition(strategy_type: MaterialStrategyType) -> MaterialStrategyDefinition:
    """Retrieve strategy definition or return default CONCRETE_TO_ABSTRACT."""
    return STRATEGY_REGISTRY.get(strategy_type, STRATEGY_REGISTRY[MaterialStrategyType.CONCRETE_TO_ABSTRACT])
