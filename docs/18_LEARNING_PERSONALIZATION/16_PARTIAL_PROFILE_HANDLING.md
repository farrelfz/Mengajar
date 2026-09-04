# PARTIAL PROFILE HANDLING & SAFE DEFAULTS
## BATCH 18 — LEARNING PERSONALIZATION & ADAPTIVE PEDAGOGICAL PROFILE SYSTEM

### 1. Incomplete Profile Resolution (`LearnerProfileBuilder`)
When a user provides only partial signals (e.g. `knowledge_level=NOVICE`), omitted dimensions are resolved deterministically:
- `prior_knowledge`: Set to `NONE` for novice, `BASIC` for intermediate.
- `cognitive_support`: Set to `HIGH_SUPPORT` for novice, `MODERATE` for intermediate.
- `abstraction_preference`: Set to `CONCRETE_FIRST` for novice, `CONCRETE_TO_ABSTRACT` for intermediate.
- No demographic or sensitive attributes are ever invented.
