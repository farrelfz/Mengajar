# 01 — Existing Capability Family Forensics & Duplication Audit

## Context & Objectives
Prior to Batch 9, capabilities were created primarily as monolithic pairs: a Pydantic `CapabilitySpec` and an accompanying dedicated `CapabilityRenderer` (generating either raw HTML or SVG markup). While modular, scaling to 100+ capabilities under this paradigm leads to file explosion, code duplication across SVG path calculations, card layouts, matrix tables, and flowchart arrow positioning.

This forensic audit analyzes all 21 registered capabilities to discover latent structural families and quantify duplication risks.

---

## 1. Comprehensive Capability Forensics Matrix

| Capability ID | Current Domain | Semantic Intent | Information Structure | Visual Grammar | Potential Family | Structural Reusability & Overlap | Current Renderer Duplication Risk |
|---|---|---|---|---|---|---|---|
| `diagram.process_flow` | `general` | `SEQUENCE` | `LINEAR_SEQUENCE` | `PROCESS_FLOW` | **PROCESS** | High overlap with experiment workflow and scientific reasoning pathway | **HIGH**: Duplicates linear SVG node/arrow rendering logic. |
| `research.scientific.reasoning_pathway` | `research_education` | `SEQUENCE` | `LINEAR_SEQUENCE` | `REASONING_FLOW` | **PROCESS** / **REASONING** | High overlap with process flow; 4-stage pipeline | **HIGH**: Duplicates sequential stage cards and connecting arrows. |
| `research.experiment_workflow` | `research_education` | `SEQUENCE` | `LINEAR_SEQUENCE` | `PROCESS_FLOW` | **PROCESS** | Identical structure to process flow with protocol badges | **HIGH**: Duplicates SVG chevron and step progression layout. |
| `universal.comparison_matrix` | `general` | `COMPARE` | `MATRIX` | `COMPARISON` | **COMPARISON** | Multi-item comparison card with badges | **HIGH**: Duplicates HTML table / card comparison layout. |
| `pedagogy.misconception_correction` | `general` | `COMPARE` | `MATRIX` | `COMPARISON` | **COMPARISON** | Binary side-by-side comparison ("Intuition vs Reality") | **MEDIUM**: Specialized 2-column contrast card. |
| `research.problem.gap_matrix` | `research_education` | `COMPARE` | `MATRIX` | `COMPARISON` | **COMPARISON** | 3-column matrix (Literature, Gap, Contribution) | **HIGH**: Re-implements 3-column comparative HTML cards. |
| `universal.concept_hierarchy` | `general` | `CLASSIFY` | `HIERARCHY` | `CONCEPT_MAP` | **HIERARCHY** | Tree-structure parent/child nodes | **HIGH**: Duplicates tree node rendering and SVG branch connectors. |
| `research.problem.funnel` | `research_education` | `NARROW_SCOPE` | `HIERARCHY` | `FUNNEL` | **HIERARCHY** / **PROCESS** | Progressive narrowing layers | **MEDIUM**: Trapezoidal SVG funnel rendering. |
| `universal.evidence_chain` | `general` | `ARGUE` | `EVIDENCE_CHAIN` | `REASONING_FLOW` | **REASONING** | Premise → Evidence → Warrant → Conclusion | **HIGH**: Re-implements logical step cards and arrows. |
| `research.scientific.hypothesis_test` | `research_education` | `INVESTIGATE` | `EVIDENCE_CHAIN` | `MATRIX` | **REASONING** / **EVIDENCE** | Hypothesis vs observation vs falsification | **MEDIUM**: 3-stage validation block. |
| `pedagogy.worked_example` | `general` | `DERIVE` | `TRANSFORMATION` | `EQUATION_CHAIN` | **STEPWISE_REASONING** / **QUANTITATIVE** | Step-by-step mathematical problem solution | **HIGH**: Duplicates formula block formatting and step numbering. |
| `mathematics.equation_derivation` | `mathematics` | `DERIVE` | `TRANSFORMATION` | `EQUATION_CHAIN` | **QUANTITATIVE** | Mathematical algebraic transformations | **HIGH**: Duplicates derivation step-by-step layout. |
| `mathematics.variable_mapping` | `mathematics` | `EXPLAIN` | `MAPPING` | `TABLE` | **QUANTITATIVE** / **COLLECTION** | Symbol, Name, Dimension, Unit reference table | **HIGH**: Duplicates reference table HTML markup. |
| `research.methodology.design_matrix` | `research_education` | `ANALYZE` | `MATRIX` | `MATRIX` | **QUANTITATIVE** / **COLLECTION** | Methodological dimension table | **HIGH**: Duplicates tabular matrix rendering. |
| `research.variable_relationship_map` | `research_education` | `RELATE` | `MAPPING` | `ANNOTATED_DIAGRAM` | **RELATIONSHIP** | Directed variable relationship diagram | **HIGH**: Complex node-and-directed-arrow SVG layout. |
| `pedagogy.question_progression` | `general` | `INVESTIGATE` | `QUESTION_SET` | `CHECKPOINT_CARD` | **PROGRESSION** | Bloom's taxonomy staged questions | **HIGH**: Progressive ladder card structure. |
| `pedagogy.concept_checkpoint` | `general` | `ASSESS` | `QUESTION_SET` | `CHECKPOINT_CARD` | **PROGRESSION** / **COLLECTION** | Diagnostic MCQ and conceptual reflection | **MEDIUM**: Question container with option pills. |
| `presentation.hero_statement` | `general` | `HOOK` | `SINGLE_ENTITY` | `HERO` | **COLLECTION** / **FRAMING** | High-impact quote/title hero panel | **LOW**: Standalone full-bleed banner. |
| `presentation.concept_introduction` | `general` | `INTRODUCE` | `SINGLE_ENTITY` | `CONCEPT_PANEL` | **COLLECTION** / **CONCEPT** | Definition, analogy, properties panel | **LOW**: Standard concept card layout. |
| `physics.mechanics.torque_diagram` | `physics` | `EXPLAIN` | `SPATIAL_SYSTEM` | `ANNOTATED_DIAGRAM` | **SPATIAL_SYSTEMS** | Physical mechanics lever & force vector SVG | **LOW**: Highly domain-specific trigonometric physics engine. |
| `physics.mechanics.free_body_diagram` | `physics` | `ANALYZE` | `SPATIAL_SYSTEM` | `ANNOTATED_DIAGRAM` | **SPATIAL_SYSTEMS** | Orthogonal force vector simulation SVG | **LOW**: Highly domain-specific force summation engine. |

---

## 2. Key Structural Redundancies Identified

1. **Process & Flow Duplication**:
   - `diagram.process_flow`, `research.experiment_workflow`, and `research.scientific.reasoning_pathway` all compute sequential horizontal/vertical SVG node cards with chevron connectors and status pills.
   - *Family Solution*: Unified `PROCESS` family with `LinearProcessTemplate`, `PipelineProcessTemplate`, and `CyclicProcessTemplate`.

2. **Comparison Matrix Duplication**:
   - `universal.comparison_matrix`, `pedagogy.misconception_correction`, and `research.problem.gap_matrix` all render contrasting column cards with accent borders, icons, and distinction tags.
   - *Family Solution*: Unified `COMPARISON` family with `MatrixComparisonTemplate`, `BinaryContrastTemplate`, and `MultiAxisComparisonTemplate`.

3. **Hierarchy & Tree Duplication**:
   - `universal.concept_hierarchy` and `research.problem.funnel` render hierarchical levels and parent-child connectors.
   - *Family Solution*: Unified `HIERARCHY` family with `TreeHierarchyTemplate` and `LayeredPyramidTemplate`.

4. **Stepwise Reasoning & Derivation Duplication**:
   - `pedagogy.worked_example` and `mathematics.equation_derivation` both format annotated mathematical transformations.
   - *Family Solution*: Unified `QUANTITATIVE` / `STEPWISE_REASONING` family with `EquationDerivationTemplate` and `StepwiseReasoningTemplate`.

5. **Reasoning & Evidence Chain Duplication**:
   - `universal.evidence_chain` and `research.scientific.hypothesis_test` format premise-evidence-conclusion inference structures.
   - *Family Solution*: Unified `REASONING` family with `EvidenceChainTemplate` and `ArgumentMapTemplate`.

6. **Progression & Scaffold Duplication**:
   - `pedagogy.question_progression` and `pedagogy.concept_checkpoint` render phased learning ladders.
   - *Family Solution*: Unified `PROGRESSION` family with `QuestionLadderTemplate` and `CheckpointCardTemplate`.

---

## 3. Structural Family Unification Blueprint

By consolidating these 6 recurring structural archetypes into **Generative Family Templates**, the codebase can support 100+ future domain capabilities (e.g. Chemistry reaction pathways, Biology ecological pyramids, Economics supply-demand shifts) with **zero new renderer implementations**.
