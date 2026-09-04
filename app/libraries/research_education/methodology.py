"""
KIR AI Document Intelligence — Research Methodology Library.

Provides parameterized components for research design and methodology:
- Methodology Design Matrix (Variables, Sampling, Instruments, Procedure, Analysis)
"""

from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field

from app.capabilities.contracts import (
    Capability,
    CapabilityMetadata,
    CapabilityOutput,
    CapabilityRenderer,
    CapabilitySpec,
)


class VariableItem(BaseModel):
    name: str
    role: str  # "Independent", "Dependent", "Control"
    operational_definition: str
    measurement_unit_or_scale: str


class MethodologyDesignSpec(CapabilitySpec):
    study_title: str
    research_design_type: str = "True Experimental (Pretest-Posttest Control Group)"
    population_and_sample: str
    data_collection_instruments: list[str] = Field(default_factory=list)
    variables: list[VariableItem] = Field(default_factory=list)
    procedure_steps: list[str] = Field(default_factory=list)
    data_analysis_technique: str


class MethodologyDesignRenderer(CapabilityRenderer[MethodologyDesignSpec]):

    def validate_spec(self, spec: MethodologyDesignSpec) -> bool:
        return bool(spec.study_title and spec.data_analysis_technique)

    def measure(self, spec: MethodologyDesignSpec, context: dict[str, Any] | None = None) -> dict[str, Any]:
        return {"height_px": 420, "complexity": "high"}

    def render(self, spec: MethodologyDesignSpec, context: dict[str, Any] | None = None) -> CapabilityOutput:
        var_rows = "".join(f"""
        <tr>
            <td><span class="badge role-badge role-{v.role.lower()}">{v.role}</span></td>
            <td><strong>{v.name}</strong></td>
            <td>{v.operational_definition}</td>
            <td><code>{v.measurement_unit_or_scale}</code></td>
        </tr>
        """ for v in spec.variables)

        inst_list = "".join(f"<li>{inst}</li>" for inst in spec.data_collection_instruments)
        proc_list = "".join(f"<li>{step}</li>" for step in spec.procedure_steps)

        html = f"""
        <div class="capability-methodology-matrix card">
            <div class="meth-header">
                <span class="badge meth-badge">Research Methodology Framework</span>
                <h3>{spec.study_title}</h3>
                <div class="design-type-tag"><strong>Design:</strong> {spec.research_design_type}</div>
            </div>
            
            {f'''
            <div class="meth-section">
                <h4>1. Operational Variable Matrix</h4>
                <table class="meth-table">
                    <thead>
                        <tr><th>Role</th><th>Variable Name</th><th>Operational Definition</th><th>Measurement Scale</th></tr>
                    </thead>
                    <tbody>{var_rows}</tbody>
                </table>
            </div>
            ''' if spec.variables else ''}

            <div class="meth-grid-2">
                <div class="card subcard">
                    <h4>2. Sample & Instruments</h4>
                    <p><strong>Sample/Subjects:</strong> {spec.population_and_sample}</p>
                    {f'<ul>{inst_list}</ul>' if inst_list else ''}
                </div>
                <div class="card subcard">
                    <h4>3. Analysis Technique</h4>
                    <p><strong>Statistical/Qualitative Analysis:</strong> {spec.data_analysis_technique}</p>
                    {f'<ol>{proc_list}</ol>' if proc_list else ''}
                </div>
            </div>
        </div>
        """
        return CapabilityOutput(
            capability_id="research.methodology.design_matrix",
            output_format="html",
            rendered_content=html,
            width_px=800,
            height_px=420,
        )


def _extract_methodology_design(step: Any, material: Any) -> dict[str, Any]:
    title = material.content.metadata.title
    return {
        "study_title": title,
        "population_and_sample": "Target educational cohort (N=100)",
        "data_analysis_technique": "Inferential statistical testing and descriptive metrics",
    }


from app.capabilities.taxonomy import (
    CapabilityFamily,
    DensityProfile,
    InformationStructure,
    PedagogicalRole,
    SemanticIntent,
    TaxonomySignature,
    VisualGrammar,
)


methodology_design_capability = Capability(
    metadata=CapabilityMetadata(
        capability_id="research.methodology.design_matrix",
        category="methodology",
        display_name="Research Methodology Design Matrix",
        description="Comprehensive research design matrix specifying variables, sampling, instruments, procedure, and analysis.",
        semantic_tags=["methodology", "research_design", "variables", "instruments", "data_analysis", "kti_bab3"],
        supported_artifacts=["presentation", "document", "poster", "worksheet"],
        domain="research_education",
        complexity_score=3.0,
        preferred_renderer="html",
        taxonomy=TaxonomySignature(
            family=CapabilityFamily.QUANTITATIVE_ANALYSIS,
            primary_intent=SemanticIntent.ANALYZE,
            supported_intents=[SemanticIntent.INVESTIGATE, SemanticIntent.CLASSIFY],
            structure=InformationStructure.MATRIX,
            pedagogical_role=PedagogicalRole.ANALYSIS,
            visual_grammar=VisualGrammar.MATRIX,
            density=DensityProfile.DENSE_REFERENCE,
            preferred_formats=["a4_portrait", "a4_landscape", "presentation_16_9"],
        ),
    ),
    spec_model=MethodologyDesignSpec,
    renderer=MethodologyDesignRenderer(),
    parameter_extractor=_extract_methodology_design,
)
