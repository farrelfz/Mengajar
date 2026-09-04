# IMPROVEMENT EVALUATION & DELTA ANALYSIS
## BATCH 17 — ITERATIVE REFINEMENT & CLOSED-LOOP MATERIAL IMPROVEMENT

### 1. Dual Evaluation Engine (`app/refinement/evaluator.py`)
Each candidate artifact is re-evaluated using both:
1. `QualityEvaluationEngine` (Batch 15): Numerical scores ($0.0-1.0$).
2. `GenerativeCriticEngine` (Batch 16): Qualitative findings & perspective trace.

### 2. Comparator Metrics (`ImprovementComparator`)
- `quality_delta`: Score change ($\text{Candidate} - \text{Baseline}$).
- `resolved_finding_ids`: Diagnostics resolved by the patch.
- `persisting_finding_ids`: Diagnostics still present.
- `new_regressions`: New flaws introduced by the patch.
- `invariant_violations`: Invariant breaches detected.
