# UNIVERSAL DOCUMENT INTELLIGENCE SYSTEM V5
# PHASE 4 — REPAIR ACTUATION & STRUCTURAL RECOMPOSITION ENGINE
## System Architecture & Technical Specification

---

## 1. Executive Overview & Mission

Phase 4 bridges the critical architectural boundary between **diagnostic repair planning** (Phases 3B – 3D.1) and **physical artifact transformation**. In previous phases, the system identified root causes and scheduled repair plans, but relied on mock or template-level mutations. 

The **Phase 4 Repair Actuation & Structural Recomposition Engine** implements true physical artifact mutation across five distinct structural abstraction layers. It provides deterministic, causal-aware, atomic repairs that eliminate physical rendering defects (`ELEMENT_COLLISION`, `TEXT_TOO_SMALL`, `OVERFLOW_VERTICAL`) and structural pedagogical defects (`REPETITION_STREAK`, `PEDAGOGICAL_ARC_BROKEN`), while guaranteeing zero semantic loss, zero external AI calls, strict explanation withholding, and non-bypassable quality gating by `UnifiedQualityAuthority`.

---

## 2. The 5 Mutation Layers

To prevent chaotic mutations and enforce sound engineering boundaries, repair operations are strictly segregated into five hierarchical mutation layers:

```
┌────────────────────────────────────────────────────────┐
│ Layer 5: Semantic Organization                        │
│ (Inquiry Arc Reordering, Section Restructuring)        │
├────────────────────────────────────────────────────────┤
│ Layer 4: Blueprint Recomposition                       │
│ (Component Splitting, Section Redistribution)          │
├────────────────────────────────────────────────────────┤
│ Layer 3: Page Composition                              │
│ (Multi-Column Reflow, Card Layout Reorganization)      │
├────────────────────────────────────────────────────────┤
│ Layer 2: Component Layout & Box Sizing                 │
│ (Formula Box Clamping, Padding/Margin Normalization)   │
├────────────────────────────────────────────────────────┤
│ Layer 1: Token & Typography                            │
│ (Font Size Constraint Solver, Line Height Calibration) │
└────────────────────────────────────────────────────────┘
```

### Layer 1: Token & Typography (`MutationLayer.TOKEN`)
- **Actuators**: `TypographyConstraintSolver`, `TokenReflowActuator`.
- **Scope**: Modifies font sizes, line heights, letter spacing, and CSS token bindings.
- **Invariants**: Enforces absolute floor constraints:
  - Presentations: Minimum 12.0pt body, 16.0pt headings.
  - Worksheets: Minimum 10.5pt body, 13.0pt headings.
  - Handouts: Minimum 10.0pt body, 12.0pt headings.
  - Scientific Documents: Minimum 9.5pt body, 11.0pt headings.
  - Font scaling factor step-down limit: delta <= 2.0pt per step; hard floor never breached.

### Layer 2: Component Layout (`MutationLayer.COMPONENT`)
- **Actuators**: `FormulaWidthActuator`, `ComponentReflowActuator`.
- **Scope**: Internal geometry and layout of atomic components.
- **Invariants**:
  - Formulas exceeding bounding box width are converted to block display with auto-overflow and scaled font constraints.
  - Padding and margins are compressed symmetrically, preserving visual hierarchy.

### Layer 3: Page Composition (`MutationLayer.PAGE_COMPOSITION`)
- **Actuators**: `PresentationCompositionActuator`, `HandoutBalanceActuator`.
- **Scope**: Multi-component spatial distribution within a single page or slide.
- **Invariants**:
  - Converts single-column card overflows into balanced 2-column or 3-column CSS grids (`grid-template-columns: repeat(N, 1fr)`).
  - Enforces collision-free bounding boxes with guaranteed inter-card gutters (>= 16px).

### Layer 4: Blueprint Recomposition (`MutationLayer.BLUEPRINT_RECOMPOSITION`)
- **Actuators**: `SlideSplitActuator`, `BlueprintRecompositionEngine`.
- **Scope**: Structural page splits, component migrations across pages, and blueprint node duplication/distribution.
- **Invariants**:
  - Overcrowded slides (> 4 cards or total card height > 540pt) are deterministically split into continuation slides (`Page N` -> `Page N.1`, `Page N.2`).
  - Total concept preservation: No blueprint element is dropped; elements are cleanly partitioned across child pages.

### Layer 5: Semantic Organization (`MutationLayer.SEMANTIC_ORGANIZATION`)
- **Actuators**: `WorksheetInquiryRecompositionActuator`, `ScientificCitationActuator`, `ScientificEvidenceActuator`.
- **Scope**: Pedagogical ordering, epistemic inquiry arcs, and evidence/citation linkage.
- **Invariants**:
  - Restructures repetitive worksheets into the canonical 7-stage inquiry arc:
    1. `ENGAGE` (Phenomenon observation)
    2. `EXPLORE` (Qualitative manipulation)
    3. `EXPLAIN` (Conceptual modeling)
    4. `ELABORATE` (Quantitative calculation)
    5. `EVALUATE` (Critical synthesis)
    6. `REFLECT` (Metacognitive extension)
    7. `CHALLENGE` (Transfer scenario)
  - Answer withholding invariant: Explanations and solution keys are strictly withheld (`withhold_explanation=True`) on student worksheets.

---

## 3. Pre-Actuation Causal-Chain Verification

To prevent applying repairs that conflict with the root cause or violate causal ordering, every repair actuation is subject to pre-actuation validation via `PreActuationCausalValidator`:

1. **Causal Depth Consistency**:
   - Repair operators specify their target depth ($D_{target}$).
   - If the root cause identified in the causal graph has depth $D_{root}$, the actuator must operate at $D >= D_{root}$. Applying a shallow token repair to a deep architectural defect (e.g. blueprint overflow) is rejected before execution (`SKIPPED_PRECONDITION`).
2. **Precondition Validation**:
   - Each actuator executes an idempotent precondition check (`can_apply()`). If the artifact does not manifest the specific structural pattern targeted by the operator, execution is bypassed without mutation.

---

## 4. Typography Constraint Solver

Located in `app/quality/repair/actuation/typography_solver.py`:
- Solves linear optimization constraints for text layout:
  min |s - s_target| s.t. s >= s_floor, TotalHeight(s) <= H_page
- Step-down scaling reduces font sizes by standard typographic increments (0.5pt or 1.0pt) while strictly respecting the artifact-specific floor.
- Completely eliminates `TEXT_TOO_SMALL` defects while simultaneously resolving vertical overflows without unreadable microscopic fonts.

---

## 5. Worksheet Inquiry Recomposition & Diversity Engine

Located in `app/quality/repair/actuation/inquiry_recomposition.py` and `diversity_analyzer.py`:
- **Diversity Analyzer**: Computes Shannon entropy ($H$) over question types and Bloom cognitive levels:
  $H = - sum(p_i * log2(p_i))$
- Detects `REPETITION_STREAK` (consecutive identical question types >= 3) and low entropy ($H < 1.5$).
- **Inquiry Recomposition Actuator**:
  - Re-sequences exercise items into the 7-stage inquiry arc.
  - Injects cognitive framing and varied prompt stems (observational, analytical, computational, evaluative).
  - Preserves 100% of underlying knowledge concepts with zero semantic hallucination.
  - Maintains strict `explanation_withheld` status for student-facing exports.

---

## 6. Performance Learning Registry

Located in `app/quality/repair/actuation/learning.py`:
- `RepairOperatorPerformanceRegistry` records historical execution outcomes for every repair operator across artifact types:
  - Total attempts, successes, rollbacks, and execution failures.
  - Score delta achieved: delta S = S_post - S_pre.
  - Historical win-rate: W = successes / attempts.
- Powers priority sorting in the repair planner, ensuring high-yield, low-risk operators are scheduled first.
- Thread-safe, persistent, and updated atomically upon transaction commitment.

---

## 7. Atomic Rollback & Transaction Model

Located in `app/quality/repair/transaction.py`:
- Every repair execution occurs within an isolated transactional boundary (`RepairTransaction`):
  1. Deep snapshot creation of the artifact blueprint and renderer data structure.
  2. Sequential execution of planned actuators with pre-actuation causal checking.
  3. Re-rendering and evaluation by `UnifiedQualityAuthority`.
  4. Decision arbitration:
     - If quality score increases (delta S > 0) and no new blockers appear: **COMMIT**.
     - If quality score regresses (delta S < 0) or new blockers appear: **ROLLBACK** (restores snapshot, records failure in performance registry).
- Guarantees that the repository never leaves artifacts in a broken, degraded, or half-mutated state.

---

## 8. Integration with UnifiedQualityAuthority

The repair actuation subsystem operates under the strict sovereignty of `UnifiedQualityAuthority`:
- Actuators **never** decide if a repair is successful.
- Only `UnifiedQualityAuthority.evaluate_rendered()` or `UnifiedQualityAuthority.evaluate_comprehensive()` determines whether an artifact qualifies for Level-0 export.
- Thresholds are never lowered dynamically.
- Zero-AI guarantee is enforced at every boundary.
