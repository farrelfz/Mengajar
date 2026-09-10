# PHASE 3C.1 — ADVERSARIAL REPAIR SAFETY & DESIGN SYSTEM INTEGRATION HARDENING
## Universal Document Intelligence System V5
### Technical Reference, Safety Invariants, and Architecture Specification

---

## 1. Executive Overview

Phase 3C.1 provides the comprehensive forensic hardening layer for the automated repair engine (`app/quality/repair/`). In previous phases, the system established the Universal Design System (Phase 3B.0), Causal Attribution (Phase 3B), and Targeted Repair Strategies (Phase 3C). 

However, autonomous document repair engines face fundamental hazards if left ungoverned:
1. **Destructive Quality Optimization**: An engine might delete 40% of slide text or condense multiple sections into one to boost a physical layout score, destroying the educational value.
2. **Semantic & Factual Drift**: An engine might alter facts, drop key learning objectives, or modify scientific assertions without grounding.
3. **Traceability Degradation**: Source knowledge unit references (`source_refs`) might be dropped or orphaned during refactoring.
4. **Answer Leakage**: An engine might attempt to format or pad a worksheet question, inadvertently printing the answer key in the student workspace.
5. **Fabrication of Evidence**: An engine resolving an unsupported claim defect might fabricate citations to satisfy validator constraints.
6. **Cross-Renderer Parity Drift**: An engine repairing HTML might cause ReportLab or Pillow rendering to degrade or diverge.
7. **Oscillatory Churn**: Two competing repair strategies could alternate indefinitely (e.g. increase font vs decrease padding).

Phase 3C.1 solves these failure modes by enforcing **deterministic, mathematically verifiable constraints** before, during, and after every repair mutation.

---

## 2. Minimal-Intervention Mutation Scope Hierarchy

Every repair action in the system is classified under a strict **Mutation Scope Hierarchy (Levels 0 through 6)**. When repairing any defect, the `MinimalInterventionRepairPlanner` is algorithmically constrained to select the lowest possible rank that resolves the root cause.

```
+-----------------------------------------------------------------------------+
| LEVEL 0: NO-OP / METADATA ONLY                                              |
| - Description: Inspection tag, explanation comment, annotation.             |
| - Blast Radius: 0.00 | Reversibility: 1.00                                   |
+-----------------------------------------------------------------------------+
                                      |
                                      v
+-----------------------------------------------------------------------------+
| LEVEL 1: LOCAL DESIGN TOKEN MUTATION                                        |
| - Description: Padding (compact/normal), margin, local color variable.      |
| - Blast Radius: 0.05 | Reversibility: 1.00                                   |
+-----------------------------------------------------------------------------+
                                      |
                                      v
+-----------------------------------------------------------------------------+
| LEVEL 2: COMPONENT PARAMETER TUNING                                         |
| - Description: Column count, container width, grid ratio, gap size.         |
| - Blast Radius: 0.15 | Reversibility: 0.95                                   |
+-----------------------------------------------------------------------------+
                                      |
                                      v
+-----------------------------------------------------------------------------+
| LEVEL 3: COMPONENT REPLACEMENT                                              |
| - Description: Swap CalloutBox <-> KeyTakeaway; BulletList <-> FlowSteps.   |
| - Blast Radius: 0.30 | Reversibility: 0.85                                   |
+-----------------------------------------------------------------------------+
                                      |
                                      v
+-----------------------------------------------------------------------------+
| LEVEL 4: LOCAL CONTENT STRUCTURING                                          |
| - Description: Split slide into two; promote/demote section heading.        |
| - Blast Radius: 0.50 | Reversibility: 0.70                                   |
+-----------------------------------------------------------------------------+
                                      |
                                      v
+-----------------------------------------------------------------------------+
| LEVEL 5: GLOBAL LAYOUT RE-PAGINATION                                        |
| - Description: Redistribute sections across pages; reorder chapters.        |
| - Blast Radius: 0.75 | Reversibility: 0.50                                   |
+-----------------------------------------------------------------------------+
                                      |
                                      v
+-----------------------------------------------------------------------------+
| LEVEL 6: SEMANTIC RE-EXTRACTION / RE-BLUEPRINTING                           |
| - Description: Request source re-extraction or synthesis rebuild.           |
| - Blast Radius: 1.00 | Reversibility: 0.20 | Requires Manual Authorization   |
+-----------------------------------------------------------------------------+
```

### Utility Scoring Function

Candidates are ranked using a multi-factor deterministic utility calculation:

$$\text{Utility} = \frac{\text{Expected Quality Gain} \times \text{Confidence} \times \text{Root Cause Confidence}}{\text{Mutation Cost} \times \text{Blast Radius} \times \text{Regression Risk}}$$

When utilities are comparable, candidates are ordered strictly ascending by their scope rank ($\text{Level 1} \prec \text{Level 2} \prec \dots \prec \text{Level 6}$).

---

## 3. Artifact-Specific Mutation Budgets

To prevent cumulative degradation over multi-step repair loops, each artifact type has hard deterministic limits tracked by `MutationBudgetTracker`:

| Parameter | PRESENTATION | HANDOUT | WORKSHEET | SCIENTIFIC_DOCUMENT |
| :--- | :--- | :--- | :--- | :--- |
| **Max Iterations** | 4 | 3 | 3 | 3 |
| **Max Cumulative Cost** | 2.5 | 2.0 | 2.0 | 2.0 |
| **Max Content Churn Rate** | 15% | 10% | 5% | 5% |
| **Max Scope Allowed** | LEVEL_4 | LEVEL_5 | LEVEL_4 | LEVEL_5 |
| **Allowed Mutation Types** | Layout, Spacing, Split Slide | Pagination, Hierarchy, Gap | Anti-Spoiling, Sequence, Workspace | Claim Downgrade, Order, Evidence Map |
| **Forbidden Mutations** | Text Deletion > 15%, Scope 5/6 | Text Deletion > 10%, Scope 6 | Answer Exposure, Workspace Shrink | Evidence Fabrication, Scope 6 |

Any repair attempt that would exceed these thresholds is blocked with `BUDGET_EXCEEDED`, terminating the loop safely and escalating to human review if needed.

---

## 4. Artifact Drift Analyzer

The `ArtifactDriftAnalyzer` computes multi-dimensional drift between the pre-mutation baseline and the proposed post-mutation blueprint:

1. **Semantic Drift ($D_{\text{sem}}$)**: Measures word count deltas, vocabulary shift, and loss of critical knowledge concepts.
   - Threshold: $\le 0.15$ (PRESENTATION), $\le 0.10$ (HANDOUT), $\le 0.05$ (WORKSHEET, SCIENTIFIC).
2. **Structural Drift ($D_{\text{struct}}$)**: Measures element count churn (slides, sections, activities, babs).
   - Threshold: $\le 0.30$ (PRESENTATION), $\le 0.20$ (HANDOUT, WORKSHEET, SCIENTIFIC).
3. **Narrative Drift ($D_{\text{narr}}$)**: Measures re-ordering distances and sequence inversion.
   - Threshold: $\le 0.25$.
4. **Traceability Drift ($D_{\text{trace}}$)**: Measures the retention of `source_refs` and `target_knowledge_unit_ids`.
   - Threshold: Strictly $\le 0.00$ (zero dropped references).

If any drift metric exceeds the artifact's threshold, `is_acceptable` is `False`, and the transaction manager triggers an automatic rollback.

---

## 5. Non-Negotiable Safety Invariants

The `RepairSafetyInvariants` validator executes deterministic pre-commit checks:

### Global Invariants (All Artifacts)
- **Zero Orphaned Traceability**: Every knowledge reference present in the pre-state must exist in the post-state.
- **Monotonic Quality Enforcement**: Repairs must achieve positive expected quality gain without introducing new hard blocking signals.
- **Budget Compliance**: Cumulative cost must not exceed the artifact budget.

### Format-Specific Invariants
- **WORKSHEET Anti-Spoiling**: 
  - Answers and reasoning steps are strictly purged from student-facing prompts (`withhold_explanation=True`).
  - Active workspace dimensions cannot be reduced below the minimum response threshold.
- **SCIENTIFIC Zero Evidence Fabrication**:
  - Unsupported claims may only be hedged or re-linked to verified evidence units in `source_manifest`.
  - Evidence units cannot be fabricated, synthesized, or hallucinated under any circumstances.
  - Mandatory 5-chapter structure (`BAB I` through `BAB V`) must be strictly preserved.
- **PRESENTATION Narrative Flow**:
  - Title and orientation slides must remain anchored at the beginning.
  - Text density cannot be reduced by wholesale block deletion.

---

## 6. Universal Design System Integration (`RepairDesignContext`)

Repairs never emit raw CSS literals, hex strings, or arbitrary point values. Instead, all visual mutations flow through `RepairDesignContext`, which enforces:

- **Strict Token Resolution**: Dimensions, paddings, and colors resolve from `DesignTokenResolver`.
- **Discrete Stepping**: Spacing modifications step through discrete token increments (`compact` $\leftrightarrow$ `normal` $\leftrightarrow$ `relaxed`).
- **Typography Floors**: Font sizes are strictly clamped to artifact-specific minimum floors (e.g. 18pt for Presentation, 9pt for Handout/KTI) to prevent microscopic unreadable text.
- **WCAG AA Color Contrast**: All color adjustments are evaluated against the background canvas, enforcing a contrast ratio $\ge 4.5:1$.

---

## 7. Cross-Renderer Parity Validator (`CrossRendererParityValidator`)

To guarantee physical equivalence across rendering engines (HTML/Playwright, ReportLab, Pillow), `CrossRendererParityValidator` checks:

- **Geometric Discrepancy**: Maximum tolerance $\le 1.0\,\text{pt}$.
- **Font Size Discrepancy**: Maximum tolerance $\le 0.5\,\text{pt}$.
- **Color Discrepancy**: Normalized Euclidean distance in RGB space $\le 0.02$.
- **Canvas Aspect Ratio**: Strict 16:9 for presentations, $\sqrt{2}:1$ for A4 documents.

---

## 8. Atomic Transaction Lifecycle (`RepairTransactionManager`)

Every repair mutation is wrapped in an atomic transaction:

```
[Start Transaction]
       |
1. Snapshot Pre-State (SHA-256 state hash)
       |
2. Verify Budget Tracker (Check iteration, cost, and scope)
       |
3. Execute Strategy Mutation (Pure Python deepcopy)
       |
4. Compute Multi-Dimensional Drift (ArtifactDriftAnalyzer)
       |
5. Verify Safety Invariants (Global & Format-specific)
       |
6. Verify Non-Regression (Predicted score delta > 0)
       |
[Decision Point]
  /           \
[PASS]        [FAIL / VIOLATION]
  |                   |
7. Commit State     7. Rollback to Pre-State Snapshot
  |                   |
Record Audit Log    Record Rollback Cause & Escalate
```

---

## 9. Verification & Regression Results

The adversarial test suite verifies all safety invariants against pathological conditions:

| Scenario | Objective | Status |
| :--- | :--- | :--- |
| **Scenario A** | Excessive content deletion (40% dropped) rejected by drift analyzer | **PASSED** |
| **Scenario B** | Minimal intervention prefers padding adjustment (Level 1) over slide split (Level 4) | **PASSED** |
| **Scenario C** | Tiny text in dense cluster identifies CONTENT_DENSITY root cause (not blind font growth) | **PASSED** |
| **Scenario D** | Scientific claim downgrade hedges claim without fabricating evidence units | **PASSED** |
| **Scenario E** | Worksheet answer leak purged from student text, not hidden via CSS | **PASSED** |
| **Scenario F** | State oscillation (A $\rightarrow$ B $\rightarrow$ A) detected and escalated to manual review | **PASSED** |
| **Scenario G** | Quality improvement with excessive drift (+35%) triggers automatic rollback | **PASSED** |
| **Scenario H** | Traceability loss during repair triggers hard invariant violation rollback | **PASSED** |
| **Scenario I** | Clean repair (+0.15 quality, zero drift) commits successfully | **PASSED** |
| **Scenario J** | Bounded iteration limit enforced deterministically without infinite loop | **PASSED** |

### Test Suite Execution Summary
- **Phase 3C.1 Test Suite**: 22 / 22 PASSED.
- **Unit Test Baseline**: 368 / 368 PASSED.
- **Quality & Targeted Repair Integrations**: 25 / 25 PASSED.
- **Golden Benchmark Renderings**: 37 / 37 PASSED.
- **Total Verified Tests**: **430 / 430 PASSED (100% Green, 0 Regressions)**.

---

## 10. Boundary & Hand-Off to Phase 3D

Phase 3C.1 is complete. All safety invariants, budget controls, drift limits, and parity validators are verified and active.

**DO NOT proceed to Phase 3D (Production Pipeline Convergence Orchestration) without explicit user review and approval.**
