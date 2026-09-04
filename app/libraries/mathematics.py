"""
KIR AI Document Intelligence — Mathematics Explanation Library.

Provides parameterized components for mathematical reasoning:
- Equation Derivation Steps (Known Equation -> Transformations -> Final Equation)
- Variable Mapping (Equation -> Symbols -> Physical Meanings -> SI Units)
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


class DerivationStep(BaseModel):
    step_number: int
    equation: str
    annotation: str
    rule_applied: str | None = None


class EquationDerivationSpec(CapabilitySpec):
    initial_equation: str
    final_equation: str
    target_variable: str | None = None
    steps: list[DerivationStep] = Field(default_factory=list)


class EquationDerivationRenderer(CapabilityRenderer[EquationDerivationSpec]):

    def validate_spec(self, spec: EquationDerivationSpec) -> bool:
        return bool(spec.initial_equation and spec.final_equation)

    def measure(self, spec: EquationDerivationSpec, context: dict[str, Any] | None = None) -> dict[str, Any]:
        return {"height_px": len(spec.steps) * 70 + 150}

    def render(self, spec: EquationDerivationSpec, context: dict[str, Any] | None = None) -> CapabilityOutput:
        steps_html = ""
        for s in spec.steps:
            rule_badge = f"<span class='badge rule-badge'>{s.rule_applied}</span>" if s.rule_applied else ""
            steps_html += f"""
            <div class="derivation-step-row">
                <div class="step-badge">{s.step_number}</div>
                <div class="step-eq"><code>{s.equation}</code></div>
                <div class="step-arrow">➔</div>
                <div class="step-note">{s.annotation} {rule_badge}</div>
            </div>
            """

        html = f"""
        <div class="capability-equation-derivation card">
            <div class="derivation-header">
                <span class="badge math-badge">Equation Derivation</span>
                <h3>Target: <code>{spec.final_equation}</code></h3>
            </div>
            <div class="derivation-steps">
                <div class="derivation-start">
                    <span class="start-label">Starting Principle:</span>
                    <code>{spec.initial_equation}</code>
                </div>
                {steps_html}
                <div class="derivation-result">
                    <span class="result-label">Result:</span>
                    <code>{spec.final_equation}</code>
                </div>
            </div>
        </div>
        """
        return CapabilityOutput(
            capability_id="mathematics.equation_derivation",
            output_format="html",
            rendered_content=html,
            width_px=750,
            height_px=len(spec.steps) * 70 + 150,
        )


from app.capabilities.taxonomy import (
    CapabilityFamily,
    DensityProfile,
    InformationStructure,
    PedagogicalRole,
    SemanticIntent,
    TaxonomySignature,
    VisualGrammar,
)


equation_derivation_capability = Capability(
    metadata=CapabilityMetadata(
        capability_id="mathematics.equation_derivation",
        category="mathematics",
        display_name="Equation Derivation Pathway",
        description="Step-by-step mathematical derivation showing algebraic transformations and principles applied.",
        semantic_tags=["equation_derivation", "algebra", "derivation", "formula_proof", "step_by_step_math"],
        supported_artifacts=["presentation", "document", "worksheet", "poster"],
        domain="mathematics",
        complexity_score=3.0,
        preferred_renderer="html",
        taxonomy=TaxonomySignature(
            family=CapabilityFamily.STEPWISE_REASONING,
            primary_intent=SemanticIntent.DERIVE,
            supported_intents=[SemanticIntent.SEQUENCE, SemanticIntent.EXPLAIN],
            structure=InformationStructure.TRANSFORMATION,
            pedagogical_role=PedagogicalRole.EXPLANATION,
            visual_grammar=VisualGrammar.EQUATION_CHAIN,
            density=DensityProfile.ANALYTICAL,
            preferred_formats=["a4_portrait", "a4_landscape", "presentation_16_9"],
        ),
    ),
    spec_model=EquationDerivationSpec,
    renderer=EquationDerivationRenderer(),
)


# --- 2. Variable Mapping ---

class VariableItem(BaseModel):
    symbol: str
    meaning: str
    si_unit: str
    typical_value: str | None = None


class VariableMappingSpec(CapabilitySpec):
    equation_name: str
    formula: str
    variables: list[VariableItem] = Field(default_factory=list)


class VariableMappingRenderer(CapabilityRenderer[VariableMappingSpec]):

    def validate_spec(self, spec: VariableMappingSpec) -> bool:
        return len(spec.variables) > 0

    def measure(self, spec: VariableMappingSpec, context: dict[str, Any] | None = None) -> dict[str, Any]:
        return {"height_px": len(spec.variables) * 50 + 120}

    def render(self, spec: VariableMappingSpec, context: dict[str, Any] | None = None) -> CapabilityOutput:
        rows = "".join(f"""
        <tr>
            <td><code class="symbol-code">{v.symbol}</code></td>
            <td><strong>{v.meaning}</strong></td>
            <td><code>{v.si_unit}</code></td>
            <td>{v.typical_value or '—'}</td>
        </tr>
        """ for v in spec.variables)

        html = f"""
        <div class="capability-variable-mapping card">
            <div class="var-header">
                <span class="badge formula-badge">Formula Breakdown</span>
                <h3>{spec.equation_name}: <code>{spec.formula}</code></h3>
            </div>
            <table class="variable-table">
                <thead>
                    <tr>
                        <th>Symbol</th>
                        <th>Physical Meaning</th>
                        <th>SI Unit</th>
                        <th>Notes / Example</th>
                    </tr>
                </thead>
                <tbody>
                    {rows}
                </tbody>
            </table>
        </div>
        """
        return CapabilityOutput(
            capability_id="mathematics.variable_mapping",
            output_format="html",
            rendered_content=html,
            width_px=700,
            height_px=len(spec.variables) * 50 + 120,
        )


variable_mapping_capability = Capability(
    metadata=CapabilityMetadata(
        capability_id="mathematics.variable_mapping",
        category="mathematics",
        display_name="Formula Variable Mapping Table",
        description="Tabular breakdown of variables in an equation with symbols, meanings, SI units, and sample values.",
        semantic_tags=["variable_mapping", "units", "dimensions", "formula_breakdown", "symbols", "si_units"],
        supported_artifacts=["presentation", "document", "worksheet", "poster"],
        domain="mathematics",
        complexity_score=1.5,
        preferred_renderer="html",
        taxonomy=TaxonomySignature(
            family=CapabilityFamily.QUANTITATIVE_ANALYSIS,
            primary_intent=SemanticIntent.EXPLAIN,
            supported_intents=[SemanticIntent.RELATE, SemanticIntent.CLASSIFY],
            structure=InformationStructure.MAPPING,
            pedagogical_role=PedagogicalRole.REFERENCE,
            visual_grammar=VisualGrammar.TABLE,
            density=DensityProfile.DENSE_REFERENCE,
            preferred_formats=["a4_portrait", "a4_landscape", "presentation_16_9"],
        ),
    ),
    spec_model=VariableMappingSpec,
    renderer=VariableMappingRenderer(),
)
