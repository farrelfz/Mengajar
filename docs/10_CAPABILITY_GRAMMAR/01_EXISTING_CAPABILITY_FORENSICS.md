# 01 — Forensic Inventory & Capability Analysis

## 1. Executive Summary

Prior to Batch 8, the KIR AI Engine possessed 14 distinct capabilities registered across separate domain folders (`physics/`, `pedagogy/`, `research_education/`, `presentation/`, `mathematics/`, `diagrams/`).

This forensic audit analyzes their true underlying **semantic purpose**, **information shape**, **pedagogical role**, **visual grammar**, and **output behavior**, revealing that domain specialization is merely a topical skin over a set of universal cognitive and visual patterns.

---

## 2. Forensic Analysis of Existing Capabilities

### 1. `physics.mechanics.torque_diagram`
- **Semantic Purpose:** Explain a spatial force-vector relationship and calculate equilibrium magnitude.
- **Information Shape:** Spatial system with trigonometric vector geometry ($\vec{F}, \theta, \vec{r}, \vec{\tau}$).
- **Pedagogical Role:** Explanation & visual intuition anchor.
- **Visual Grammar:** Annotated Spatial Vector Diagram (SVG coordinate canvas).
- **Output Behavior:** Static SVG with computed numerical torque badge.

### 2. `physics.mechanics.free_body_diagram`
- **Semantic Purpose:** Visualize concurrent forces acting upon a central mass.
- **Information Shape:** Coordinate vector network (Cartesian 2D).
- **Pedagogical Role:** Analysis & problem modeling.
- **Visual Grammar:** Central Body Vector Map (SVG).
- **Output Behavior:** Multi-vector radial diagram.

### 3. `pedagogy.worked_example`
- **Semantic Purpose:** Demonstrate step-by-step problem-solving reasoning from knowns to interpretation.
- **Information Shape:** Stepwise transformation (Knowns $\rightarrow$ Principles $\rightarrow$ Steps $\rightarrow$ Result).
- **Pedagogical Role:** Cognitive scaffolding & guided demonstration.
- **Visual Grammar:** Step Sequence Card (HTML).
- **Output Behavior:** Expandable narrative block with code/math steps.

### 4. `pedagogy.misconception_correction`
- **Semantic Purpose:** Contrast intuitive naive belief with rigorous scientific model.
- **Information Shape:** 2-way comparative contrast (Belief vs Reality).
- **Pedagogical Role:** Conceptual change & misconception refutation.
- **Visual Grammar:** Side-by-Side Contrast Card (HTML).
- **Output Behavior:** Dual card container with badge highlights.

### 5. `presentation.hero_statement`
- **Semantic Purpose:** Hook learner attention with opening big idea or dramatic metric.
- **Information Shape:** Key statement with highlighted focal element.
- **Pedagogical Role:** Hook & framing.
- **Visual Grammar:** Hero Card / Title Block (HTML).
- **Output Behavior:** Expansive typography container.

### 6. `presentation.concept_introduction`
- **Semantic Purpose:** Introduce new terminology, formal definition, and intuitive analogy.
- **Information Shape:** Concept structure (Name + Definition + Analogy + Properties).
- **Pedagogical Role:** Foundation & concept introduction.
- **Visual Grammar:** Structured Concept Panel (HTML).
- **Output Behavior:** Multi-section card.

### 7. `diagrams.process_flow`
- **Semantic Purpose:** Illustrate linear or branching temporal stages.
- **Information Shape:** Linear sequence / Flow network.
- **Pedagogical Role:** Process explanation.
- **Visual Grammar:** Horizontal/Vertical Process Pipeline.
- **Output Behavior:** SVG flow diagram.

### 8. `research.scientific.reasoning_pathway`
- **Semantic Purpose:** Map the scientific inquiry cycle from observation to conclusion.
- **Information Shape:** Cyclic / linear evidence pipeline.
- **Pedagogical Role:** Scientific thinking scaffold.
- **Visual Grammar:** Horizontal Pipeline Flow (SVG).
- **Output Behavior:** Multi-stage chevron/node sequence.

### 9. `research.problem.funnel`
- **Semantic Purpose:** Narrow broad real-world phenomenon into a constrained research question.
- **Information Shape:** Hierarchical transformation / scope narrowing.
- **Pedagogical Role:** Problem formulation scaffold.
- **Visual Grammar:** Inverted Funnel Diagram (SVG).
- **Output Behavior:** Trapezoidal hierarchy diagram.

### 10. `research.problem.gap_matrix`
- **Semantic Purpose:** Contrast established literature consensus with the unresolved gap and novel study contribution.
- **Information Shape:** 3-way comparative matrix.
- **Pedagogical Role:** Literature positioning & novelty justification.
- **Visual Grammar:** 3-Column Comparative Card (HTML).
- **Output Behavior:** Side-by-side comparative cards.

### 11. `research.scientific.hypothesis_test`
- **Semantic Purpose:** Operationalize independent, dependent, and controlled variables into a testable hypothesis.
- **Information Shape:** Variable mapping + prediction verification.
- **Pedagogical Role:** Experimental design scaffold.
- **Visual Grammar:** Hypothesis Protocol Matrix (HTML).
- **Output Behavior:** Variable grid with prediction banner.

### 12. `research.methodology.design_matrix`
- **Semantic Purpose:** Specify research design, sampling, instruments, procedure, and analysis.
- **Information Shape:** Multi-dimensional matrix & operational table.
- **Pedagogical Role:** Methodological specification.
- **Visual Grammar:** Framework Table + Grid (HTML).
- **Output Behavior:** Structured tabular cards.

### 13. `mathematics.equation_derivation`
- **Semantic Purpose:** Walk through formal algebraic or calculus derivation step by step.
- **Information Shape:** Stepwise equation transformation.
- **Pedagogical Role:** Formal mathematical reasoning.
- **Visual Grammar:** Equation Chain (HTML).
- **Output Behavior:** Vertical mathematical proof card.

### 14. `mathematics.variable_mapping`
- **Semantic Purpose:** Map formula symbols to physical quantities, units, and definitions.
- **Information Shape:** Key-value symbolic dictionary.
- **Pedagogical Role:** Reference & parameter definition.
- **Visual Grammar:** Variable Table (HTML).
- **Output Behavior:** Two-column reference matrix.

---

## 3. Key Forensic Discovery: The Hidden Grammatical Overlap

| Capability | Domain Folder | Underlying Visual Grammar | Underlying Information Shape |
|---|---|---|---|
| `diagrams.process_flow` | Universal | **PROCESS_FLOW** | Linear Sequence |
| `research.scientific.reasoning_pathway` | Research | **PROCESS_FLOW** | Linear Sequence |
| `pedagogy.misconception_correction` | Pedagogy | **COMPARISON** | 2-Way Contrast |
| `research.problem.gap_matrix` | Research | **COMPARISON** | 3-Way Contrast |
| `pedagogy.worked_example` | Pedagogy | **STEP_SEQUENCE** | Stepwise Transformation |
| `mathematics.equation_derivation` | Mathematics | **STEP_SEQUENCE** | Stepwise Transformation |
| `physics.mechanics.torque_diagram` | Physics | **ANNOTATED_SPATIAL** | Spatial Coordinate System |
| `physics.mechanics.free_body_diagram` | Physics | **ANNOTATED_SPATIAL** | Spatial Coordinate System |

### Architectural Conclusion
Domain (`physics`, `research`, `mathematics`) is **NOT** the fundamental taxonomic layer. It is a specialization layer on top of universal **Capability Families** (e.g. `PROCESS_VISUALIZATION`, `COMPARATIVE_REASONING`, `STEPWISE_REASONING`, `SPATIAL_SYSTEMS`, `EVIDENCE_ANALYSIS`).
