# 04 — Capability Reality Audit & Parameterization Matrix

## 1. Capability Maturity Classification

We audited each of the 11 registered capabilities against the 4 maturity levels:
- **LEVEL 0 (Demo):** Hardcoded single demonstration; cannot vary without broken layout or wrong text.
- **LEVEL 1 (Parameterized):** Accepts parameter variations, but visual structure remains rigid.
- **LEVEL 2 (Reusable):** Works across multiple topics/domains with robust data handling.
- **LEVEL 3 (Adaptive / Responsive):** Adapts composition or layout based on available space and aspect ratio.

---

## 2. Comprehensive Capability Matrix

| Capability ID | Display Name | Category | Maturity Level | Input Model & Varying Parameters | Format-Aware? | Risk / Limitation |
|---|---|---|---|---|---|---|
| `physics.torque_diagram` | Torque Diagram | physics | **LEVEL 2** | `pivot_label`, `lever_length_m`, `force_newtons`, `force_angle_deg`, `rotation_direction` | Fixed 650x320 SVG viewBox, responsive in container | Angle > 180° requires validation guard |
| `physics.free_body_diagram` | Free Body Diagram | physics | **LEVEL 2** | `object_name`, `mass_kg`, `forces: list[ForceVector]` | 500x400 SVG viewBox | Extreme number of overlapping forces (>6) |
| `pedagogy.worked_example` | Worked Example Scaffold | pedagogy | **LEVEL 2** | `problem`, `knowns`, `unknowns`, `principles`, `steps: list`, `final_answer` | HTML responsive to step count | Large number of steps (>5) requires page split |
| `pedagogy.misconception_correction` | Misconception Card | pedagogy | **LEVEL 2** | `common_belief`, `why_it_seems_true`, `counterexample`, `correct_explanation` | HTML 2-column flex grid | Needs minimum 600px width for 2 columns |
| `research.scientific.reasoning_pathway` | Scientific Reasoning Pathway | research | **LEVEL 2** | `topic`, `stages: list[PathwayStage]` | SVG 900x260 horizontal flow | Better suited for landscape/presentation than narrow portrait |
| `research.problem.funnel` | Research Problem Funnel | research | **LEVEL 2** | `topic`, `phenomenon`, `problem_identification`, `scope_limitation`, `final_question` | SVG 850x360 inverted trapezoid | Text wrapping inside SVG trapezoids is manually truncated |
| `research.hypothesis.test_matrix` | Hypothesis Matrix | research | **LEVEL 2** | `research_question`, `hypothesis`, `independent_var`, `dependent_var`, `controlled_vars` | HTML grid with badge highlights | Highly resilient |
| `research.gap_matrix` | Research Gap Matrix | research | **LEVEL 2** | `topic`, `existing_consensus`, `unresolved_gap`, `study_contribution` | HTML 3-column comparative card | Needs horizontal room |
| `research.methodology.design_matrix` | Methodology Matrix | research | **LEVEL 2** | `study_title`, `population_sample`, `treatment`, `data_collection`, `data_analysis` | HTML table structure | High resilience |
| `mathematics.equation_derivation` | Equation Derivation | mathematics | **LEVEL 1** | `title`, `target_formula`, `steps: list` | HTML step cards with monospace math | Latex math formatting not yet fully rendered via MathJax |
| `mathematics.variable_mapping` | Variable Mapping Table | mathematics | **LEVEL 2** | `formula_name`, `formula_latex`, `variables: list[VariableSymbol]` | HTML table | Clean and stable |
| `presentation.hero_statement` | Hero Statement | presentation | **LEVEL 1** | `headline`, `subheadline`, `tag`, `quote` | Full slide HTML flex container | Fixed typography scaling |
| `presentation.concept_introduction` | Concept Intro Card | presentation | **LEVEL 2** | `concept_name`, `formal_definition`, `intuitive_analogy`, `key_characteristics` | HTML card layout | Clean and stable |

---

## 3. Findings on Capability Architecture
- **Parameterization Truth:** All capabilities use strictly typed Pydantic spec models (`TorqueDiagramSpec`, `WorkedExampleSpec`, etc.) with real parameter calculations (e.g. vector trig `math.sin(angle_rad)`, torque calculations, HTML loops).
- **Format Awareness Gap:** Currently, capability renderers output either fixed SVG dimensions (e.g. `900x260` or `650x320`) or HTML blocks that rely on outer CSS container width. They do NOT yet inspect `ArtifactFormat` or available region height to adjust their internal layout (e.g., horizontal funnel vs vertical funnel).
- **Conclusion:** Existing capabilities are solidly at **LEVEL 1 to LEVEL 2**. None are hardcoded fake demos (LEVEL 0).
