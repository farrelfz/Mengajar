# REFINEMENT OWNERSHIP RESOLUTION
## BATCH 17 — ITERATIVE REFINEMENT & CLOSED-LOOP MATERIAL IMPROVEMENT

### 1. Deterministic Ownership Mapping (`app/refinement/ownership.py`)
Rather than brittle if-else chains, `RefinementOwnershipResolver` uses typed dictionaries mapping finding dimensions and perspectives to architectural layers:

| Source Diagnostic Finding | Dimension / Perspective | Resolved Layer | Default Intent | Default Scope |
|---|---|---|---|---|
| Pedagogical Inversion | `PEDAGOGICAL_ALIGNMENT` | `DIRECTOR` | `REORDER` | `SECTION` |
| Text Density Overload | `COGNITIVE_LOAD` / `DENSITY` | `DENSITY` | `REBALANCE_DENSITY` | `PAGE` |
| Component Mismatch | `CAPABILITY_SELECTION` | `CAPABILITY_SELECTION` | `REPLACE_CAPABILITY` | `BLOCK` |
| Repeated Spans | `REDUNDANCY` | `COMPOSITION` | `REMOVE_REDUNDANCY` | `PAGE` |
| Vague Concept Definition | `SEMANTIC_CORRECTNESS` | `CONTENT` | `CLARIFY` | `BLOCK` |
| Format Dimension Breach | `FORMAT_INTEGRITY` | `FORMAT_METADATA` | `FIX_STRUCTURE` | `DOCUMENT` |
