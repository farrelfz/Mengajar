# ITERATION CONTROLLER & MASTER LOOP
## BATCH 17 — ITERATIVE REFINEMENT & CLOSED-LOOP MATERIAL IMPROVEMENT

### 1. Master Refinement Loop (`app/refinement/controller.py`)
`IterativeRefinementController.refine()` manages the closed loop:
1. Evaluates Iteration 0 baseline.
2. Loops through Iteration $1 \dots N$ (default `max_iterations=3`).
3. Plans actions, executes localized patches, re-evaluates, checks invariants, tests convergence/oscillation, and updates audit history.
