"""
KIR AI Document Intelligence — Presentation Composition Library.

Provides parameterized components for presentation slides:
- Hero Statement (Hook, Big Question, Impact Metric)
- Concept Introduction (Definition, Visual, Analogy)
- Two-Column Comparison (Before vs After, Model A vs Model B)
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


class HeroStatementSpec(CapabilitySpec):
    headline: str
    subheadline: str | None = None
    supporting_quote: str | None = None
    tag: str = "Key Idea"
    highlight_number: str | None = None
    highlight_label: str | None = None


class HeroStatementRenderer(CapabilityRenderer[HeroStatementSpec]):

    def validate_spec(self, spec: HeroStatementSpec) -> bool:
        return bool(spec.headline)

    def measure(self, spec: HeroStatementSpec, context: dict[str, Any] | None = None) -> dict[str, Any]:
        return {"height_px": 300, "density": "expansive"}

    def render(self, spec: HeroStatementSpec, context: dict[str, Any] | None = None) -> CapabilityOutput:
        metric_part = ""
        if spec.highlight_number:
            metric_part = f"""
            <div class="hero-metric-box">
                <div class="metric-num">{spec.highlight_number}</div>
                <div class="metric-lbl">{spec.highlight_label or ''}</div>
            </div>
            """

        html = f"""
        <div class="capability-hero-slide">
            <span class="badge hero-badge">{spec.tag}</span>
            <h1 class="hero-headline">{spec.headline}</h1>
            {f'<p class="hero-subheadline">{spec.subheadline}</p>' if spec.subheadline else ''}
            {metric_part}
            {f'<blockquote class="hero-quote">"{spec.supporting_quote}"</blockquote>' if spec.supporting_quote else ''}
        </div>
        """
        return CapabilityOutput(
            capability_id="presentation.hero_statement",
            output_format="html",
            rendered_content=html,
            width_px=800,
            height_px=320,
        )


def _extract_hero_statement(step: Any, material: Any) -> dict[str, Any]:
    title = material.content.metadata.title
    domain_val = material.content.metadata.domain.value if hasattr(material.content.metadata.domain, "value") else str(material.content.metadata.domain)
    return {
        "headline": title,
        "subheadline": step.purpose if hasattr(step, "purpose") else None,
        "tag": domain_val.replace("_", " ").title(),
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


hero_statement_capability = Capability(
    metadata=CapabilityMetadata(
        capability_id="presentation.hero_statement",
        category="presentation",
        display_name="Hero Statement Slide",
        description="High-impact slide with big headline, subheadline, highlighted metric, and conceptual hook.",
        semantic_tags=["hero_statement", "hook", "big_question", "opening", "impact_statement", "title_slide"],
        supported_artifacts=["presentation", "poster"],
        domain="general",
        complexity_score=1.0,
        preferred_renderer="html",
        taxonomy=TaxonomySignature(
            family=CapabilityFamily.TITLE_FRAMING,
            primary_intent=SemanticIntent.HOOK,
            supported_intents=[SemanticIntent.INTRODUCE, SemanticIntent.EXPLAIN],
            structure=InformationStructure.SINGLE_ENTITY,
            pedagogical_role=PedagogicalRole.HOOK,
            visual_grammar=VisualGrammar.HERO,
            density=DensityProfile.MINIMAL,
            preferred_formats=["presentation_16_9", "a4_landscape"],
        ),
    ),
    spec_model=HeroStatementSpec,
    renderer=HeroStatementRenderer(),
    parameter_extractor=_extract_hero_statement,
)


class ConceptIntroSpec(CapabilitySpec):
    concept_name: str
    formal_definition: str
    intuitive_analogy: str | None = None
    key_characteristics: list[str] = Field(default_factory=list)


class ConceptIntroRenderer(CapabilityRenderer[ConceptIntroSpec]):

    def validate_spec(self, spec: ConceptIntroSpec) -> bool:
        return bool(spec.concept_name and spec.formal_definition)

    def measure(self, spec: ConceptIntroSpec, context: dict[str, Any] | None = None) -> dict[str, Any]:
        return {"height_px": 320}

    def render(self, spec: ConceptIntroSpec, context: dict[str, Any] | None = None) -> CapabilityOutput:
        chars_html = "".join(f"<li>{c}</li>" for c in spec.key_characteristics)
        html = f"""
        <div class="capability-concept-intro card">
            <div class="concept-badge-row">
                <span class="badge concept-badge">Concept Focus</span>
            </div>
            <h2 class="concept-title">{spec.concept_name}</h2>
            <div class="concept-def-box">
                <p class="formal-def"><strong>Definition:</strong> {spec.formal_definition}</p>
            </div>
            {f'<div class="analogy-box">💡 <strong>Intuition & Analogy:</strong> {spec.intuitive_analogy}</div>' if spec.intuitive_analogy else ''}
            {f'<div class="characteristics-list"><h4>Key Properties:</h4><ul>{chars_html}</ul></div>' if chars_html else ''}
        </div>
        """
        return CapabilityOutput(
            capability_id="presentation.concept_introduction",
            output_format="html",
            rendered_content=html,
            width_px=800,
            height_px=320,
        )


def _extract_concept_intro(step: Any, material: Any) -> dict[str, Any]:
    title = material.content.metadata.title
    concept = material.content.concepts[0] if material.content.concepts else None
    return {
        "concept_name": concept.name if concept else title,
        "formal_definition": concept.formal_definition if concept else (step.purpose if hasattr(step, "purpose") else title),
        "intuitive_analogy": concept.intuitive_explanation if concept else None,
        "key_characteristics": [f.statement[:80] for f in material.content.facts[:3]] if material.content.facts else [],
    }


concept_intro_capability = Capability(
    metadata=CapabilityMetadata(
        capability_id="presentation.concept_introduction",
        category="presentation",
        display_name="Concept Introduction Panel",
        description="Structured introduction of a core concept including definition, intuitive analogy, and properties.",
        semantic_tags=["concept", "concept_intro", "definition", "phenomenon", "fundamental_theory"],
        supported_artifacts=["presentation", "document", "worksheet", "poster"],
        domain="general",
        complexity_score=1.5,
        preferred_renderer="html",
        taxonomy=TaxonomySignature(
            family=CapabilityFamily.CONCEPT_STRUCTURE,
            primary_intent=SemanticIntent.INTRODUCE,
            supported_intents=[SemanticIntent.EXPLAIN, SemanticIntent.CLASSIFY],
            structure=InformationStructure.SINGLE_ENTITY,
            pedagogical_role=PedagogicalRole.INTRODUCTION,
            visual_grammar=VisualGrammar.CONCEPT_PANEL,
            density=DensityProfile.FOCUSED,
            preferred_formats=["presentation_16_9", "a4_portrait", "a4_landscape"],
        ),
    ),
    spec_model=ConceptIntroSpec,
    renderer=ConceptIntroRenderer(),
    parameter_extractor=_extract_concept_intro,
)
