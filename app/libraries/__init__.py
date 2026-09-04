"""
KIR AI Document Intelligence — Libraries Subsystem & Domain Packs.

Houses all parameterized, reusable capabilities across domain packs:
- Universal (Pedagogy, General Diagrams, Presentation)
- Research Education (Scientific Thinking, Problem Formulation, Methodology)
- Physics Mechanics (Torque, Free Body, Inclined Plane)
- Mathematics (Equation derivation, Variable mapping)
"""

from app.capabilities.registry import CapabilityRegistry

# Universal Domain
from app.libraries.pedagogy import worked_example_capability, misconception_capability
from app.libraries.diagrams import process_flow_capability
from app.libraries.presentation import hero_statement_capability, concept_intro_capability
from app.libraries.universal import (
    comparison_matrix_capability,
    concept_hierarchy_capability,
    evidence_chain_capability,
)
from app.libraries.pedagogy_scaffolding import (
    question_progression_capability,
    concept_checkpoint_capability,
)

# Physics & Mathematics
from app.libraries.physics import torque_diagram_capability, free_body_diagram_capability
from app.libraries.mathematics import equation_derivation_capability, variable_mapping_capability

# Research Education Domain Pack
from app.libraries.research_education import (
    scientific_reasoning_pathway_capability,
    hypothesis_test_capability,
    problem_funnel_capability,
    research_gap_capability,
    methodology_design_capability,
)
from app.libraries.research_education.scientific_thinking import (
    variable_relationship_map_capability,
    experiment_workflow_capability,
)


# Domain Packs (Batch 10 Massive Library Expansion)
from app.libraries.packs import (
    register_academic_writing_pack,
    register_data_literacy_pack,
    register_experiment_pack,
    register_pedagogy_pack,
    register_presentation_pack,
    register_research_education_pack,
    register_scientific_thinking_pack,
    register_universal_pack,
)


def register_all_default_capabilities(registry: CapabilityRegistry | None = None) -> CapabilityRegistry:
    """Register all standard built-in capabilities and domain packs into registry."""
    reg = registry or CapabilityRegistry.get_instance()

    # 1. Research Education Baseline Capabilities
    reg.register(scientific_reasoning_pathway_capability, overwrite=True)
    reg.register(hypothesis_test_capability, overwrite=True)
    reg.register(problem_funnel_capability, overwrite=True)
    reg.register(research_gap_capability, overwrite=True)
    reg.register(methodology_design_capability, overwrite=True)
    reg.register(variable_relationship_map_capability, overwrite=True)
    reg.register(experiment_workflow_capability, overwrite=True)

    # 2. Universal Pedagogy & Scaffolding Baseline
    reg.register(worked_example_capability, overwrite=True)
    reg.register(misconception_capability, overwrite=True)
    reg.register(process_flow_capability, overwrite=True)
    reg.register(hero_statement_capability, overwrite=True)
    reg.register(concept_intro_capability, overwrite=True)
    reg.register(comparison_matrix_capability, overwrite=True)
    reg.register(concept_hierarchy_capability, overwrite=True)
    reg.register(evidence_chain_capability, overwrite=True)
    reg.register(question_progression_capability, overwrite=True)
    reg.register(concept_checkpoint_capability, overwrite=True)

    # 3. Physics Mechanics & Mathematics Baseline
    reg.register(torque_diagram_capability, overwrite=True)
    reg.register(free_body_diagram_capability, overwrite=True)
    reg.register(equation_derivation_capability, overwrite=True)
    reg.register(variable_mapping_capability, overwrite=True)

    # 4. Domain Packs (Batch 10 Massive Expansion)
    register_universal_pack(reg)
    register_pedagogy_pack(reg)
    register_scientific_thinking_pack(reg)
    register_research_education_pack(reg)
    register_academic_writing_pack(reg)
    register_experiment_pack(reg)
    register_data_literacy_pack(reg)
    register_presentation_pack(reg)

    return reg
