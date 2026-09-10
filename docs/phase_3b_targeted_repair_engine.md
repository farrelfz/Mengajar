# PHASE 3B — ROOT-CAUSE-AWARE TARGETED REPAIR & ITERATIVE QUALITY CONVERGENCE ENGINE
## Universal Document Intelligence System V5
### Architectural Implementation Report

---

## 1. Executive Summary & Core Mission

Phase 3B transforms the Universal Document Intelligence System from a passive detection and blocking system:
$$\text{DETECT} \longrightarrow \text{REPORT} \longrightarrow \text{BLOCK}$$
into an active, explainable, self-correcting document production engine:
$$\text{DETECT} \longrightarrow \text{CORRELATE} \longrightarrow \text{ROOT CAUSE} \longrightarrow \text{PLAN MINIMAL REPAIR} \longrightarrow \text{TARGETED REPAIR} \longrightarrow \text{RE-EVALUATE} \longrightarrow \text{VERIFY NO REGRESSION} \longrightarrow \text{CONVERGE OR ESCALATE}$$

The repair engine operates across **all four artifact types**:
1. **PRESENTATION** (16:9 Slide Decks)
2. **HANDOUT** (Continuous A4 Reading Materials)
3. **WORKSHEET** (Inquiry-driven Student Worksheets / LKS)
4. **SCIENTIFIC_DOCUMENT** (Formal Indonesian Scientific Research Papers / KTI)

### Core Architectural Invariants:
1. **Single Level-0 Authority**: `UnifiedQualityAuthority` remains the exclusive arbiter of document export readiness. The repair engine never bypasses or weakens quality gates.
2. **Deterministic & 100% Offline**: Zero external LLM / AI dependencies. All repairs are deterministic, bounded, explainable, and reproducible.
3. **Cause-Driven, Not Symptom-Chasing**: Repairs address underlying architectural causes rather than masking physical symptoms (e.g. splitting overloaded slides instead of shrinking fonts below legibility thresholds).
4. **Zero Evidence Fabrication**: Factual claims may only be mapped to verified ground-truth knowledge units in the source manifest, softened in certainty, or isolated as research limitations. Factual synthesis is strictly prohibited.
5. **Reversibility & Anti-Regression**: Every mutation is snapshot-guarded. If a repair introduces a new hard blocker, causes score degradation, or breaks traceability, the system rolls back immediately.

---

## 2. Canonical Repair Architecture & Pipeline Flow

```
                  +-------------------------------------------------------------+
                  |         UnifiedQualityAuthority (Phase 3A.1 Consolidation)    |
                  |     Issues ExportDecision & Canonical QualityFinding list   |
                  +------------------------------+------------------------------+
                                                 │
                                                 ▼
                  +-------------------------------------------------------------+
                  |              Deterministic Root Cause Analyzer              |
                  |   Infers RootCauseType (CONTENT_DENSITY, INQUIRY_ARC, etc.)  |
                  +------------------------------+------------------------------+
                                                 │
                                                 ▼
                  +-------------------------------------------------------------+
                  |                  Repair Strategy Registry                   |
                  |     Selects strategy matching (Format, Code, Cause)         |
                  |     Prioritizes minimal mutation cost (Class A -> Class E)  |
                  +------------------------------+------------------------------+
                                                 │
                                                 ▼
                  +-------------------------------------------------------------+
                  |                 Snapshot Manager (Rollback)                 |
                  |         Takes minimal SHA-256 deep copy snapshot            |
                  +------------------------------+------------------------------+
                                                 │
                                                 ▼
                  +-------------------------------------------------------------+
                  |              Targeted Repair Strategy Execution             |
                  |     Applies planned mutation to artifact blueprint          |
                  +------------------------------+------------------------------+
                                                 │
                                                 ▼
                  +-------------------------------------------------------------+
                  |                Authoritative Re-Evaluation                  |
                  |     Re-evaluates mutated document with UnifiedAuthority     |
                  +------------------------------+------------------------------+
                                                 │
                                                 ▼
                  +-------------------------------------------------------------+
                  |                       Regression Guard                      |
                  |   Checks: No new hard blockers, score delta >= -0.05,       |
                  |   traceability preserved, pedagogical invariants intact     |
                  +--------------+-------------------------------+--------------+
                                 │ Passed                        │ Failed
                                 ▼                               ▼
                  +-----------------------------+ +-----------------------------+
                  |    Convergence Controller   | |           Rollback          |
                  |  State hashing, oscillation | |  Restores pre-repair state, |
                  |  check, iteration budget (3)| |  escalates or tries alt plan|
                  +--------------+--------------+ +-----------------------------+
                                 │
                                 ▼
                  +-------------------------------------------------------------+
                  |                Repair Provenance Graph                      |
                  |   Emits repair_report.json & audit trace markdown           |
                  +-------------------------------------------------------------+
```

---

## 3. Repair Mutation Taxonomy

Repairs are strictly segregated into six orthogonal mutation classes with explicit invariants:

| Mutation Class | Scope & Operations | Allowed Mutations | Strictly Forbidden |
| :--- | :--- | :--- | :--- |
| **CLASS A: Non-Semantic Geometry** | Physical container layout & margins | Padding adjustment, margin normalization, column width tuning, element spacing, workspace enlargement. | Font shrinking below 12pt body / 14pt title, altering semantic text, deleting claims. |
| **CLASS B: Compositional Structure** | Content grouping & unit allocation | Splitting overloaded slides/pages, consolidating orphan trailing pages, rebalancing multi-column cards. | Discarding unique knowledge units, breaking source traceability. |
| **CLASS C: Semantic Layout Remapping** | Visual grammar matrix mapping | Remapping layout families (e.g. concept_card -> two_column, process -> sequence) to match narrative function. | Changing underlying knowledge units or pedagogical intent. |
| **CLASS D: Pedagogical Structure** | Educational narrative & inquiry flow | Reordering activities into canonical inquiry progression, enforcing `withhold_explanation=True`, sanitizing answers. | Exposing explanatory conclusions before prediction/observation. |
| **CLASS E: Semantic Integrity** | Verifiable claim-evidence linking | Re-linking claims to verified source evidence, softening modal certainty (assertion -> hypothesis), isolating limitations. | **FABRICATING EVIDENCE**, inventing fake citations, hallucinating facts. |
| **CLASS F: Non-Repairable Escalation** | Source contradictions & missing data | Safe termination and escalation to `MANUAL_REVIEW_REQUIRED`. | Destructive heuristics, deleting contradictory thesis statements. |

---

## 4. Root Cause Taxonomy & Deterministic Inference

The `DeterministicRootCauseAnalyzer` evaluates co-occurring finding clusters and metrics to infer the true origin of failure:

1. **`CONTENT_DENSITY`**: Inferred when `TEXT_OVERFLOW` or `TEXT_CLIPPING` occurs with high container occupancy (> 0.85), card count $\ge 5$, or when accompanied by `FONT_TOO_SMALL`. Resolves via **Class B split**, not font shrinking!
2. **`PADDING_SPACING` / `GRID_GEOMETRY`**: Inferred when overflow occurs under normal occupancy or when elements collide / breach safe margins. Resolves via **Class A geometry relaxation**.
3. **`SEMANTIC_LAYOUT_MAPPING`**: Inferred for `LAYOUT_MONOTONY` ($\ge 5$ identical layouts) or `LAYOUT_TAXONOMY_MISMATCH`. Resolves via **Class C visual grammar remapping**.
4. **`INQUIRY_STRUCTURE`**: Inferred for `INQUIRY_ARC_BROKEN` or `ANTI_SPOILING_BREACH`. Resolves via **Class D inquiry progression restoration**.
5. **`EVIDENCE_MAPPING`**: Inferred for `UNSUPPORTED_SCIENTIFIC_CLAIM` or `MISATTRIBUTED_EVIDENCE` when verifiable source units exist. Resolves via **Class E evidence linkage**.
6. **`SOURCE_INSUFFICIENCY`**: Inferred for `SOURCE_CONTRADICTION` or missing mandatory source knowledge. Non-repairable; safely routes to **Class F escalation**.
7. **`PAGE_BREAK`**: Inferred for `ACCIDENTAL_PAGE` with orphan content. Resolves via **Class B pagination consolidation**.

---

## 5. Format-Specific Strategy Registry

The `RepairStrategyRegistry` indexes 13 canonical format-specific strategies:

### 1. Presentation Strategies (`app/quality/repair/strategies/presentation.py`)
- **`PresentationDensitySplitStrategy`** (Class B, Priority 1, Cost 0.5):
  Splits an overloaded slide into two sequential slides ("Bagian 1" and "Bagian 2"), partitioning key blocks equally, preserving source references, and avoiding legibility-destroying font reductions.
- **`PresentationLayoutRemapStrategy`** (Class C, Priority 1, Cost 0.3):
  Remaps monotonous layouts (`concept_card` -> `two_column` -> `three_column_comparison`) based on canonical narrative functions.
- **`PresentationPaddingAdjustmentStrategy`** (Class A, Priority 1, Cost 0.1):
  Compacts padding for boundary margin breaches under normal content volume.

### 2. Handout Strategies (`app/quality/repair/strategies/handout.py`)
- **`HandoutPaginationStrategy`** (Class B, Priority 1, Cost 0.2):
  Consolidates orphan trailing sections (< 10% content) into predecessor sections, eliminating accidental extra pages.
- **`HandoutHierarchyRepairStrategy`** (Class D, Priority 1, Cost 0.15):
  Restores monotonic heading hierarchy depth (e.g. fixing H1 -> H3 skips to H1 -> H2).
- **`HandoutDensityBalanceStrategy`** (Class B, Priority 1, Cost 0.35):
  Splits dense reading sections into structured conceptual subsections without fragmenting reading comfort.

### 3. Worksheet Strategies (`app/quality/repair/strategies/worksheet.py`)
- **`WorksheetAntiSpoilingRepairStrategy`** (Class D, Priority 1, Cost 0.3):
  Enforces `withhold_explanation = True` across inquiry stages, strips premature explanatory answers from prediction prompts, and moves explanations to reflection phases.
- **`WorksheetInquirySequenceStrategy`** (Class D, Priority 1, Cost 0.25):
  Restores the canonical inquiry sequence: `PHENOMENON` $\to$ `PREDICTION` $\to$ `INVESTIGATION` $\to$ `OBSERVATION` $\to$ `DATA_ANALYSIS` $\to$ `REFLECTION`.
- **`WorksheetWorkspaceExpansionStrategy`** (Class A, Priority 1, Cost 0.15):
  Allocates generous student response workspaces (min 120pt) and prevents collapse into multiple-choice quizzes.

### 4. Scientific Document Strategies (`app/quality/repair/strategies/scientific.py`)
- **`ScientificEvidenceMappingStrategy`** (Class E, Priority 1, Cost 0.4):
  Links unmapped claims to verified source evidence units in the manifest.
- **`ScientificClaimDowngradeStrategy`** (Class E, Priority 2, Cost 0.6):
  Softens absolute unverified claims ("secara mutlak membuktikan" -> "berdasarkan pengamatan awal terindikasi bahwa"), changes role to `HYPOTHESIS`, and reduces confidence score without fabricating citations.
- **`ScientificLimitationIsolationStrategy`** (Class E, Priority 3, Cost 0.7):
  Isolates unresolved empirical assertions into Batasan Penelitian (`LIMITATION`).
- **`ScientificMethodologyOrderStrategy`** (Class D, Priority 1, Cost 0.25):
  Restores standard Indonesian KTI sequence (Bab I Pendahuluan to Bab V Kesimpulan).

---

## 6. Convergence Control, Rollback & Anti-Oscillation

1. **Snapshot Manager** (`app/quality/repair/rollback.py`):
   Creates lightweight, immutable, deep-copied blueprints with SHA-256 state hashes. Instant rollback on any detected regression.
2. **Regression Guard** (`app/quality/repair/regression_guard.py`):
   Verifies that the repair did not:
   - Introduce new hard blockers (Zero Tolerance).
   - Degrade quality score ($\Delta < -0.05$).
   - Break source knowledge traceability.
   - Violate format-specific invariants (e.g. anti-spoiling).
3. **Repair Oscillation Detector** (`app/quality/repair/convergence.py`):
   - **State Hash Recurrence**: Catches circular repair loops ($A \to B \to A$).
   - **Strategy Alternation**: Catches flipping between conflicting strategies.
   - **Stagnation**: Halts repair if two iterations yield zero score progression.
4. **Iteration Budget**:
   Strict upper limit of 3 iterations prevents runaway execution; unresolved documents cleanly route to `MANUAL_REVIEW_REQUIRED`.

---

## 7. Verification & Test Accounting

The entire Phase 3B repair subsystem is backed by **35 dedicated unit and integration tests**:

- `tests/unit/quality/repair/test_repair_contracts.py` (4 passed)
- `tests/unit/quality/repair/test_root_cause_analysis.py` (4 passed)
- `tests/unit/quality/repair/test_strategy_registry.py` (3 passed)
- `tests/unit/quality/repair/test_format_specific_repairs.py` (8 passed)
- `tests/unit/quality/repair/test_regression_guard.py` (4 passed)
- `tests/unit/quality/repair/test_oscillation.py` (3 passed)
- `tests/unit/quality/repair/test_convergence.py` (2 passed)
- `tests/integration/test_targeted_repair_pipeline.py` (7 passed)

**Full Quality Regression Suite**: **341 tests passing (100% Green)** across all quality evaluation, causal intelligence, rendered inspection, and repair pipeline modules.
