# REFINEMENT STRATEGIES CATALOG
## BATCH 17 — ITERATIVE REFINEMENT & CLOSED-LOOP MATERIAL IMPROVEMENT

### 1. Strategy Catalog (`app/refinement/strategies.py`)
- `PedagogicalRefinementStrategy`: Reorders stages to guarantee prerequisite scaffolding.
- `DensityRefinementStrategy`: Splits overloaded blocks across regions and pages.
- `CapabilityRefinementStrategy`: Replaces inappropriate component families with semantically matching ones.
- `RedundancyRefinementStrategy`: Deduplicates repeated text into summary callouts.
