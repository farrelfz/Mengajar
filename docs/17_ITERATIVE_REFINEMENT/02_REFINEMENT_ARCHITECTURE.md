# REFINEMENT ARCHITECTURE & CLOSED-LOOP WORKFLOW
## BATCH 17 — ITERATIVE REFINEMENT & CLOSED-LOOP MATERIAL IMPROVEMENT

### 1. Closed-Loop System Architecture
The Iterative Refinement subsystem (`app/refinement/`) closes the loop between diagnosis and production:

```text
                     ┌──────────────────────┐
                     │ Original Material    │
                     │ Artifact Version N   │
                     └──────────┬───────────┘
                                │
                                ▼
                     ┌──────────────────────┐
                     │ Quality Evaluation   │
                     │ (Batch 15)           │
                     └──────────┬───────────┘
                                │
                                ▼
                     ┌──────────────────────┐
                     │ Generative Critic    │
                     │ (Batch 16)           │
                     └──────────┬───────────┘
                                │
                        Diagnosed Findings
                                │
                                ▼
                  ┌──────────────────────────┐
                  │ Refinement Planner       │
                  │ (app/refinement/planner) │
                  │ Finding → Target Layer   │
                  │ Finding → Intent & Scope │
                  │ Risk & Invariant Bounds  │
                  └────────────┬─────────────┘
                               │
                               ▼
                  ┌──────────────────────────┐
                  │ Refinement Strategies    │
                  │ (app/refinement/strategy)│
                  │ Density / Pedagogical /  │
                  │ Capability / Redundancy  │
                  └────────────┬─────────────┘
                               │
                               ▼
                  ┌──────────────────────────┐
                  │ Patch Executor           │
                  │ (app/refinement/patches) │
                  │ Original + Patch         │
                  │   = Candidate Artifact   │
                  └────────────┬─────────────┘
                               │
                               ▼
                  ┌──────────────────────────┐
                  │ Invariant Checker        │
                  │ (app/refinement/invariants│
                  │ Semantic / Format Guard  │
                  └────────────┬─────────────┘
                               │
                               ▼
                  ┌──────────────────────────┐
                  │ Improvement Judge        │
                  │ (app/refinement/decision)│
                  │ Before vs After Delta    │
                  │ Regression & Oscillation │
                  └────────────┬─────────────┘
                               │
                   ┌───────────┼───────────┐
                   ▼           ▼           ▼
                ACCEPT       RETRY        STOP
```

---

### 2. Core Operational Invariants
- **Non-Destructive Localized Patches**: Avoids indiscriminate global document regeneration.
- **Strict Invariant Guard**: Immediately rejects any candidate where learning objectives, core concepts, or physical geometry are broken.
- **Convergence & Oscillation Detection**: Halts upon reaching score plateaus ($\Delta < 0.005$) or repeated state fingerprints.
