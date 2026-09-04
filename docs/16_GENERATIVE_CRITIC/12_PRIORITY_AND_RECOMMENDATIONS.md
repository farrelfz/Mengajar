# PRIORITIZATION ENGINE & ACTIONABLE RECOMMENDATIONS
## BATCH 16 — GENERATIVE CRITIC & EXPLAINABLE MATERIAL CRITIQUE

### 1. Prioritization Mathematics (`app/critic/prioritization.py`)
Finding priority is computed via weighted ranking:
- Base severity rank (`CRITICAL` = 40, `HIGH` = 30, `MEDIUM` = 20, `LOW` = 10)
- Multi-perspective consensus boost (+5 if backed by an agreement cluster)
- Scope magnitude (number of affected locations)
- Deterministic ID tie-breaking

### 2. Actionable Non-Destructive Recommendations (`app/critic/recommendations.py`)
- Emits structured `CritiqueRecommendation` models with defined `ImplementationScope` (`BLOCK`, `PAGE`, `SECTION`, `GLOBAL_PATTERN`).
- Provides directional improvement advice without directly executing mutations on source models.
