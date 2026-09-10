# UNIVERSAL DOCUMENT INTELLIGENCE SYSTEM V5
# PHASE 4 — REPAIR ACTUATION & STRUCTURAL RECOMPOSITION FORENSIC AUDIT

**System:** Universal Document Intelligence System V5  
**Stage:** Phase 4 — Phase 0 Forensic Capability Audit  
**Status:** COMPLETE & VERIFIED  
**Date:** 2026-09-06  

---

## 1. Executive Forensic Summary

In Phase 3D.1, the repair governance and convergence controller achieved zero-leakage strategy filtering, self-disqualification, and causal reach matching. However, golden benchmark replay proved that when confronted with **structural and semantic defects**, the pipeline halts at `MANUAL_REVIEW_REQUIRED` because the existing repair strategies lack **executable actuation capability**.

The existing repair strategies in `app/quality/repair/strategies/` were largely declarative metadata mutators:
1. `presentation_component_reflow` declared that it resolved `ELEMENT_COLLISION`, but only toggled a string in `slide.layout` or `beat.visual_priority`. The renderer adapter ignored `"COMPARISON_GRID"`, resulting in a `ZERO_EFFECT_MUTATION`.
2. `worksheet_layout_alternation` declared that it resolved `REPETITION_STREAK`, but merely cycled strings in `expected_reasoning_type`. The worksheet bridge template ignored this field, leaving the 15-page question monotony intact.
3. `worksheet_workspace_expansion` and `worksheet_typography_scale` only mutated string metadata in `scaffolding_level` without injecting renderer-level layout or typography styles.

Phase 4 bridges this gap by introducing the **Repair Actuation & Structural Recomposition Engine**:
$$\text{Finding} \rightarrow \text{Root Cause} \rightarrow \text{Causal Reach} \rightarrow \text{Repair Strategy} \rightarrow \mathbf{Actuation\ Operator} \rightarrow \mathbf{Artifact\ Transformation} \rightarrow \text{Re-render} \rightarrow \text{Quality Authority}$$

---

## 2. Forensic CodeGraph Exploration Map

The CodeGraph exploration of `.codegraph/` traced all transformation and repair surfaces:
- **Strategy Definitions**: `app/quality/repair/strategies/` (`base.py`, `presentation.py`, `worksheet.py`, `handout.py`, `scientific.py`)
- **Refinement Operators**: `app/refinement/patches.py` (`BaseRefinementPatch`, `DensitySplitPatch`, `PedagogicalSequencePatch`, `CapabilityReplacementPatch`)
- **Presentation Rendering Pipeline**: `app/presentation/slide_generator.py` (`SlideGenerator`, `_render_formula`, `_render_hero`, `_render_concept`), `app/presentation/visual_grammar_registry.py`
- **Adapter & Grouping Logic**: `app/integration/renderer_adapters/presentation_adapter.py` (`PresentationContractAdapter`), `app/integration/artifact_bridge/presentation_bridge.py`
- **Worksheet Bridge & Rendering**: `app/integration/artifact_bridge/worksheet_bridge.py`, `app/integration/render_execution/worksheet_executor.py`
- **Quality Authority & PDF Inspection**: `app/quality/rendered/pdf_inspector.py` (detects `ELEMENT_COLLISION` when block overlap > 20 sq pt; detects `TEXT_TOO_SMALL` when font < 11.0pt / 9.5pt)

---

## 3. Explicit Forensic Capability Audit (Questions A through H)

### Question A: Which repair strategies currently have REAL mutation operators?
1. `presentation_density_split`: Performs real semantic splitting of `PlannedSlide` (`key_blocks` / `claim_units`) or `ConceptualBeat` (`supporting_unit_ids` and cognitive load).
2. `worksheet_anti_spoiling_repair`: Performs real prompt regex sanitization, stripping explanatory leakage while setting `withhold_explanation=True`.
3. `worksheet_inquiry_sequence_repair`: Performs real sorting of activities according to the canonical inquiry arc (`PHENOMENON` $\to$ `PREDICTION` $\to$ `INVESTIGATION` $\to$ `OBSERVATION` $\to$ `DATA_ANALYSIS` $\to$ `REFLECTION`).
4. `handout_pagination_consolidation`: Performs real merging/splitting of `ExplanatorySection` items and heading level shifts.
5. `scientific_claim_downgrade` & `scientific_evidence_mapping`: Performs real confidence downgrade and evidence citation anchoring.

### Question B: Which strategies are merely declarative labels?
1. `presentation_component_reflow`: Modifies `slide.layout = "two_column"` or `beat.visual_priority = "CONCEPT_CARD"`. Does not alter grid column allocations, component stacking, or container geometry.
2. `worksheet_layout_alternation`: Cycles `expected_reasoning_type` through 5 strings. Neither the worksheet bridge nor the Jinja template reacts to this property.
3. `worksheet_workspace_expansion`: Mutates `scaffolding_level = "STRUCTURED_GUIDANCE"`. Does not allocate vertical response space or inject min-height containers.
4. `worksheet_typography_scale`: Mutates `scaffolding_level = "DETAILED_PROMPTS"`. Does not change CSS token font sizes.

### Question C: Which findings have no executable actuation path?
1. `ELEMENT_COLLISION` on Presentations: Overlapping bounding boxes in formula breakdown grids (Page 2 & 5 of `hand_fire_full`, Page 5 of `oobleck_experiment`) have no executable operator to reallocate grid columns, convert horizontal items to vertical cards, or split derivations.
2. `REPETITION_STREAK` on Worksheets: Monotonous sequences of 15 identical question pages have no actuator to cluster questions, insert observation tables, or inject interactive checkpoints.
3. `TEXT_TOO_SMALL` caused by layout/density pressure: No typography constraint solver exists to remove decorative headers, reallocate card space, or reflow elements so that font sizes can naturally meet readability floors.
4. `SCIENTIFIC_CITATION_INVISIBLE` caused by print margin clipping or layer occlusion: No layout-level citation reflow actuator exists.

### Question D: Which root causes require blueprint recomposition?
1. `CONTENT_DENSITY` when slides/pages have exceeded capacity floors: Requires `PresentationSlideSplitActuator` or `HandoutDensityReflowActuator`.
2. `INQUIRY_STRUCTURE` & `REPETITION_STREAK` on Worksheets: Requires `WorksheetInquiryRecompositionActuator` to rebuild the activity progression graph.
3. `NARRATIVE_ORDER`: Requires reordering beats or sections across the blueprint.
4. `CITATION_LINEAGE`: Requires reconstructing bibliography units and citation anchor keys in blueprint metadata.

### Question E: Which defects require renderer-level transformations?
1. `ELEMENT_COLLISION` caused by CSS grid template column constraints (`grid-template-columns: 1fr 1fr;` without wrapping).
2. `TEXT_TOO_SMALL` caused by fixed SVG viewBox aspect ratio scaling down child `<text>` elements.
3. `MARGIN_VIOLATION` / `VIEWPORT_BREACH` caused by fixed card padding.
4. `CONTRAST_DEFICIT` caused by token color assignments on dark background elements.

### Question F: Which defects cannot be safely automated?
1. Missing empirical data or evidence not present in source manifest.
2. Unresolved research methodology omissions.
3. Factual questions whose answer would violate `withhold_explanation=True`.
4. Irreconcilable contradictory claims in source text.
These must deterministically route to `MANUAL_REVIEW_REQUIRED` with actionable guidance.

### Question G: Where is the narrowest safe mutation boundary for each artifact?
- **Presentation**:
  - Narrowest: `LEVEL_2_COMPONENT_GEOMETRY` (re-stacking formula items or grid cards within the slide).
  - Broadest: `LEVEL_4_BLUEPRINT_REGROUPING` (splitting slide into progressive beats).
- **Worksheet**:
  - Narrowest: `LEVEL_3_PAGE_COMPOSITION` (clustering questions into structured observation cards).
  - Broadest: `LEVEL_4_BLUEPRINT_REGROUPING` (re-synthesizing inquiry progression).
- **Handout**:
  - Narrowest: `LEVEL_1_LOCAL_TOKEN` (adjusting heading margins or padding).
  - Broadest: `LEVEL_3_PAGE_COMPOSITION` (re-balancing section pagination).
- **Scientific Document**:
  - Narrowest: `LEVEL_1_LOCAL_TOKEN` (citation anchor typography).
  - Broadest: `LEVEL_4_BLUEPRINT_REGROUPING` (methodology and evidence section re-ordering).

### Question H: Which existing transformation engines can be reused?
1. `app/refinement/patches.py`: Reusable patch structures (`DensitySplitPatch`, `PedagogicalSequencePatch`, `CapabilityReplacementPatch`).
2. `app/intelligence/transformation/transformers.py`: Blueprint generator transformers for all 4 artifact formats.
3. `app/integration/artifact_bridge/`: Blueprint-to-RenderArtifact translation bridges.
4. `app/presentation/visual_director.py`: Layout selection rules and visual grammar registry.
5. `app/design_system/resolver.py`: Deterministic token resolvers.

---

## 4. Architectural Transformation Plan for Phase 4

```
┌────────────────────────────────────────────────────────┐
│ Phase 1: Canonical Repair Actuation Contracts          │
│   - RepairActuationRequest, RepairActuationResult      │
│   - RepairActuator Protocol                            │
└────────────────────────────────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│ Phase 2: Actuator Registry & 5th Firewall Filter       │
│   - RepairActuatorRegistry                             │
│   - Firewall: ACTUATOR_AVAILABLE_AND_CAPABLE           │
└────────────────────────────────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│ Phase 3: Multi-Layer Mutation Model (Layers 0-4)       │
│   - Token -> Component -> Composition -> Blueprint     │
└────────────────────────────────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│ Phase 4-8: Concrete Structural Actuators               │
│   - PresentationComponentReflowActuator                │
│   - PresentationFormulaRecompositionActuator           │
│   - PresentationCompositionActuator                    │
│   - PresentationSlideSplitActuator                     │
│   - PresentationStructuralDiversityGuard               │
│   - TypographyConstraintSolver                         │
│   - WorksheetInquiryRecompositionActuator              │
│   - WorksheetPedagogicalDiversityAnalyzer              │
└────────────────────────────────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│ Phase 9-15: Blueprint Engine, Learning, Diff System    │
│   - BlueprintRecompositionEngine                       │
│   - RepairOperatorPerformanceRegistry                  │
│   - Pre-actuation causal check & zero-effect extension │
│   - ArtifactTransformationDiff (json + md)             │
└────────────────────────────────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│ Phase 16-20: Adversarial Suite, Replay & Regression    │
│   - 30+ new adversarial tests (Scenarios A through AD) │
│   - Full 8-run benchmark replay across Oobleck & Fire  │
│   - 100% green test suite                              │
└────────────────────────────────────────────────────────┘
```
