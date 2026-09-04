# CRITIC CONFLICTS & DESIGN TRADE-OFF SURFACING
## BATCH 16 — GENERATIVE CRITIC & EXPLAINABLE MATERIAL CRITIQUE

### 1. The Reality of Instructional Trade-Offs
Educational design involves inherent tensions:
- **Pedagogical Expansion**: Adding more detailed explanations, analogies, and practice steps to scaffold understanding.
- **Cognitive Load Minimization**: Reducing text volume and extraneous detail to avoid working memory saturation.

### 2. Conflict Preservation vs Arbitrary Resolution
Rather than silently picking a winner, `CritiqueSynthesizer` generates a typed `CritiqueConflict` model containing:
- Competing finding IDs
- Conflicting perspectives (`pedagogical` vs `cognitive_load`)
- A concrete `synthesis_question` framed for the future Batch 17 Refiner:
  > *"Should instructional scaffolding be expanded via additional explanatory text or achieved via multi-page chunking and non-textual representations?"*
