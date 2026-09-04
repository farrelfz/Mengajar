"""
Unit tests for Research Education Domain Pack capabilities.
"""

from app.libraries.research_education import (
    scientific_reasoning_pathway_capability,
    hypothesis_test_capability,
    problem_funnel_capability,
    research_gap_capability,
    methodology_design_capability,
)
from app.libraries.research_education.scientific_thinking import (
    ScientificReasoningPathwaySpec,
    HypothesisTestSpec,
    ReasoningStage,
)
from app.libraries.research_education.research_problem import (
    ProblemFunnelSpec,
    ResearchGapSpec,
)
from app.libraries.research_education.methodology import (
    MethodologyDesignSpec,
    VariableItem,
)


def test_scientific_reasoning_pathway_rendering():
    spec = ScientificReasoningPathwaySpec(
        topic="Physics Inquiry",
        stages=[
            ReasoningStage(stage_name="Observation", description="Apple falls from tree"),
            ReasoningStage(stage_name="Question", description="Why does it fall straight down?"),
            ReasoningStage(stage_name="Hypothesis", description="Earth exerts an invisible attractive force"),
            ReasoningStage(stage_name="Evidence", description="Orbital mechanics & acceleration data"),
            ReasoningStage(stage_name="Conclusion", description="Universal gravitation law"),
        ],
    )
    assert scientific_reasoning_pathway_capability.renderer.validate_spec(spec) is True
    output = scientific_reasoning_pathway_capability.renderer.render(spec)

    assert output.output_format == "svg"
    assert "<svg" in output.rendered_content
    assert "Apple falls" in output.rendered_content
    assert "Universal gravitation" in output.rendered_content


def test_problem_funnel_rendering():
    spec = ProblemFunnelSpec(
        topic="Microplastics in Tap Water",
        phenomenon="Plastic waste accumulation in urban water reservoirs",
        problem_identification="High concentration of microplastics entering domestic supply",
        scope_limitation="Residential tap water in District X over a 30-day period",
        final_research_question="What is the daily microplastic particle intake per household in District X?",
    )
    assert problem_funnel_capability.renderer.validate_spec(spec) is True
    output = problem_funnel_capability.renderer.render(spec)

    assert output.output_format == "svg"
    assert "<svg" in output.rendered_content
    assert "Problem Formulation Funnel" in output.rendered_content
    assert "Microplastics" in output.rendered_content


def test_research_gap_matrix_rendering():
    spec = ResearchGapSpec(
        topic="AI in Document Intelligence",
        existing_consensus="LLMs generate raw text easily",
        unresolved_gap="LLMs cannot deterministically lay out print-quality PDFs without pixel bugs",
        study_contribution="Hybrid deterministic layout engine with semantic blueprints",
    )
    assert research_gap_capability.renderer.validate_spec(spec) is True
    output = research_gap_capability.renderer.render(spec)

    assert output.output_format == "html"
    assert "Literature Gap Analysis" in output.rendered_content
    assert "The Knowledge Gap" in output.rendered_content


def test_methodology_design_matrix_rendering():
    spec = MethodologyDesignSpec(
        study_title="Effect of Retrieval Practice on Physics Retention",
        research_design_type="Quasi-Experimental Pretest-Posttest Design",
        population_and_sample="120 Grade 11 Physics students across 4 classrooms",
        data_collection_instruments=["Conceptual Diagnostic Test (FCI)", "Retention Questionnaire"],
        variables=[
            VariableItem(
                name="Retrieval Practice Frequency",
                role="Independent",
                operational_definition="Weekly spaced retrieval quizzes vs standard review",
                measurement_unit_or_scale="Frequency per week (0 vs 2 sessions)",
            ),
            VariableItem(
                name="Physics Conceptual Score",
                role="Dependent",
                operational_definition="Score on 30-item diagnostic test",
                measurement_unit_or_scale="Percentage (0-100%)",
            ),
        ],
        procedure_steps=["Pre-test administration", "8-week intervention", "Post-test & Delayed test"],
        data_analysis_technique="ANCOVA controlling for baseline pre-test scores",
    )
    assert methodology_design_capability.renderer.validate_spec(spec) is True
    output = methodology_design_capability.renderer.render(spec)

    assert output.output_format == "html"
    assert "Operational Variable Matrix" in output.rendered_content
    assert "ANCOVA" in output.rendered_content
