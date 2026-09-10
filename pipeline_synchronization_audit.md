# Pipeline Synchronization & State Machine Forensic Audit

## 1. Executive Summary & Root Cause

The pipeline previously suffered from an **architectural state synchronization and convergence failure**.

### The Core Failure Mechanism
1. **Stale QA Authority**: When `PresentationQualityGate` evaluated artifacts in Task 9, a `QualityValidationReport` was generated. If failures were detected, `DeterministicRepairEngine` was invoked in Task 10. While the repair mutated internal layout properties and triggered an ad-hoc re-render, the pipeline lacked an authoritative state machine. The repair engine reported attempts rather than confirmed convergence, and no versioned round model existed.
2. **False Duplication Blowup in Gate 5 (60.6%)**: Gate 5 previously compared raw `slides[i].rendered_html` against `slides[j].rendered_html` using `SequenceMatcher`. In clean, minimalist slide layouts, HTML wrapper tags, CSS class names (`card`, `badge`, `layout-two-column`), and boilerplate DOM nodes comprise 85%+ of character strings. Comparing raw HTML caused template similarity to be misclassified as duplicate slides. Furthermore, duplicate pairs were normalized by dividing pair combinations by $N$, causing a mathematical scaling error.
3. **English Fallback Hallucination in Gate 11 (7 Unsupported Claims)**: When slides had short lists or punctuation-free procedural items, sentence splitting regex (`(?<=[.?!])\s+`) yielded empty claims. The fallback mechanism extracted English internal strings (`f"{s.title}: {s.purpose}"`), causing Indonesian technical text to be validated against English purpose phrases with 0% lexical grounding.
4. **Visual Grammar Matrix Taxonomy Divergence in Gate 16**: `SlideArchitect`, `SemanticLayoutValidator`, and `DeterministicRepairEngine` maintained isolated, competing layout dictionaries. Slides with narrative role `PROCESS` containing tabular data were marked as severe mismatches because `data_table` was excluded from the validator's local allowed list.
5. **Progress Logger Discrepancy**: Hardcoded `/5` counters in Branch B and `content_intelligence_agent.py` contradicted the 10-stage pipeline architecture.

---

## 2. Before vs After State Machine

### BEFORE (Unsynchronized & Ambiguous)
```
[Task 8: Render PDF]
         │
         ▼
[Task 9: Run QA] ──► [Report: 19/25, Score: 68.5%]
         │
         ▼
[Task 10: Repair Attempt]
         │ (5 CSS/tiny-text fixes performed)
         ▼
Log: "Loop perbaikan selesai: 5 perbaikan dilakukan"  <-- Confuses attempt with convergence!
         │
         ▼ (Gate 5, Gate 11, Gate 16 remained broken)
ERROR: Gate 5 Failed (60.6%), Gate 11 Failed (7 claims), Gate 16 Failed (5 slides)
[Export Blocked with Stale/Confusing Pipeline State]
```

### AFTER (Authoritative Deterministic State Machine)
```
[Task 8: Render PDF v1]
         │
         ▼
[Task 9: QA ROUND 1 (PDF v1)]
         │
         ├── Record in qa_history
         └── Set active_qa_result = Round 1
         │
         ▼
Has Repairable Failures?
   ├── NO  ──► Final Decision ──► [Export Check]
   └── YES ──► [Task 10: Convergence Loop] (Max 2 Iterations)
                    │
                    ├── 1. Execute targeted repairs (Attempted vs Successful)
                    ├── 2. Invalidate dependency graph:
                    │      Blueprint -> Composition -> HTML -> PDF -> QA
                    │      (active_qa_result = None)  <-- Invalidate stale QA!
                    ├── 3. Re-compose Document
                    ├── 4. Re-render PDF v2
                    ├── 5. QA ROUND 2 (PDF v2)
                    │      (active_qa_result = Round 2)
                    ├── 6. RepairConvergenceAnalyzer (score_delta, resolved, diverged?)
                    └── 7. QualityDecisionEngine (Authoritative Export Decision)
                                 │
                                 ├── BLOCKED (if critical failures persist)
                                 └── EXPORT_APPROVED / EXPORT_APPROVED_WITH_WARNINGS
                                       │
                                       ▼
                         Verify All 8 Final Invariants
```

---

## 3. Artifact Dependency Graph & Invalidation Topology

```
SOURCE (v1)
    │
    ▼
SEMANTIC IR (v1)
    │
    ▼
MANIFEST (v1)
    │
    ▼
BLUEPRINT (v1 -> v2 on repair)
    │
    ├─────────────────────────────┐
    ▼                             ▼
COMPOSITION (v1 -> v2)       HTML (v1 -> v2)
    │                             │
    └──────────────┬──────────────┘
                   ▼
               PDF (v1 -> v2)
                   │
                   ▼
              QA (v1 -> v2)
```

### Invalidation Invariant:
When `BLUEPRINT` mutates in Task 10:
- `COMPOSITION`, `HTML`, `PDF`, and `QA` versions are bumped.
- `pipeline_state.active_qa_result = None`.
- Old QA result from PDF v1 can **never** be used as final export evidence.

---

## 4. Quality Round History & Invariant Enforcement

### The 8 Strict State Invariants
1. `state.active_qa_result != None`: Active QA must exist.
2. `QA artifact version == final PDF artifact version`: Stale QA artifact versions are blocked.
3. `No CRITICAL_FAILURE gates`: All blocking gates must pass.
4. `No STALE gates`: Mismatched version gates are rejected.
5. `No NOT_EVALUATED critical gates`: Critical gates must have verified evaluations.
6. `Export decision derived from active QA only`: Decision matches `active_qa_result.round_id`.
7. `qa_history length >= 2 if repair occurred`: Repair must be verified by re-evaluation.
8. `Repair success evidenced by revalidation`: PDF version must be $\ge 2$ after repair.

---

## 5. Specific Gate Diagnoses

### Gate 5: Duplicate Slide Rate (60.6%)
- **Diagnostic Finding**: Raw HTML comparison included shared boilerplate tags (`<div class="card">`, `<span class="badge">`). In concise cards, 88% of tokens were HTML boilerplate.
- **Architectural Solution**: Built `DuplicateSlideAnalyzer`. It strips HTML and CSS scripts, computes text similarity on semantic tokens, evaluates information gain, and distinguishes:
  - Exact Duplicate
  - Near Textual Duplicate
  - Concept Progression
  - Intentional Continuity
  - Visual Template Similarity
  - True Redundant Slide
- Combined with `SlideDeduplicationPlanner` to merge source references into predecessor slides without losing critical content coverage.

### Gate 11: Unsupported Claims (7 Claims)
- **Diagnostic Finding**: Short procedural lines lacked terminal punctuation, causing sentence extraction to fall back to English `s.purpose` phrases against Indonesian text.
- **Architectural Solution**:
  - Enhanced sentence and bullet line extraction in `SlideArchitect`.
  - Fallback strictly uses Indonesian title and block text, never internal English purpose strings.
  - Added `ClaimProvenanceRepairer` to re-link ground truth provenance when source references were omitted.

### Gate 16: Semantic Layout Mismatch (5 Slides)
- **Diagnostic Finding**: `SlideArchitect` and `SemanticLayoutValidator` had disparate lists of allowed layouts for procedural roles (`PROCESS`).
- **Architectural Solution**: Created canonical `VISUAL_GRAMMAR_MATRIX` in `app/presentation/visual_grammar_registry.py` shared across Architect, Validator, and Repair Engine.
