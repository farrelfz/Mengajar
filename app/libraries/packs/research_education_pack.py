"""
Research Education & Methodology Domain Pack.

Provides structured visual and pedagogical components for scholarly investigation:
- Problem Boundary & Novelty
- Conceptual Framework & Literature Map
- Population Sampling & Operationalization
- Results Synthesis & Recommendation Mapping
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


def register_research_education_pack(registry: CapabilityRegistry) -> None:
    """Register all research education capabilities into registry."""

    # 1. Research Novelty Map
    register_family_capability(
        registry=registry,
        capability_id="research.novelty_map",
        template_id="comparison.matrix",
        metadata=CapabilityMetadata(
            capability_id="research.novelty_map",
            category="research_education",
            display_name="Scholarly Novelty & Contribution Map",
            description="Contrasts state-of-the-art literature limits against novel theoretical/empirical contributions",
            semantic_tags=["novelty", "contribution", "state_of_the_art", "originality", "literature_gap"],
            supported_artifacts=["presentation", "document", "poster"],
            domain="research_education",
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

    # 2. Conceptual Framework
    register_family_capability(
        registry=registry,
        capability_id="research.conceptual_framework",
        template_id="relationship.network",
        metadata=CapabilityMetadata(
            capability_id="research.conceptual_framework",
            category="research_education",
            display_name="Theoretical & Conceptual Framework",
            description="Maps theoretical constructs, operational dimensions, and hypothesized relationships",
            semantic_tags=["conceptual_framework", "theoretical_model", "constructs", "research_design"],
            supported_artifacts=["presentation", "document", "poster"],
            domain="research_education",
            taxonomy=TaxonomySignature(
                family=CapabilityFamily.RELATIONSHIP_MAPPING,
                primary_intent=SemanticIntent.RELATE,
                structure=InformationStructure.NETWORK,
                pedagogical_role=PedagogicalRole.EXPLANATION,
                visual_grammar=VisualGrammar.ANNOTATED_DIAGRAM,
                density=DensityProfile.ANALYTICAL,
            ),
        ),
    )

    # 3. Variable Operationalization Table
    register_family_capability(
        registry=registry,
        capability_id="research.variable_operationalization",
        template_id="comparison.matrix",
        metadata=CapabilityMetadata(
            capability_id="research.variable_operationalization",
            category="research_education",
            display_name="Variable Operationalization Matrix",
            description="Maps abstract theoretical variables to observable indicators, measurement scales, and instruments",
            semantic_tags=["operationalization", "indicators", "measurement_scale", "instruments", "variables"],
            supported_artifacts=["presentation", "document", "worksheet"],
            domain="research_education",
            taxonomy=TaxonomySignature(
                family=CapabilityFamily.COMPARATIVE_REASONING,
                primary_intent=SemanticIntent.EXPLAIN,
                structure=InformationStructure.MATRIX,
                pedagogical_role=PedagogicalRole.REFERENCE,
                visual_grammar=VisualGrammar.TABLE,
                density=DensityProfile.DENSE_REFERENCE,
            ),
        ),
    )

    # 4. Sampling & Population Design
    register_family_capability(
        registry=registry,
        capability_id="research.population_sampling",
        template_id="process.linear",
        metadata=CapabilityMetadata(
            capability_id="research.population_sampling",
            category="research_education",
            display_name="Population Sampling & Selection Flow",
            description="Stepwise sampling funnel: Target Population → Sampling Frame → Stratification → Sample Cohort",
            semantic_tags=["sampling_technique", "population", "sample_size", "representativeness", "sampling_flow"],
            supported_artifacts=["presentation", "document", "worksheet"],
            domain="research_education",
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

    # 5. Finding Summary & Pattern Detection
    register_family_capability(
        registry=registry,
        capability_id="research.finding_summary",
        template_id="collection.grid",
        metadata=CapabilityMetadata(
            capability_id="research.finding_summary",
            category="research_education",
            display_name="Empirical Finding Summary & Patterns",
            description="Synthesizes core quantitative/qualitative empirical findings by research question",
            semantic_tags=["findings", "empirical_results", "data_patterns", "evidence_summary"],
            supported_artifacts=["presentation", "document", "poster"],
            domain="research_education",
            taxonomy=TaxonomySignature(
                family=CapabilityFamily.CONCEPT_STRUCTURE,
                primary_intent=SemanticIntent.SYNTHESIZE,
                structure=InformationStructure.MATRIX,
                pedagogical_role=PedagogicalRole.SYNTHESIS,
                visual_grammar=VisualGrammar.CONCEPT_PANEL,
                density=DensityProfile.FOCUSED,
            ),
        ),
    )

    # 6. Limitation & Future Work Analysis
    register_family_capability(
        registry=registry,
        capability_id="research.limitation_analysis",
        template_id="comparison.matrix",
        metadata=CapabilityMetadata(
            capability_id="research.limitation_analysis",
            category="research_education",
            display_name="Methodological Limitations & Future Horizons",
            description="Contrasts unavoidable study scope constraints against concrete recommendations for future research",
            semantic_tags=["limitations", "scope_constraints", "future_work", "academic_rigor"],
            supported_artifacts=["presentation", "document", "worksheet"],
            domain="research_education",
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

    # 7. Actionable Recommendation Map
    register_family_capability(
        registry=registry,
        capability_id="research.recommendation_map",
        template_id="collection.grid",
        metadata=CapabilityMetadata(
            capability_id="research.recommendation_map",
            category="research_education",
            display_name="Grounded Policy & Practical Recommendations",
            description="Actionable stakeholder recommendations strictly grounded in verified research findings",
            semantic_tags=["recommendations", "policy_implications", "stakeholder_actions", "practical_impact"],
            supported_artifacts=["presentation", "document", "poster"],
            domain="research_education",
            taxonomy=TaxonomySignature(
                family=CapabilityFamily.CONCEPT_STRUCTURE,
                primary_intent=SemanticIntent.SYNTHESIZE,
                structure=InformationStructure.MATRIX,
                pedagogical_role=PedagogicalRole.SYNTHESIS,
                visual_grammar=VisualGrammar.CONCEPT_PANEL,
                density=DensityProfile.FOCUSED,
            ),
        ),
    )

    # 8. Literature Map
    register_family_capability(
        registry=registry,
        capability_id="research.literature_map",
        template_id="relationship.network",
        metadata=CapabilityMetadata(
            capability_id="research.literature_map",
            category="research_education",
            display_name="Scholarly Literature Network Map",
            description="Visualizes citation genealogies, seminal papers, and thematic research clusters",
            semantic_tags=["literature_map", "citation_network", "seminal_papers", "research_clusters"],
            supported_artifacts=["presentation", "document", "poster"],
            domain="research_education",
            taxonomy=TaxonomySignature(
                family=CapabilityFamily.RELATIONSHIP_MAPPING,
                primary_intent=SemanticIntent.RELATE,
                structure=InformationStructure.NETWORK,
                pedagogical_role=PedagogicalRole.EXPLANATION,
                visual_grammar=VisualGrammar.ANNOTATED_DIAGRAM,
                density=DensityProfile.ANALYTICAL,
            ),
        ),
    )

    # 9. Previous Study Comparison
    register_family_capability(
        registry=registry,
        capability_id="research.previous_study_comparison",
        template_id="comparison.matrix",
        metadata=CapabilityMetadata(
            capability_id="research.previous_study_comparison",
            category="research_education",
            display_name="Benchmark Against Previous Studies",
            description="Direct comparison matrix evaluating findings, sample sizes, and methodologies across published literature",
            semantic_tags=["previous_studies", "literature_benchmark", "comparative_findings"],
            supported_artifacts=["presentation", "document", "worksheet"],
            domain="research_education",
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

    # 10. Data Collection Workflow
    register_family_capability(
        registry=registry,
        capability_id="research.data_collection_flow",
        template_id="process.linear",
        metadata=CapabilityMetadata(
            capability_id="research.data_collection_flow",
            category="research_education",
            display_name="Empirical Data Collection Procedure",
            description="Step-by-step data collection protocol: Ethics Approval → Pilot Testing → Field Deployment → Archival",
            semantic_tags=["data_collection", "fieldwork", "instrumentation", "ethics", "pilot_test"],
            supported_artifacts=["presentation", "document", "worksheet"],
            domain="research_education",
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

    # 11. Interpretation & Discussion Chain
    register_family_capability(
        registry=registry,
        capability_id="research.interpretation_chain",
        template_id="reasoning.evidence_chain",
        metadata=CapabilityMetadata(
            capability_id="research.interpretation_chain",
            category="research_education",
            display_name="Scholarly Interpretation & Discussion Chain",
            description="Deep discussion chain linking empirical result to theoretical explanation and broader impact",
            semantic_tags=["discussion", "interpretation", "theoretical_context", "academic_argument"],
            supported_artifacts=["presentation", "document", "worksheet"],
            domain="research_education",
            taxonomy=TaxonomySignature(
                family=CapabilityFamily.EVIDENCE_ANALYSIS,
                primary_intent=SemanticIntent.ARGUE,
                structure=InformationStructure.EVIDENCE_CHAIN,
                pedagogical_role=PedagogicalRole.SYNTHESIS,
                visual_grammar=VisualGrammar.REASONING_FLOW,
                density=DensityProfile.ANALYTICAL,
            ),
        ),
    )
