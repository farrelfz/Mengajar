"""
Universal Knowledge Visualization Domain Pack.

Provides general-purpose structural, comparative, reasoning, and collection capabilities.
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


def register_universal_pack(registry: CapabilityRegistry) -> None:
    """Register all universal knowledge capabilities into registry."""

    # 1. Structure: Component Breakdown
    register_family_capability(
        registry=registry,
        capability_id="universal.component_breakdown",
        template_id="hierarchy.tree",
        metadata=CapabilityMetadata(
            capability_id="universal.component_breakdown",
            category="universal",
            display_name="Component Breakdown Structure",
            description="Decomposes a complex system or entity into constituent sub-components",
            semantic_tags=["component", "breakdown", "subsystems", "structure", "parts"],
            supported_artifacts=["presentation", "document", "poster", "worksheet"],
            domain="general",
            taxonomy=TaxonomySignature(
                family=CapabilityFamily.CONCEPT_STRUCTURE,
                primary_intent=SemanticIntent.CLASSIFY,
                structure=InformationStructure.HIERARCHY,
                pedagogical_role=PedagogicalRole.EXPLANATION,
                visual_grammar=VisualGrammar.CONCEPT_MAP,
                density=DensityProfile.FOCUSED,
            ),
        ),
    )

    # 2. Structure: System Map
    register_family_capability(
        registry=registry,
        capability_id="universal.system_map",
        template_id="relationship.network",
        metadata=CapabilityMetadata(
            capability_id="universal.system_map",
            category="universal",
            display_name="System Architecture & Relationship Map",
            description="Maps interconnected system elements and their causal/functional relationships",
            semantic_tags=["system", "architecture", "network", "dependencies", "interactions"],
            supported_artifacts=["presentation", "document", "poster"],
            domain="general",
            taxonomy=TaxonomySignature(
                family=CapabilityFamily.RELATIONSHIP_MAPPING,
                primary_intent=SemanticIntent.RELATE,
                structure=InformationStructure.NETWORK,
                pedagogical_role=PedagogicalRole.ANALYSIS,
                visual_grammar=VisualGrammar.ANNOTATED_DIAGRAM,
                density=DensityProfile.ANALYTICAL,
            ),
        ),
    )

    # 3. Comparison: Pros & Cons
    register_family_capability(
        registry=registry,
        capability_id="universal.pros_cons",
        template_id="comparison.matrix",
        metadata=CapabilityMetadata(
            capability_id="universal.pros_cons",
            category="universal",
            display_name="Pros & Cons Evaluation Matrix",
            description="Contrasts advantages and limitations across one or more options",
            semantic_tags=["pros_cons", "advantages", "disadvantages", "trade_offs", "evaluation"],
            supported_artifacts=["presentation", "document", "worksheet"],
            domain="general",
            taxonomy=TaxonomySignature(
                family=CapabilityFamily.COMPARATIVE_REASONING,
                primary_intent=SemanticIntent.COMPARE,
                structure=InformationStructure.MATRIX,
                pedagogical_role=PedagogicalRole.ANALYSIS,
                visual_grammar=VisualGrammar.COMPARISON,
                density=DensityProfile.FOCUSED,
            ),
        ),
    )

    # 4. Comparison: Before vs After
    register_family_capability(
        registry=registry,
        capability_id="universal.before_after",
        template_id="comparison.matrix",
        metadata=CapabilityMetadata(
            capability_id="universal.before_after",
            category="universal",
            display_name="Before vs After Transformation Matrix",
            description="Compares baseline conditions directly against post-intervention outcomes",
            semantic_tags=["before_after", "transformation", "intervention", "comparison", "impact"],
            supported_artifacts=["presentation", "document", "poster"],
            domain="general",
            taxonomy=TaxonomySignature(
                family=CapabilityFamily.COMPARATIVE_REASONING,
                primary_intent=SemanticIntent.COMPARE,
                structure=InformationStructure.MATRIX,
                pedagogical_role=PedagogicalRole.ANALYSIS,
                visual_grammar=VisualGrammar.COMPARISON,
                density=DensityProfile.FOCUSED,
            ),
        ),
    )

    # 5. Comparison: Similarity & Difference
    register_family_capability(
        registry=registry,
        capability_id="universal.similarity_difference",
        template_id="comparison.matrix",
        metadata=CapabilityMetadata(
            capability_id="universal.similarity_difference",
            category="universal",
            display_name="Similarity & Distinction Matrix",
            description="Highlights shared commonalities and distinguishing features between concepts",
            semantic_tags=["similarity", "distinction", "nuance", "compare_contrast"],
            supported_artifacts=["presentation", "document", "worksheet"],
            domain="general",
            taxonomy=TaxonomySignature(
                family=CapabilityFamily.COMPARATIVE_REASONING,
                primary_intent=SemanticIntent.COMPARE,
                structure=InformationStructure.MATRIX,
                pedagogical_role=PedagogicalRole.ANALYSIS,
                visual_grammar=VisualGrammar.COMPARISON,
                density=DensityProfile.FOCUSED,
            ),
        ),
    )

    # 6. Reasoning: Cause & Effect Chain
    register_family_capability(
        registry=registry,
        capability_id="universal.cause_effect_chain",
        template_id="reasoning.evidence_chain",
        metadata=CapabilityMetadata(
            capability_id="universal.cause_effect_chain",
            category="universal",
            display_name="Causal Mechanism Chain",
            description="Stepwise causal cascade linking initial trigger to intermediate and final effects",
            semantic_tags=["cause_effect", "causality", "chain_reaction", "mechanism", "trigger"],
            supported_artifacts=["presentation", "document", "poster"],
            domain="general",
            taxonomy=TaxonomySignature(
                family=CapabilityFamily.EVIDENCE_ANALYSIS,
                primary_intent=SemanticIntent.RELATE,
                structure=InformationStructure.EVIDENCE_CHAIN,
                pedagogical_role=PedagogicalRole.EXPLANATION,
                visual_grammar=VisualGrammar.REASONING_FLOW,
                density=DensityProfile.ANALYTICAL,
            ),
        ),
    )

    # 7. Reasoning: Problem-Solution Frame
    register_family_capability(
        registry=registry,
        capability_id="universal.problem_solution",
        template_id="reasoning.evidence_chain",
        metadata=CapabilityMetadata(
            capability_id="universal.problem_solution",
            category="universal",
            display_name="Problem-Diagnosis-Solution Architecture",
            description="Structures problem statement, root cause diagnosis, proposed remedy, and outcome",
            semantic_tags=["problem_solution", "diagnosis", "remedy", "intervention", "resolution"],
            supported_artifacts=["presentation", "document", "worksheet"],
            domain="general",
            taxonomy=TaxonomySignature(
                family=CapabilityFamily.EVIDENCE_ANALYSIS,
                primary_intent=SemanticIntent.ARGUE,
                structure=InformationStructure.EVIDENCE_CHAIN,
                pedagogical_role=PedagogicalRole.SYNTHESIS,
                visual_grammar=VisualGrammar.REASONING_FLOW,
                density=DensityProfile.FOCUSED,
            ),
        ),
    )

    # 8. Process: Decision Path Flow
    register_family_capability(
        registry=registry,
        capability_id="universal.decision_path",
        template_id="process.linear",
        metadata=CapabilityMetadata(
            capability_id="universal.decision_path",
            category="universal",
            display_name="Decision Tree & Criteria Flow",
            description="Stepwise branching criteria guiding decisions or categorization",
            semantic_tags=["decision_path", "logic_tree", "criteria_flow", "guidelines"],
            supported_artifacts=["presentation", "document", "worksheet"],
            domain="general",
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

    # 9. Collection: Key Takeaways
    register_family_capability(
        registry=registry,
        capability_id="universal.key_takeaways",
        template_id="collection.grid",
        metadata=CapabilityMetadata(
            capability_id="universal.key_takeaways",
            category="universal",
            display_name="Key Takeaways & Core Insights",
            description="Grouped essential conclusions and high-priority learning takeaways",
            semantic_tags=["takeaways", "summary", "core_insights", "conclusions", "highlights"],
            supported_artifacts=["presentation", "document", "poster", "worksheet"],
            domain="general",
            taxonomy=TaxonomySignature(
                family=CapabilityFamily.CONCEPT_STRUCTURE,
                primary_intent=SemanticIntent.SYNTHESIZE,
                structure=InformationStructure.MATRIX,
                pedagogical_role=PedagogicalRole.SYNTHESIS,
                visual_grammar=VisualGrammar.CONCEPT_PANEL,
                density=DensityProfile.MINIMAL,
            ),
        ),
    )

    # 10. Collection: Summary Board
    register_family_capability(
        registry=registry,
        capability_id="universal.summary_board",
        template_id="collection.grid",
        metadata=CapabilityMetadata(
            capability_id="universal.summary_board",
            category="universal",
            display_name="Comprehensive Summary Board",
            description="Multi-category card grid summarizing unit or chapter themes",
            semantic_tags=["summary_board", "overview", "chapter_summary", "unit_review"],
            supported_artifacts=["presentation", "document", "worksheet"],
            domain="general",
            taxonomy=TaxonomySignature(
                family=CapabilityFamily.CONCEPT_STRUCTURE,
                primary_intent=SemanticIntent.SYNTHESIZE,
                structure=InformationStructure.MATRIX,
                pedagogical_role=PedagogicalRole.REFERENCE,
                visual_grammar=VisualGrammar.CONCEPT_PANEL,
                density=DensityProfile.DENSE_REFERENCE,
            ),
        ),
    )

    # 11. Structure: Concept Definition
    register_family_capability(
        registry=registry,
        capability_id="universal.concept_definition",
        template_id="collection.grid",
        metadata=CapabilityMetadata(
            capability_id="universal.concept_definition",
            category="universal",
            display_name="Formal Concept Definition & Etymology",
            description="Authoritative domain definition, formal notation, and etymology breakdown",
            semantic_tags=["definition", "formal_term", "terminology", "glossary"],
            supported_artifacts=["presentation", "document", "worksheet"],
            domain="general",
            taxonomy=TaxonomySignature(
                family=CapabilityFamily.CONCEPT_STRUCTURE,
                primary_intent=SemanticIntent.INTRODUCE,
                structure=InformationStructure.SINGLE_ENTITY,
                pedagogical_role=PedagogicalRole.INTRODUCTION,
                visual_grammar=VisualGrammar.CONCEPT_PANEL,
                density=DensityProfile.MINIMAL,
            ),
        ),
    )

    # 12. Comparison: Feature Comparison
    register_family_capability(
        registry=registry,
        capability_id="universal.feature_comparison",
        template_id="comparison.matrix",
        metadata=CapabilityMetadata(
            capability_id="universal.feature_comparison",
            category="universal",
            display_name="Multi-Feature Comparison Matrix",
            description="Multi-attribute benchmark evaluating multiple entities across standardized criteria",
            semantic_tags=["feature_comparison", "benchmark", "evaluation_grid", "matrix"],
            supported_artifacts=["presentation", "document", "worksheet"],
            domain="general",
            taxonomy=TaxonomySignature(
                family=CapabilityFamily.COMPARATIVE_REASONING,
                primary_intent=SemanticIntent.COMPARE,
                structure=InformationStructure.MATRIX,
                pedagogical_role=PedagogicalRole.ANALYSIS,
                visual_grammar=VisualGrammar.COMPARISON,
                density=DensityProfile.FOCUSED,
            ),
        ),
    )

    # 13. Process: Transformation Flow
    register_family_capability(
        registry=registry,
        capability_id="universal.transformation_flow",
        template_id="process.linear",
        metadata=CapabilityMetadata(
            capability_id="universal.transformation_flow",
            category="universal",
            display_name="State Transformation & Lifecycle Flow",
            description="Stages of physical, conceptual, or operational metamorphosis",
            semantic_tags=["transformation", "lifecycle", "state_machine", "evolution"],
            supported_artifacts=["presentation", "document", "poster"],
            domain="general",
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

    # 14. Collection: Fact Collection Grid
    register_family_capability(
        registry=registry,
        capability_id="universal.fact_collection",
        template_id="collection.grid",
        metadata=CapabilityMetadata(
            capability_id="universal.fact_collection",
            category="universal",
            display_name="Core Fact & Data Inventory Grid",
            description="Structured grid of verified empirical facts, constants, and principles",
            semantic_tags=["facts", "data_inventory", "constants", "principles"],
            supported_artifacts=["presentation", "document", "worksheet"],
            domain="general",
            taxonomy=TaxonomySignature(
                family=CapabilityFamily.CONCEPT_STRUCTURE,
                primary_intent=SemanticIntent.SYNTHESIZE,
                structure=InformationStructure.MATRIX,
                pedagogical_role=PedagogicalRole.REFERENCE,
                visual_grammar=VisualGrammar.CONCEPT_PANEL,
                density=DensityProfile.FOCUSED,
            ),
        ),
    )
