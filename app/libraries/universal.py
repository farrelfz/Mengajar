"""
KIR AI Document Intelligence — Universal Capability Library.

Cross-domain reusable capabilities:
- Multi-Entity Comparison Matrix
- Concept Hierarchy Tree
- Evidence Reasoning Chain
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
from app.capabilities.taxonomy import (
    CapabilityFamily,
    DensityProfile,
    InformationStructure,
    PedagogicalRole,
    SemanticIntent,
    TaxonomySignature,
    VisualGrammar,
)


# =====================================================================
# 1. Multi-Entity Comparison Matrix
# =====================================================================

class ComparisonCriterion(BaseModel):
    name: str
    values: dict[str, str] = Field(default_factory=dict)


class ComparisonMatrixSpec(CapabilitySpec):
    matrix_title: str = "Comparative Evaluation"
    entities: list[str] = Field(default_factory=lambda: ["Option A", "Option B"])
    criteria: list[ComparisonCriterion] = Field(default_factory=list)


class ComparisonMatrixRenderer(CapabilityRenderer[ComparisonMatrixSpec]):

    def validate_spec(self, spec: ComparisonMatrixSpec) -> bool:
        return len(spec.entities) >= 2 and len(spec.criteria) > 0

    def measure(self, spec: ComparisonMatrixSpec, context: dict[str, Any] | None = None) -> dict[str, Any]:
        return {"height_px": len(spec.criteria) * 60 + 140}

    def render(self, spec: ComparisonMatrixSpec, context: dict[str, Any] | None = None) -> CapabilityOutput:
        header_th = "".join(f"<th>{e}</th>" for e in spec.entities)
        rows_html = ""
        for crit in spec.criteria:
            tds = "".join(f"<td>{crit.values.get(e, '—')}</td>" for e in spec.entities)
            rows_html += f"""
            <tr>
                <td class="crit-name"><strong>{crit.name}</strong></td>
                {tds}
            </tr>
            """

        html = f"""
        <div class="capability-comparison-matrix card">
            <div class="matrix-header">
                <span class="badge matrix-badge">Comparative Analysis</span>
                <h3>{spec.matrix_title}</h3>
            </div>
            <table class="comparison-table">
                <thead>
                    <tr>
                        <th>Evaluation Dimension</th>
                        {header_th}
                    </tr>
                </thead>
                <tbody>
                    {rows_html}
                </tbody>
            </table>
        </div>
        """
        return CapabilityOutput(
            capability_id="universal.comparison_matrix",
            output_format="html",
            rendered_content=html,
            width_px=800,
            height_px=len(spec.criteria) * 60 + 140,
        )


def _extract_comparison_matrix(step: Any, material: Any) -> dict[str, Any]:
    title = material.content.metadata.title
    return {
        "matrix_title": f"Comparative Matrix: {title}",
        "entities": ["Qualitative Approach", "Quantitative Approach"],
        "criteria": [
            ComparisonCriterion(name="Core Objective", values={"Qualitative Approach": "Exploration & Deep Meaning", "Quantitative Approach": "Hypothesis Testing & Measurement"}),
            ComparisonCriterion(name="Data Instrument", values={"Qualitative Approach": "Interviews & Observations", "Quantitative Approach": "Surveys & Sensors"}),
            ComparisonCriterion(name="Generalizability", values={"Qualitative Approach": "Context-Specific", "Quantitative Approach": "Statistically Generalizable"}),
        ],
    }


comparison_matrix_capability = Capability(
    metadata=CapabilityMetadata(
        capability_id="universal.comparison_matrix",
        category="universal",
        display_name="Multi-Entity Comparison Matrix",
        description="Structured table comparing two or more entities across consistent analytical criteria.",
        semantic_tags=["comparison", "compare", "matrix", "evaluation", "contrast", "pros_cons", "tradeoffs"],
        supported_artifacts=["presentation", "document", "poster", "worksheet"],
        domain="general",
        complexity_score=2.0,
        preferred_renderer="html",
        taxonomy=TaxonomySignature(
            family=CapabilityFamily.COMPARATIVE_REASONING,
            primary_intent=SemanticIntent.COMPARE,
            supported_intents=[SemanticIntent.ANALYZE, SemanticIntent.EVALUATE],
            structure=InformationStructure.MATRIX,
            pedagogical_role=PedagogicalRole.ANALYSIS,
            visual_grammar=VisualGrammar.COMPARISON,
            density=DensityProfile.ANALYTICAL,
            preferred_formats=["a4_portrait", "a4_landscape", "presentation_16_9"],
        ),
    ),
    spec_model=ComparisonMatrixSpec,
    renderer=ComparisonMatrixRenderer(),
    parameter_extractor=_extract_comparison_matrix,
)


# =====================================================================
# 2. Concept Hierarchy Tree
# =====================================================================

class HierarchyNode(BaseModel):
    node_id: str
    label: str
    parent_id: str | None = None
    description: str | None = None


class ConceptHierarchySpec(CapabilitySpec):
    root_title: str = "Taxonomy Architecture"
    nodes: list[HierarchyNode] = Field(default_factory=list)


class ConceptHierarchyRenderer(CapabilityRenderer[ConceptHierarchySpec]):

    def validate_spec(self, spec: ConceptHierarchySpec) -> bool:
        return len(spec.nodes) > 0

    def measure(self, spec: ConceptHierarchySpec, context: dict[str, Any] | None = None) -> dict[str, Any]:
        return {"height_px": 320}

    def render(self, spec: ConceptHierarchySpec, context: dict[str, Any] | None = None) -> CapabilityOutput:
        nodes_html = ""
        for n in spec.nodes:
            nodes_html += f"""
            <div class="hierarchy-item {'root-item' if not n.parent_id else 'sub-item'}">
                <div class="node-badge">●</div>
                <div class="node-content">
                    <span class="node-label">{n.label}</span>
                    {f'<p class="node-desc">{n.description}</p>' if n.description else ''}
                </div>
            </div>
            """

        html = f"""
        <div class="capability-concept-hierarchy card">
            <div class="hierarchy-header">
                <span class="badge hier-badge">Classification Structure</span>
                <h3>{spec.root_title}</h3>
            </div>
            <div class="hierarchy-tree-container">
                {nodes_html}
            </div>
        </div>
        """
        return CapabilityOutput(
            capability_id="universal.concept_hierarchy",
            output_format="html",
            rendered_content=html,
            width_px=750,
            height_px=320,
        )


def _extract_concept_hierarchy(step: Any, material: Any) -> dict[str, Any]:
    title = material.content.metadata.title
    return {
        "root_title": f"Structural Hierarchy: {title}",
        "nodes": [
            HierarchyNode(node_id="root", label=title, description="Root Concept & Principle"),
            HierarchyNode(node_id="sub1", label="Foundational Components", parent_id="root", description="Core theoretical axioms"),
            HierarchyNode(node_id="sub2", label="Applied Operations", parent_id="root", description="Practical implementation domains"),
        ],
    }


concept_hierarchy_capability = Capability(
    metadata=CapabilityMetadata(
        capability_id="universal.concept_hierarchy",
        category="universal",
        display_name="Concept Hierarchy & Taxonomy Tree",
        description="Hierarchical breakdown showing taxonomic parent-child conceptual relationships.",
        semantic_tags=["hierarchy", "taxonomy", "classification", "tree", "categorization", "subtypes"],
        supported_artifacts=["presentation", "document", "poster", "worksheet"],
        domain="general",
        complexity_score=2.0,
        preferred_renderer="html",
        taxonomy=TaxonomySignature(
            family=CapabilityFamily.CONCEPT_STRUCTURE,
            primary_intent=SemanticIntent.CLASSIFY,
            supported_intents=[SemanticIntent.EXPLAIN, SemanticIntent.SYNTHESIZE],
            structure=InformationStructure.HIERARCHY,
            pedagogical_role=PedagogicalRole.SCAFFOLD,
            visual_grammar=VisualGrammar.CONCEPT_MAP,
            density=DensityProfile.FOCUSED,
            preferred_formats=["presentation_16_9", "a4_landscape", "a4_portrait"],
        ),
    ),
    spec_model=ConceptHierarchySpec,
    renderer=ConceptHierarchyRenderer(),
    parameter_extractor=_extract_concept_hierarchy,
)


# =====================================================================
# 3. Evidence Reasoning Chain
# =====================================================================

class EvidenceLink(BaseModel):
    step_num: int
    claim: str
    grounded_evidence: str
    warrant: str


class EvidenceChainSpec(CapabilitySpec):
    argument_claim: str
    links: list[EvidenceLink] = Field(default_factory=list)


class EvidenceChainRenderer(CapabilityRenderer[EvidenceChainSpec]):

    def validate_spec(self, spec: EvidenceChainSpec) -> bool:
        return bool(spec.argument_claim and len(spec.links) > 0)

    def measure(self, spec: EvidenceChainSpec, context: dict[str, Any] | None = None) -> dict[str, Any]:
        return {"height_px": len(spec.links) * 90 + 130}

    def render(self, spec: EvidenceChainSpec, context: dict[str, Any] | None = None) -> CapabilityOutput:
        links_html = ""
        for l in spec.links:
            links_html += f"""
            <div class="evidence-step-card">
                <div class="link-num">{l.step_num}</div>
                <div class="link-body">
                    <div class="link-claim"><strong>Premise:</strong> {l.claim}</div>
                    <div class="link-evidence"><strong>Evidence:</strong> {l.grounded_evidence}</div>
                    <div class="link-warrant"><strong>Scientific Warrant:</strong> {l.warrant}</div>
                </div>
            </div>
            """

        html = f"""
        <div class="capability-evidence-chain card">
            <div class="chain-header">
                <span class="badge arg-badge">Evidence-Grounded Argument</span>
                <h3>Target Conclusion: {spec.argument_claim}</h3>
            </div>
            <div class="chain-links-list">
                {links_html}
            </div>
        </div>
        """
        return CapabilityOutput(
            capability_id="universal.evidence_chain",
            output_format="html",
            rendered_content=html,
            width_px=750,
            height_px=len(spec.links) * 90 + 130,
        )


def _extract_evidence_chain(step: Any, material: Any) -> dict[str, Any]:
    title = material.content.metadata.title
    return {
        "argument_claim": f"Grounded scientific deduction for {title}",
        "links": [
            EvidenceLink(step_num=1, claim="Observed empirical regularity", grounded_evidence="Consistent measurement records across trials", warrant="Inductive consistency principle"),
            EvidenceLink(step_num=2, claim="Theoretical alignment", grounded_evidence="Governing conservation laws", warrant="Deductive law conformity"),
        ],
    }


evidence_chain_capability = Capability(
    metadata=CapabilityMetadata(
        capability_id="universal.evidence_chain",
        category="universal",
        display_name="Evidence Reasoning Chain",
        description="Structured Toulmin-style argument chain connecting premises, empirical evidence, and scientific warrants.",
        semantic_tags=["argument", "evidence", "claim", "reasoning_chain", "proof", "warrant", "deduction"],
        supported_artifacts=["presentation", "document", "poster", "worksheet"],
        domain="general",
        complexity_score=2.5,
        preferred_renderer="html",
        taxonomy=TaxonomySignature(
            family=CapabilityFamily.EVIDENCE_ANALYSIS,
            primary_intent=SemanticIntent.ARGUE,
            supported_intents=[SemanticIntent.SYNTHESIZE, SemanticIntent.ANALYZE],
            structure=InformationStructure.EVIDENCE_CHAIN,
            pedagogical_role=PedagogicalRole.SYNTHESIS,
            visual_grammar=VisualGrammar.REASONING_FLOW,
            density=DensityProfile.ANALYTICAL,
            preferred_formats=["presentation_16_9", "a4_portrait", "a4_landscape"],
        ),
    ),
    spec_model=EvidenceChainSpec,
    renderer=EvidenceChainRenderer(),
    parameter_extractor=_extract_evidence_chain,
)
