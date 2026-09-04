"""
Pedagogy & Learning Domain Pack.

Provides structured instructional, scaffolding, explanation, and assessment capabilities.
"""

from app.capabilities.contracts import CapabilityMetadata
from app.capabilities.families.factory import register_family_capability
from app.capabilities.registry import CapabilityRegistry
from app.capabilities.taxonomy import (
    CapabilityFamily,
    DensityProfile,
    InformationStructure,
    PedagogicalRole,
    SemanticIntent,
    TaxonomySignature,
    VisualGrammar,
)


def register_pedagogy_pack(registry: CapabilityRegistry) -> None:
    """Register all pedagogical instructional capabilities into registry."""

    # 1. Learning Objectives
    register_family_capability(
        registry=registry,
        capability_id="pedagogy.learning_objectives",
        template_id="collection.grid",
        metadata=CapabilityMetadata(
            capability_id="pedagogy.learning_objectives",
            category="pedagogy",
            display_name="Learning Objectives & Outcomes",
            description="Clear Bloom's taxonomy aligned learning goals for a unit or lesson",
            semantic_tags=["objectives", "outcomes", "goals", "competencies", "lesson_plan"],
            supported_artifacts=["presentation", "document", "worksheet"],
            domain="pedagogy",
            taxonomy=TaxonomySignature(
                family=CapabilityFamily.CONCEPT_STRUCTURE,
                primary_intent=SemanticIntent.INTRODUCE,
                structure=InformationStructure.MATRIX,
                pedagogical_role=PedagogicalRole.INTRODUCTION,
                visual_grammar=VisualGrammar.CONCEPT_PANEL,
                density=DensityProfile.FOCUSED,
            ),
        ),
    )

    # 2. Concept Progression Sequence
    register_family_capability(
        registry=registry,
        capability_id="pedagogy.concept_progression",
        template_id="process.linear",
        metadata=CapabilityMetadata(
            capability_id="pedagogy.concept_progression",
            category="pedagogy",
            display_name="Conceptual Progression Roadmap",
            description="Scaffolded learning path from intuitive prerequisite to formal mastery",
            semantic_tags=["concept_progression", "scaffolding", "learning_path", "prerequisites"],
            supported_artifacts=["presentation", "document", "worksheet"],
            domain="pedagogy",
            taxonomy=TaxonomySignature(
                family=CapabilityFamily.PROCESS_VISUALIZATION,
                primary_intent=SemanticIntent.SEQUENCE,
                structure=InformationStructure.LINEAR_SEQUENCE,
                pedagogical_role=PedagogicalRole.SCAFFOLD,
                visual_grammar=VisualGrammar.PROCESS_FLOW,
                density=DensityProfile.FOCUSED,
            ),
        ),
    )

    # 3. Analogy Bridge Card
    register_family_capability(
        registry=registry,
        capability_id="pedagogy.analogy_bridge",
        template_id="comparison.matrix",
        metadata=CapabilityMetadata(
            capability_id="pedagogy.analogy_bridge",
            category="pedagogy",
            display_name="Intuitive Analogy Bridge",
            description="Connects familiar real-world domain with abstract target scientific domain",
            semantic_tags=["analogy", "intuitive_model", "real_world_connection", "mental_model"],
            supported_artifacts=["presentation", "document", "worksheet"],
            domain="pedagogy",
            taxonomy=TaxonomySignature(
                family=CapabilityFamily.COMPARATIVE_REASONING,
                primary_intent=SemanticIntent.EXPLAIN,
                structure=InformationStructure.MATRIX,
                pedagogical_role=PedagogicalRole.EXPLANATION,
                visual_grammar=VisualGrammar.COMPARISON,
                density=DensityProfile.FOCUSED,
            ),
        ),
    )

    # 4. Concrete to Abstract Transition
    register_family_capability(
        registry=registry,
        capability_id="pedagogy.concrete_to_abstract",
        template_id="process.linear",
        metadata=CapabilityMetadata(
            capability_id="pedagogy.concrete_to_abstract",
            category="pedagogy",
            display_name="Concrete to Abstract Formalization",
            description="3-stage pedagogical journey: Physical Observation → Model Representation → Formal Equation",
            semantic_tags=["concrete_to_abstract", "formalization", "representation", "abstraction"],
            supported_artifacts=["presentation", "document", "worksheet"],
            domain="pedagogy",
            taxonomy=TaxonomySignature(
                family=CapabilityFamily.PROCESS_VISUALIZATION,
                primary_intent=SemanticIntent.SEQUENCE,
                structure=InformationStructure.LINEAR_SEQUENCE,
                pedagogical_role=PedagogicalRole.EXPLANATION,
                visual_grammar=VisualGrammar.PROCESS_FLOW,
                density=DensityProfile.FOCUSED,
            ),
        ),
    )

    # 5. Example vs Non-Example Contrast
    register_family_capability(
        registry=registry,
        capability_id="pedagogy.example_nonexample",
        template_id="comparison.matrix",
        metadata=CapabilityMetadata(
            capability_id="pedagogy.example_nonexample",
            category="pedagogy",
            display_name="Example vs Non-Example Discrimination",
            description="Clarifies concept boundaries by contrasting positive instances against near-miss counterexamples",
            semantic_tags=["example_nonexample", "boundary_testing", "discrimination", "concept_mastery"],
            supported_artifacts=["presentation", "document", "worksheet"],
            domain="pedagogy",
            taxonomy=TaxonomySignature(
                family=CapabilityFamily.COMPARATIVE_REASONING,
                primary_intent=SemanticIntent.COMPARE,
                structure=InformationStructure.MATRIX,
                pedagogical_role=PedagogicalRole.EXPLANATION,
                visual_grammar=VisualGrammar.COMPARISON,
                density=DensityProfile.FOCUSED,
            ),
        ),
    )

    # 6. Common Student Errors
    register_family_capability(
        registry=registry,
        capability_id="pedagogy.common_error",
        template_id="comparison.matrix",
        metadata=CapabilityMetadata(
            capability_id="pedagogy.common_error",
            category="pedagogy",
            display_name="Common Errors & Corrective Strategy",
            description="Catalogs typical exam/problem-solving mistakes alongside targeted diagnostic fixes",
            semantic_tags=["common_errors", "mistakes", "pitfalls", "exam_tips", "diagnostics"],
            supported_artifacts=["presentation", "document", "worksheet"],
            domain="pedagogy",
            taxonomy=TaxonomySignature(
                family=CapabilityFamily.COMPARATIVE_REASONING,
                primary_intent=SemanticIntent.COMPARE,
                structure=InformationStructure.MATRIX,
                pedagogical_role=PedagogicalRole.MISCONCEPTION,
                visual_grammar=VisualGrammar.COMPARISON,
                density=DensityProfile.FOCUSED,
            ),
        ),
    )

    # 7. Guided Practice Scaffold
    register_family_capability(
        registry=registry,
        capability_id="pedagogy.guided_practice",
        template_id="progression.ladder",
        metadata=CapabilityMetadata(
            capability_id="pedagogy.guided_practice",
            category="pedagogy",
            display_name="Guided Practice Ladder",
            description="Semi-structured problem solving with step-by-step teacher prompts and student inputs",
            semantic_tags=["guided_practice", "scaffolded_exercise", "hints", "stepwise_practice"],
            supported_artifacts=["presentation", "document", "worksheet"],
            domain="pedagogy",
            taxonomy=TaxonomySignature(
                family=CapabilityFamily.STEPWISE_REASONING,
                primary_intent=SemanticIntent.INVESTIGATE,
                structure=InformationStructure.QUESTION_SET,
                pedagogical_role=PedagogicalRole.SCAFFOLD,
                visual_grammar=VisualGrammar.CHECKPOINT_CARD,
                density=DensityProfile.FOCUSED,
            ),
        ),
    )

    # 8. Challenge Problem Panel
    register_family_capability(
        registry=registry,
        capability_id="pedagogy.challenge_problem",
        template_id="collection.grid",
        metadata=CapabilityMetadata(
            capability_id="pedagogy.challenge_problem",
            category="pedagogy",
            display_name="Advanced Challenge & Extension Problem",
            description="Higher-order thinking synthesis challenge for advanced learners",
            semantic_tags=["challenge", "extension", "olympiad", "advanced_problem", "synthesis"],
            supported_artifacts=["presentation", "document", "worksheet"],
            domain="pedagogy",
            taxonomy=TaxonomySignature(
                family=CapabilityFamily.CONCEPT_STRUCTURE,
                primary_intent=SemanticIntent.SYNTHESIZE,
                structure=InformationStructure.MATRIX,
                pedagogical_role=PedagogicalRole.ASSESSMENT,
                visual_grammar=VisualGrammar.CHECKPOINT_CARD,
                density=DensityProfile.ANALYTICAL,
            ),
        ),
    )

    # 9. Exit Ticket & Reflection Prompt
    register_family_capability(
        registry=registry,
        capability_id="pedagogy.exit_ticket",
        template_id="collection.grid",
        metadata=CapabilityMetadata(
            capability_id="pedagogy.exit_ticket",
            category="pedagogy",
            display_name="Formative Exit Ticket & Reflection",
            description="Quick end-of-lesson diagnostic check capturing key understanding and remaining questions",
            semantic_tags=["exit_ticket", "formative_check", "reflection", "lesson_close"],
            supported_artifacts=["presentation", "document", "worksheet"],
            domain="pedagogy",
            taxonomy=TaxonomySignature(
                family=CapabilityFamily.CONCEPT_STRUCTURE,
                primary_intent=SemanticIntent.ASSESS,
                structure=InformationStructure.QUESTION_SET,
                pedagogical_role=PedagogicalRole.ASSESSMENT,
                visual_grammar=VisualGrammar.CHECKPOINT_CARD,
                density=DensityProfile.MINIMAL,
            ),
        ),
    )

    # 10. Simple Explanation
    register_family_capability(
        registry=registry,
        capability_id="pedagogy.simple_explanation",
        template_id="collection.grid",
        metadata=CapabilityMetadata(
            capability_id="pedagogy.simple_explanation",
            category="pedagogy",
            display_name="Intuitive Plain-Language Explanation",
            description="Jargon-free explanation breaking down abstract concepts for novice learners",
            semantic_tags=["plain_language", "novice_friendly", "intuitive", "explanation"],
            supported_artifacts=["presentation", "document", "worksheet"],
            domain="pedagogy",
            taxonomy=TaxonomySignature(
                family=CapabilityFamily.CONCEPT_STRUCTURE,
                primary_intent=SemanticIntent.EXPLAIN,
                structure=InformationStructure.SINGLE_ENTITY,
                pedagogical_role=PedagogicalRole.EXPLANATION,
                visual_grammar=VisualGrammar.CONCEPT_PANEL,
                density=DensityProfile.MINIMAL,
            ),
        ),
    )

    # 11. Independent Practice
    register_family_capability(
        registry=registry,
        capability_id="pedagogy.independent_practice",
        template_id="progression.ladder",
        metadata=CapabilityMetadata(
            capability_id="pedagogy.independent_practice",
            category="pedagogy",
            display_name="Independent Practice Challenge Set",
            description="Unassisted practice problems designed to foster autonomous student mastery",
            semantic_tags=["independent_practice", "homework", "drills", "mastery_check"],
            supported_artifacts=["presentation", "document", "worksheet"],
            domain="pedagogy",
            taxonomy=TaxonomySignature(
                family=CapabilityFamily.STEPWISE_REASONING,
                primary_intent=SemanticIntent.INVESTIGATE,
                structure=InformationStructure.QUESTION_SET,
                pedagogical_role=PedagogicalRole.PRACTICE,
                visual_grammar=VisualGrammar.CHECKPOINT_CARD,
                density=DensityProfile.FOCUSED,
            ),
        ),
    )

    # 12. Self-Assessment Rubric
    register_family_capability(
        registry=registry,
        capability_id="pedagogy.self_assessment",
        template_id="comparison.matrix",
        metadata=CapabilityMetadata(
            capability_id="pedagogy.self_assessment",
            category="pedagogy",
            display_name="Metacognitive Self-Assessment Rubric",
            description="Criteria matrix allowing learners to self-evaluate depth of understanding",
            semantic_tags=["self_assessment", "rubric", "metacognition", "evaluation_criteria"],
            supported_artifacts=["presentation", "document", "worksheet"],
            domain="pedagogy",
            taxonomy=TaxonomySignature(
                family=CapabilityFamily.COMPARATIVE_REASONING,
                primary_intent=SemanticIntent.ASSESS,
                structure=InformationStructure.MATRIX,
                pedagogical_role=PedagogicalRole.ASSESSMENT,
                visual_grammar=VisualGrammar.COMPARISON,
                density=DensityProfile.FOCUSED,
            ),
        ),
    )
