"""
Experiment Design & Laboratory Literacy Domain Pack.

Provides domain-neutral experimental protocols, variable control cards, and laboratory procedures
applicable across Physics, Chemistry, Biology, Environmental Science, and Engineering.
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


def register_experiment_pack(registry: CapabilityRegistry) -> None:
    """Register all experiment design capabilities into registry."""

    # 1. Controlled Variables Identification
    register_family_capability(
        registry=registry,
        capability_id="experiment.controlled_variables",
        template_id="comparison.matrix",
        metadata=CapabilityMetadata(
            capability_id="experiment.controlled_variables",
            category="experiments",
            display_name="Variable Classification & Control Protocol",
            description="Categorizes Independent, Dependent, and Controlled variables with exact control mechanisms",
            semantic_tags=["controlled_variables", "fair_test", "experimental_control", "manipulated_variable"],
            supported_artifacts=["presentation", "document", "worksheet", "poster"],
            domain="experiment_design",
            taxonomy=TaxonomySignature(
                family=CapabilityFamily.COMPARATIVE_REASONING,
                primary_intent=SemanticIntent.CLASSIFY,
                structure=InformationStructure.MATRIX,
                pedagogical_role=PedagogicalRole.ANALYSIS,
                visual_grammar=VisualGrammar.COMPARISON,
                density=DensityProfile.FOCUSED,
            ),
        ),
    )

    # 2. Stepwise Experimental Procedure
    register_family_capability(
        registry=registry,
        capability_id="experiment.procedure_flow",
        template_id="process.linear",
        metadata=CapabilityMetadata(
            capability_id="experiment.procedure_flow",
            category="experiments",
            display_name="Experimental Protocol & Stepwise Procedure",
            description="Chronological laboratory protocol steps with safety warnings and measurement checkpoints",
            semantic_tags=["procedure", "laboratory_protocol", "method_steps", "experimental_run"],
            supported_artifacts=["presentation", "document", "worksheet"],
            domain="experiment_design",
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

    # 3. Apparatus Setup & Instrument Inventory
    register_family_capability(
        registry=registry,
        capability_id="experiment.apparatus_setup",
        template_id="collection.grid",
        metadata=CapabilityMetadata(
            capability_id="experiment.apparatus_setup",
            category="experiments",
            display_name="Apparatus Setup & Instrument Inventory",
            description="Inventory of laboratory glassware, electronic sensors, reagents, and calibration settings",
            semantic_tags=["apparatus", "instruments", "laboratory_equipment", "sensors", "reagents"],
            supported_artifacts=["presentation", "document", "worksheet"],
            domain="experiment_design",
            taxonomy=TaxonomySignature(
                family=CapabilityFamily.CONCEPT_STRUCTURE,
                primary_intent=SemanticIntent.INTRODUCE,
                structure=InformationStructure.MATRIX,
                pedagogical_role=PedagogicalRole.REFERENCE,
                visual_grammar=VisualGrammar.CONCEPT_PANEL,
                density=DensityProfile.FOCUSED,
            ),
        ),
    )

    # 4. Error Analysis & Uncertainty
    register_family_capability(
        registry=registry,
        capability_id="experiment.error_analysis",
        template_id="comparison.matrix",
        metadata=CapabilityMetadata(
            capability_id="experiment.error_analysis",
            category="experiments",
            display_name="Systematic vs Random Error Analysis",
            description="Evaluates measurement uncertainties, instrumental tolerances, and parallax sources",
            semantic_tags=["error_analysis", "systematic_error", "random_error", "uncertainty", "precision"],
            supported_artifacts=["presentation", "document", "worksheet"],
            domain="experiment_design",
            taxonomy=TaxonomySignature(
                family=CapabilityFamily.COMPARATIVE_REASONING,
                primary_intent=SemanticIntent.ANALYZE,
                structure=InformationStructure.MATRIX,
                pedagogical_role=PedagogicalRole.ANALYSIS,
                visual_grammar=VisualGrammar.COMPARISON,
                density=DensityProfile.FOCUSED,
            ),
        ),
    )

    # 5. Experimental Data Collection Protocol
    register_family_capability(
        registry=registry,
        capability_id="experiment.data_collection_protocol",
        template_id="process.linear",
        metadata=CapabilityMetadata(
            capability_id="experiment.data_collection_protocol",
            category="experiments",
            display_name="Data Logging & Replication Protocol",
            description="Replication schedule, sampling intervals, and duplicate trial validation rules",
            semantic_tags=["data_logging", "replication", "trials", "sampling_rate", "experimental_trials"],
            supported_artifacts=["presentation", "document", "worksheet"],
            domain="experiment_design",
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

    # 6. Experimental Variable Map
    register_family_capability(
        registry=registry,
        capability_id="experiment.variable_map",
        template_id="relationship.network",
        metadata=CapabilityMetadata(
            capability_id="experiment.variable_map",
            category="experiments",
            display_name="Laboratory Variable Interaction Network",
            description="Network diagram mapping controlled, extraneous, and manipulated variables in a lab setup",
            semantic_tags=["variable_map", "lab_variables", "controlled_setup", "extraneous_factors"],
            supported_artifacts=["presentation", "document", "poster"],
            domain="experiment_design",
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

    # 7. Raw Observation Table
    register_family_capability(
        registry=registry,
        capability_id="experiment.observation_table",
        template_id="comparison.matrix",
        metadata=CapabilityMetadata(
            capability_id="experiment.observation_table",
            category="experiments",
            display_name="Empirical Observation & Measurement Matrix",
            description="Structured table for recording quantitative measurements, units, and qualitative notes across trials",
            semantic_tags=["observation_table", "lab_data", "measurements", "trials_log"],
            supported_artifacts=["presentation", "document", "worksheet"],
            domain="experiment_design",
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

    # 8. Laboratory Safety & Hazard Warning
    register_family_capability(
        registry=registry,
        capability_id="experiment.safety_protocol",
        template_id="collection.grid",
        metadata=CapabilityMetadata(
            capability_id="experiment.safety_protocol",
            category="experiments",
            display_name="Laboratory Safety & Hazard Prevention Board",
            description="Crucial chemical, electrical, and thermal hazard prevention warnings and PPE requirements",
            semantic_tags=["safety_protocol", "hazards", "ppe", "lab_safety", "precautions"],
            supported_artifacts=["presentation", "document", "poster", "worksheet"],
            domain="experiment_design",
            taxonomy=TaxonomySignature(
                family=CapabilityFamily.CONCEPT_STRUCTURE,
                primary_intent=SemanticIntent.INTRODUCE,
                structure=InformationStructure.MATRIX,
                pedagogical_role=PedagogicalRole.INTRODUCTION,
                visual_grammar=VisualGrammar.CONCEPT_PANEL,
                density=DensityProfile.MINIMAL,
            ),
        ),
    )
