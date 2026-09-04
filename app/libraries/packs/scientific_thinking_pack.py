"""
Scientific Thinking & Empirical Reasoning Domain Pack.

Provides components for empirical inquiry, hypothesis formulation, evidence testing, and causal inference.
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


def register_scientific_thinking_pack(registry: CapabilityRegistry) -> None:
    """Register all scientific thinking capabilities into registry."""

    # 1. Observation to Question
    register_family_capability(
        registry=registry,
        capability_id="scientific.observation_to_question",
        template_id="process.linear",
        metadata=CapabilityMetadata(
            capability_id="scientific.observation_to_question",
            category="scientific_reasoning",
            display_name="Observation-to-Question Formalization",
            description="Transforms natural phenomenon observations into rigorous, testable research questions",
            semantic_tags=["observation", "question_formulation", "phenomenon", "empirical_inquiry"],
            supported_artifacts=["presentation", "document", "worksheet"],
            domain="scientific_thinking",
            taxonomy=TaxonomySignature(
                family=CapabilityFamily.PROCESS_VISUALIZATION,
                primary_intent=SemanticIntent.NARROW_SCOPE,
                structure=InformationStructure.LINEAR_SEQUENCE,
                pedagogical_role=PedagogicalRole.SCAFFOLD,
                visual_grammar=VisualGrammar.PROCESS_FLOW,
                density=DensityProfile.FOCUSED,
            ),
        ),
    )

    # 2. Question to Hypothesis
    register_family_capability(
        registry=registry,
        capability_id="scientific.question_to_hypothesis",
        template_id="reasoning.evidence_chain",
        metadata=CapabilityMetadata(
            capability_id="scientific.question_to_hypothesis",
            category="scientific_reasoning",
            display_name="Hypothesis Derivation Framework",
            description="Derives testable, falsifiable directional hypotheses grounded in underlying theory",
            semantic_tags=["hypothesis_generation", "falsifiability", "theoretical_rationale", "predictions"],
            supported_artifacts=["presentation", "document", "worksheet"],
            domain="scientific_thinking",
            taxonomy=TaxonomySignature(
                family=CapabilityFamily.EVIDENCE_ANALYSIS,
                primary_intent=SemanticIntent.ARGUE,
                structure=InformationStructure.EVIDENCE_CHAIN,
                pedagogical_role=PedagogicalRole.EXPLANATION,
                visual_grammar=VisualGrammar.REASONING_FLOW,
                density=DensityProfile.FOCUSED,
            ),
        ),
    )

    # 3. Variable Reasoning Framework
    register_family_capability(
        registry=registry,
        capability_id="scientific.variable_reasoning",
        template_id="relationship.network",
        metadata=CapabilityMetadata(
            capability_id="scientific.variable_reasoning",
            category="scientific_reasoning",
            display_name="Variable Relationship & Interaction Network",
            description="Maps causal pathways between independent, dependent, moderating, and confounding variables",
            semantic_tags=["variable_reasoning", "causal_pathway", "confounding_factors", "moderators"],
            supported_artifacts=["presentation", "document", "poster"],
            domain="scientific_thinking",
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

    # 4. Prediction vs Observation
    register_family_capability(
        registry=registry,
        capability_id="scientific.prediction_vs_observation",
        template_id="comparison.matrix",
        metadata=CapabilityMetadata(
            capability_id="scientific.prediction_vs_observation",
            category="scientific_reasoning",
            display_name="Theoretical Prediction vs Observed Data",
            description="Compares quantitative model predictions directly against empirical measurement data",
            semantic_tags=["prediction_vs_observation", "data_validation", "model_fit", "discrepancy_analysis"],
            supported_artifacts=["presentation", "document", "worksheet"],
            domain="scientific_thinking",
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

    # 5. Model Revision Cycle
    register_family_capability(
        registry=registry,
        capability_id="scientific.model_revision",
        template_id="process.linear",
        metadata=CapabilityMetadata(
            capability_id="scientific.model_revision",
            category="scientific_reasoning",
            display_name="Scientific Model Refinement Cycle",
            description="Cyclic refinement: Initial Model → Anomaly Detection → Mechanism Adjustment → Revised Model",
            semantic_tags=["model_revision", "iterative_refinement", "scientific_progress", "theory_building"],
            supported_artifacts=["presentation", "document", "poster"],
            domain="scientific_thinking",
            taxonomy=TaxonomySignature(
                family=CapabilityFamily.PROCESS_VISUALIZATION,
                primary_intent=SemanticIntent.SEQUENCE,
                structure=InformationStructure.LINEAR_SEQUENCE,
                pedagogical_role=PedagogicalRole.SYNTHESIS,
                visual_grammar=VisualGrammar.PROCESS_FLOW,
                density=DensityProfile.FOCUSED,
            ),
        ),
    )

    # 6. Conclusion Logic & Warrant
    register_family_capability(
        registry=registry,
        capability_id="scientific.conclusion_logic",
        template_id="reasoning.evidence_chain",
        metadata=CapabilityMetadata(
            capability_id="scientific.conclusion_logic",
            category="scientific_reasoning",
            display_name="Scientific Conclusion & Warrant Matrix",
            description="Validates that conclusions strictly adhere to empirical scope without unwarranted extrapolation",
            semantic_tags=["conclusion_logic", "warrant", "scope_boundary", "scientific_validity"],
            supported_artifacts=["presentation", "document", "worksheet"],
            domain="scientific_thinking",
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

    # 7. Hypothesis Testing Protocol
    register_family_capability(
        registry=registry,
        capability_id="scientific.hypothesis_testing",
        template_id="comparison.matrix",
        metadata=CapabilityMetadata(
            capability_id="scientific.hypothesis_testing",
            category="scientific_reasoning",
            display_name="Hypothesis Falsification Matrix",
            description="Evaluates null vs alternative hypotheses against experimental criteria and significance thresholds",
            semantic_tags=["hypothesis_testing", "falsification", "null_hypothesis", "significance"],
            supported_artifacts=["presentation", "document", "worksheet"],
            domain="scientific_thinking",
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

    # 8. Causal Reasoning Mechanism
    register_family_capability(
        registry=registry,
        capability_id="scientific.causal_reasoning",
        template_id="reasoning.evidence_chain",
        metadata=CapabilityMetadata(
            capability_id="scientific.causal_reasoning",
            category="scientific_reasoning",
            display_name="Physical Causal Mechanism Chain",
            description="Microscopic to macroscopic physical causality chain explaining observable effects",
            semantic_tags=["causal_reasoning", "mechanism", "physical_law", "cause_effect"],
            supported_artifacts=["presentation", "document", "poster"],
            domain="scientific_thinking",
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

    # 9. Evidence Evaluation & Triangulation
    register_family_capability(
        registry=registry,
        capability_id="scientific.evidence_evaluation",
        template_id="comparison.matrix",
        metadata=CapabilityMetadata(
            capability_id="scientific.evidence_evaluation",
            category="scientific_reasoning",
            display_name="Empirical Evidence Evaluation Matrix",
            description="Triangulates multi-modal scientific data to assess internal and external validity",
            semantic_tags=["evidence_evaluation", "triangulation", "validity", "empirical_strength"],
            supported_artifacts=["presentation", "document", "worksheet"],
            domain="scientific_thinking",
            taxonomy=TaxonomySignature(
                family=CapabilityFamily.COMPARATIVE_REASONING,
                primary_intent=SemanticIntent.EVALUATE,
                structure=InformationStructure.MATRIX,
                pedagogical_role=PedagogicalRole.ANALYSIS,
                visual_grammar=VisualGrammar.COMPARISON,
                density=DensityProfile.FOCUSED,
            ),
        ),
    )

    # 10. Claim-Evidence-Reasoning (CER) Synthesis
    register_family_capability(
        registry=registry,
        capability_id="scientific.claim_evidence_reasoning",
        template_id="reasoning.evidence_chain",
        metadata=CapabilityMetadata(
            capability_id="scientific.claim_evidence_reasoning",
            category="scientific_reasoning",
            display_name="Scientific Claim-Evidence-Reasoning (CER) Synthesis",
            description="Classic pedagogical CER board synthesizing empirical claims, observations, and principles",
            semantic_tags=["cer", "claim_evidence_reasoning", "scientific_argument", "synthesis"],
            supported_artifacts=["presentation", "document", "poster", "worksheet"],
            domain="scientific_thinking",
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
