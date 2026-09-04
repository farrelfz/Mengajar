"""
KIR AI Document Generation System — Generative Family Templates.

Implements structural rendering templates across canonical capability families:
- Process (Linear, Vertical, Pipeline)
- Comparison (Matrix, Binary Contrast)
- Hierarchy (Tree, Tiered)
- Reasoning (Evidence Chain)
- Progression (Question Ladder)
- Quantitative (Equation Derivation)
- Relationship (Network / Causal Map)
- Collection (Card Grid)
"""

from __future__ import annotations

import html
from typing import Any

from app.capabilities.contracts import RenderTarget
from app.capabilities.families.contracts import (
    BaseFamilySpec,
    CollectionSpec,
    ComparisonSpec,
    FamilyTemplate,
    HierarchySpec,
    ProcessSpec,
    ProgressionSpec,
    QuantitativeSpec,
    ReasoningSpec,
    RelationshipSpec,
)
from app.capabilities.taxonomy import CapabilityFamily, DensityProfile


# ==============================================================================
# 1. PROCESS FAMILY TEMPLATES
# ==============================================================================

class LinearProcessTemplate(FamilyTemplate[ProcessSpec]):
    """Renders sequential stage flows horizontally or vertically."""
    template_id = "process.linear"
    family = CapabilityFamily.PROCESS_VISUALIZATION
    spec_model = ProcessSpec
    preferred_render_target = RenderTarget.HTML

    def render_html(self, spec: ProcessSpec, context: dict[str, Any] | None = None) -> str:
        title_html = f'<div class="family-title font-bold text-lg mb-3">{html.escape(spec.title)}</div>' if spec.title else ''
        subtitle_html = f'<div class="family-subtitle text-xs text-slate-500 mb-4">{html.escape(spec.subtitle)}</div>' if spec.subtitle else ''

        direction_cls = "flex-col space-y-3" if spec.direction == "vertical" else "flex-row flex-wrap items-stretch gap-3"
        connector_icon = "↓" if spec.direction == "vertical" else "→"

        stages_html = []
        for idx, stage in enumerate(spec.stages, start=1):
            badge_html = f'<span class="px-2 py-0.5 text-2xs font-semibold rounded bg-indigo-100 text-indigo-800 mr-2">{html.escape(stage.badge)}</span>' if stage.badge else ''
            status_cls = "border-indigo-500 bg-indigo-50/50 ring-2 ring-indigo-200" if (spec.emphasis_index == idx - 1 or stage.status == "active") else "border-slate-200 bg-white"

            # Density adaptation
            if spec.density == DensityProfile.MINIMAL:
                card_body = f'<div class="font-semibold text-xs text-slate-800">{html.escape(stage.label)}</div>'
            elif spec.density == DensityProfile.DENSE_REFERENCE:
                meta_rows = "".join([f'<div class="text-2xs text-slate-500"><strong>{html.escape(k)}:</strong> {html.escape(str(v))}</div>' for k, v in stage.meta_info.items()])
                card_body = f'''
                    <div class="font-semibold text-xs text-slate-900 mb-1">{html.escape(stage.label)}</div>
                    <p class="text-2xs text-slate-600 mb-1">{html.escape(stage.description)}</p>
                    <div class="meta-section border-t border-slate-100 pt-1 mt-1">{meta_rows}</div>
                '''
            else:  # FOCUSED or ANALYTICAL
                card_body = f'''
                    <div class="font-semibold text-xs text-slate-900 mb-1">{html.escape(stage.label)}</div>
                    <p class="text-2xs text-slate-600">{html.escape(stage.description)}</p>
                '''

            stage_block = f'''
                <div class="stage-card flex-1 min-w-[140px] p-3 rounded-lg border shadow-xs transition-all {status_cls}">
                    <div class="flex items-center justify-between mb-1.5">
                        <span class="inline-flex items-center justify-center w-5 h-5 rounded-full bg-slate-900 text-white font-mono text-2xs font-bold">{idx}</span>
                        {badge_html}
                    </div>
                    {card_body}
                </div>
            '''
            stages_html.append(stage_block)

            # Connector
            if spec.show_connectors and idx < len(spec.stages):
                stages_html.append(f'<div class="connector flex items-center justify-center text-slate-400 font-bold px-1 text-sm">{connector_icon}</div>')

        return f'''
        <div class="family-container family-process p-4 rounded-xl bg-slate-50/70 border border-slate-200">
            {title_html}
            {subtitle_html}
            <div class="stages-flow flex {direction_cls}">
                {"".join(stages_html)}
            </div>
        </div>
        '''


# ==============================================================================
# 2. COMPARISON FAMILY TEMPLATES
# ==============================================================================

class MatrixComparisonTemplate(FamilyTemplate[ComparisonSpec]):
    """Renders structured multi-axis or binary comparison cards."""
    template_id = "comparison.matrix"
    family = CapabilityFamily.COMPARATIVE_REASONING
    spec_model = ComparisonSpec
    preferred_render_target = RenderTarget.HTML

    def render_html(self, spec: ComparisonSpec, context: dict[str, Any] | None = None) -> str:
        title_html = f'<div class="family-title font-bold text-lg mb-2">{html.escape(spec.title)}</div>' if spec.title else ''
        subtitle_html = f'<div class="family-subtitle text-xs text-slate-500 mb-4">{html.escape(spec.subtitle)}</div>' if spec.subtitle else ''

        columns_count = len(spec.items)
        grid_cls = f"grid grid-cols-1 md:grid-cols-{min(columns_count, 4)} gap-4"

        cards = []
        for item in spec.items:
            tag_html = f'<span class="px-2 py-0.5 text-2xs font-bold rounded uppercase tracking-wider bg-slate-200 text-slate-700">{html.escape(item.tag)}</span>' if item.tag else ''
            highlight_cls = "ring-2 ring-indigo-500 border-indigo-500 shadow-md bg-indigo-50/30" if item.highlight else "border-slate-200 bg-white"

            attr_rows = []
            for axis, val in item.attributes.items():
                is_dim_highlight = (spec.highlight_dimension and spec.highlight_dimension.lower() == axis.lower())
                row_cls = "bg-amber-50/60 font-semibold text-amber-900 rounded p-1" if is_dim_highlight else ""
                attr_rows.append(f'''
                    <div class="attribute-row mb-2 pb-1 border-b border-slate-100 last:border-0 {row_cls}">
                        <span class="block text-3xs uppercase font-bold text-slate-400">{html.escape(axis)}</span>
                        <span class="text-xs text-slate-700">{html.escape(val)}</span>
                    </div>
                ''')

            cards.append(f'''
                <div class="comparison-card p-4 rounded-xl border flex flex-col justify-between {highlight_cls}">
                    <div>
                        <div class="flex items-center justify-between mb-3">
                            <h4 class="font-bold text-sm text-slate-900">{html.escape(item.name)}</h4>
                            {tag_html}
                        </div>
                        <div class="attributes-body mt-2">
                            {"".join(attr_rows)}
                        </div>
                    </div>
                </div>
            ''')

        return f'''
        <div class="family-container family-comparison p-4 rounded-xl bg-slate-50/70 border border-slate-200">
            {title_html}
            {subtitle_html}
            <div class="{grid_cls}">
                {"".join(cards)}
            </div>
        </div>
        '''


# ==============================================================================
# 3. HIERARCHY FAMILY TEMPLATES
# ==============================================================================

class HierarchyTreeTemplate(FamilyTemplate[HierarchySpec]):
    """Renders structured hierarchical tree or level-based classification."""
    template_id = "hierarchy.tree"
    family = CapabilityFamily.CONCEPT_STRUCTURE
    spec_model = HierarchySpec
    preferred_render_target = RenderTarget.HTML

    def render_html(self, spec: HierarchySpec, context: dict[str, Any] | None = None) -> str:
        title_html = f'<div class="family-title font-bold text-lg mb-2">{html.escape(spec.title)}</div>' if spec.title else ''
        subtitle_html = f'<div class="family-subtitle text-xs text-slate-500 mb-4">{html.escape(spec.subtitle)}</div>' if spec.subtitle else ''

        # Group nodes by level
        level_map: dict[int, list] = {}
        for n in spec.nodes:
            level_map.setdefault(n.level, []).append(n)

        level_blocks = []
        for lvl in sorted(level_map.keys()):
            nodes = level_map[lvl]
            node_cards = []
            for n in nodes:
                badge_html = f'<span class="text-3xs px-1.5 py-0.5 rounded bg-indigo-100 text-indigo-700 font-bold ml-2">{html.escape(n.badge)}</span>' if n.badge else ''
                node_cards.append(f'''
                    <div class="hierarchy-node p-3 rounded-lg border border-slate-200 bg-white shadow-xs min-w-[130px] flex-1 text-center">
                        <div class="font-bold text-xs text-slate-900">{html.escape(n.label)}{badge_html}</div>
                        {f'<p class="text-3xs text-slate-500 mt-1">{html.escape(n.description)}</p>' if n.description else ''}
                    </div>
                ''')
            
            level_blocks.append(f'''
                <div class="level-row flex items-center justify-center gap-3 w-full">
                    {"".join(node_cards)}
                </div>
            ''')
            if lvl < max(level_map.keys()):
                level_blocks.append('<div class="level-connector flex justify-center text-slate-300 font-bold text-xs">│</div>')

        return f'''
        <div class="family-container family-hierarchy p-4 rounded-xl bg-slate-50/70 border border-slate-200">
            {title_html}
            {subtitle_html}
            <div class="hierarchy-tree flex flex-col items-center space-y-2">
                {"".join(level_blocks)}
            </div>
        </div>
        '''


# ==============================================================================
# 4. REASONING FAMILY TEMPLATES
# ==============================================================================

class EvidenceChainTemplate(FamilyTemplate[ReasoningSpec]):
    """Renders structured logical inference chains (Claim -> Evidence -> Warrant -> Conclusion)."""
    template_id = "reasoning.evidence_chain"
    family = CapabilityFamily.EVIDENCE_ANALYSIS
    spec_model = ReasoningSpec
    preferred_render_target = RenderTarget.HTML

    def render_html(self, spec: ReasoningSpec, context: dict[str, Any] | None = None) -> str:
        title_html = f'<div class="family-title font-bold text-lg mb-2">{html.escape(spec.title)}</div>' if spec.title else ''
        subtitle_html = f'<div class="family-subtitle text-xs text-slate-500 mb-4">{html.escape(spec.subtitle)}</div>' if spec.subtitle else ''

        role_styles = {
            "premise": "border-slate-300 bg-slate-50 text-slate-800",
            "claim": "border-blue-300 bg-blue-50/60 text-blue-950",
            "evidence": "border-amber-300 bg-amber-50/60 text-amber-950",
            "warrant": "border-purple-300 bg-purple-50/60 text-purple-950",
            "conclusion": "border-emerald-500 bg-emerald-50 text-emerald-950 ring-2 ring-emerald-200",
        }

        cards = []
        for idx, elem in enumerate(spec.elements, start=1):
            style = role_styles.get(elem.role.lower(), "border-slate-200 bg-white text-slate-900")
            badge_text = elem.badge or elem.role.upper()
            data_html = f'<div class="text-3xs text-slate-500 mt-2 italic font-mono bg-white/70 p-1 rounded border border-slate-100">Data/Ref: {html.escape(elem.citation_or_data)}</div>' if elem.citation_or_data else ''

            cards.append(f'''
                <div class="reasoning-step flex-1 min-w-[150px] p-3 rounded-lg border {style} shadow-xs">
                    <div class="flex items-center justify-between mb-1.5">
                        <span class="text-3xs font-mono font-bold uppercase tracking-wider">{badge_text}</span>
                        <span class="text-2xs font-mono font-bold opacity-60">#{idx}</span>
                    </div>
                    <div class="text-xs font-medium">{html.escape(elem.statement)}</div>
                    {data_html}
                </div>
            ''')
            if idx < len(spec.elements):
                cards.append('<div class="connector flex items-center justify-center text-slate-300 font-bold text-sm">→</div>')

        return f'''
        <div class="family-container family-reasoning p-4 rounded-xl bg-slate-50/70 border border-slate-200">
            {title_html}
            {subtitle_html}
            <div class="reasoning-flow flex flex-row flex-wrap items-stretch gap-2">
                {"".join(cards)}
            </div>
        </div>
        '''


# ==============================================================================
# 5. PROGRESSION FAMILY TEMPLATES
# ==============================================================================

class ProgressionLadderTemplate(FamilyTemplate[ProgressionSpec]):
    """Renders structured cognitive progression ladder (Bloom's taxonomy scaffolding)."""
    template_id = "progression.ladder"
    family = CapabilityFamily.STEPWISE_REASONING
    spec_model = ProgressionSpec
    preferred_render_target = RenderTarget.HTML

    def render_html(self, spec: ProgressionSpec, context: dict[str, Any] | None = None) -> str:
        title_html = f'<div class="family-title font-bold text-lg mb-2">{html.escape(spec.title)}</div>' if spec.title else ''
        subtitle_html = f'<div class="family-subtitle text-xs text-slate-500 mb-4">{html.escape(spec.subtitle)}</div>' if spec.subtitle else ''

        stages_html = []
        for stage in sorted(spec.stages, key=lambda s: s.level):
            guidance_html = f'<div class="guidance-block mt-2 p-1.5 rounded bg-indigo-50/80 text-2xs text-indigo-900 font-sans border border-indigo-100">💡 <strong>Focus:</strong> {html.escape(stage.answer_or_guidance)}</div>' if stage.answer_or_guidance else ''

            stages_html.append(f'''
                <div class="ladder-stage flex items-start gap-3 p-3 rounded-lg border border-slate-200 bg-white mb-2 shadow-xs">
                    <div class="level-badge flex flex-col items-center justify-center w-8 h-8 rounded-lg bg-slate-900 text-white font-mono text-xs font-bold shrink-0">
                        L{stage.level}
                    </div>
                    <div class="stage-content flex-1">
                        <div class="flex items-center justify-between">
                            <h4 class="font-bold text-xs text-slate-900">{html.escape(stage.title)}</h4>
                            <span class="text-3xs uppercase font-mono px-2 py-0.5 rounded bg-slate-100 text-slate-600">{html.escape(stage.cognitive_dimension)}</span>
                        </div>
                        <p class="text-xs text-slate-700 mt-1">{html.escape(stage.prompt_or_question)}</p>
                        {guidance_html}
                    </div>
                </div>
            ''')

        return f'''
        <div class="family-container family-progression p-4 rounded-xl bg-slate-50/70 border border-slate-200">
            {title_html}
            {subtitle_html}
            <div class="ladder-container">
                {"".join(stages_html)}
            </div>
        </div>
        '''


# ==============================================================================
# 6. QUANTITATIVE FAMILY TEMPLATES
# ==============================================================================

class QuantitativeDerivationTemplate(FamilyTemplate[QuantitativeSpec]):
    """Renders mathematical equation derivations and transformation sequences."""
    template_id = "quantitative.derivation"
    family = CapabilityFamily.STEPWISE_REASONING
    spec_model = QuantitativeSpec
    preferred_render_target = RenderTarget.HTML

    def render_html(self, spec: QuantitativeSpec, context: dict[str, Any] | None = None) -> str:
        title_html = f'<div class="family-title font-bold text-lg mb-2">{html.escape(spec.title)}</div>' if spec.title else ''
        subtitle_html = f'<div class="family-subtitle text-xs text-slate-500 mb-4">{html.escape(spec.subtitle)}</div>' if spec.subtitle else ''

        vars_html = ""
        if spec.variables:
            var_items = "".join([f'<span class="px-2 py-1 bg-slate-100 rounded text-3xs font-mono"><strong>{html.escape(k)}</strong> = {html.escape(v)}</span>' for k, v in spec.variables.items()])
            vars_html = f'<div class="variables-bar flex flex-wrap gap-2 mb-3 p-2 bg-slate-50 rounded-lg border border-slate-200">{var_items}</div>'

        steps_html = []
        for step in spec.steps:
            steps_html.append(f'''
                <div class="derivation-step flex items-start gap-3 p-2.5 rounded-lg border border-slate-200 bg-white mb-2 shadow-xs">
                    <span class="font-mono text-2xs font-bold text-slate-400 shrink-0 mt-0.5">[{step.step_number}]</span>
                    <div class="flex-1">
                        <div class="flex items-center justify-between mb-1">
                            <span class="text-3xs uppercase font-bold text-indigo-600">{html.escape(step.operation)}</span>
                        </div>
                        <div class="font-mono text-xs font-bold text-slate-900 bg-slate-50 p-2 rounded border border-slate-100">{html.escape(step.formula)}</div>
                        {f'<p class="text-2xs text-slate-500 mt-1">{html.escape(step.explanation)}</p>' if step.explanation else ''}
                    </div>
                </div>
            ''')

        final_html = f'''
            <div class="final-result-card mt-3 p-3 rounded-lg bg-emerald-50 border border-emerald-300 flex items-center justify-between">
                <span class="font-bold text-xs text-emerald-900">Final Result:</span>
                <span class="font-mono font-bold text-sm text-emerald-950">{html.escape(spec.final_result or "")}</span>
            </div>
        ''' if spec.final_result else ''

        return f'''
        <div class="family-container family-quantitative p-4 rounded-xl bg-slate-50/70 border border-slate-200">
            {title_html}
            {subtitle_html}
            <div class="initial-formula mb-3 p-3 rounded-lg bg-slate-900 text-white font-mono text-xs font-bold flex justify-between items-center">
                <span>Governing Principle:</span>
                <span>{html.escape(spec.initial_formula)}</span>
            </div>
            {vars_html}
            <div class="derivation-steps">
                {"".join(steps_html)}
            </div>
            {final_html}
        </div>
        '''


# ==============================================================================
# 7. RELATIONSHIP FAMILY TEMPLATES
# ==============================================================================

class RelationshipMapTemplate(FamilyTemplate[RelationshipSpec]):
    """Renders directed node-edge causal and relational factor networks."""
    template_id = "relationship.network"
    family = CapabilityFamily.RELATIONSHIP_MAPPING
    spec_model = RelationshipSpec
    preferred_render_target = RenderTarget.HTML

    def render_html(self, spec: RelationshipSpec, context: dict[str, Any] | None = None) -> str:
        title_html = f'<div class="family-title font-bold text-lg mb-2">{html.escape(spec.title)}</div>' if spec.title else ''
        subtitle_html = f'<div class="family-subtitle text-xs text-slate-500 mb-4">{html.escape(spec.subtitle)}</div>' if spec.subtitle else ''

        nodes_html = []
        for node in spec.nodes:
            nodes_html.append(f'''
                <div class="node-card p-2.5 rounded-lg border border-slate-300 bg-white shadow-xs min-w-[120px] text-center flex-1">
                    <span class="text-3xs uppercase font-mono font-bold text-slate-400 block">{html.escape(node.category)}</span>
                    <span class="text-xs font-bold text-slate-900">{html.escape(node.label)}</span>
                </div>
            ''')

        edges_html = []
        for edge in spec.edges:
            edges_html.append(f'''
                <div class="edge-row flex items-center justify-between text-2xs p-1.5 rounded bg-slate-100 font-mono text-slate-700">
                    <span class="font-bold">{html.escape(edge.source_id)}</span>
                    <span class="text-slate-400">──({html.escape(edge.label or edge.relation_type)})──▶</span>
                    <span class="font-bold">{html.escape(edge.target_id)}</span>
                </div>
            ''')

        return f'''
        <div class="family-container family-relationship p-4 rounded-xl bg-slate-50/70 border border-slate-200">
            {title_html}
            {subtitle_html}
            <div class="nodes-grid flex flex-wrap gap-3 mb-3">
                {"".join(nodes_html)}
            </div>
            <div class="edges-list space-y-1.5 border-t border-slate-200 pt-3">
                <span class="text-3xs font-bold uppercase tracking-wider text-slate-400 block mb-1">Causal & Relational Links</span>
                {"".join(edges_html)}
            </div>
        </div>
        '''


# ==============================================================================
# 8. COLLECTION FAMILY TEMPLATES
# ==============================================================================

class CardCollectionTemplate(FamilyTemplate[CollectionSpec]):
    """Renders grouped informational or definition cards in a multi-column grid."""
    template_id = "collection.grid"
    family = CapabilityFamily.CONCEPT_STRUCTURE
    spec_model = CollectionSpec
    preferred_render_target = RenderTarget.HTML

    def render_html(self, spec: CollectionSpec, context: dict[str, Any] | None = None) -> str:
        title_html = f'<div class="family-title font-bold text-lg mb-2">{html.escape(spec.title)}</div>' if spec.title else ''
        subtitle_html = f'<div class="family-subtitle text-xs text-slate-500 mb-4">{html.escape(spec.subtitle)}</div>' if spec.subtitle else ''

        grid_cols = f"grid-cols-1 md:grid-cols-{min(spec.columns, 4)}"
        cards = []
        for item in spec.items:
            cat_html = f'<span class="text-3xs font-mono uppercase px-1.5 py-0.5 rounded bg-slate-100 text-slate-600">{html.escape(item.category)}</span>' if item.category else ''
            cards.append(f'''
                <div class="collection-item-card p-3 rounded-lg border border-slate-200 bg-white shadow-xs flex flex-col justify-between">
                    <div>
                        <div class="flex items-center justify-between mb-1.5">
                            <h4 class="font-bold text-xs text-slate-900">{html.escape(item.title)}</h4>
                            {cat_html}
                        </div>
                        <p class="text-xs text-slate-600">{html.escape(item.content)}</p>
                    </div>
                </div>
            ''')

        return f'''
        <div class="family-container family-collection p-4 rounded-xl bg-slate-50/70 border border-slate-200">
            {title_html}
            {subtitle_html}
            <div class="grid {grid_cols} gap-3">
                {"".join(cards)}
            </div>
        </div>
        '''
