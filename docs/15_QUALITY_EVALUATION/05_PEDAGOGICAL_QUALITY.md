# PEDAGOGICAL ALIGNMENT & SEQUENCING EVALUATION
## BATCH 15 — QUALITY EVALUATION & MATERIAL QUALITY ASSURANCE

### 1. Pedagogical Evaluator (`app/quality/pedagogical_evaluator.py`)
Consumes [`LearningJourney`](file:///home/si/Codingan/Mencari%20nafkah/Mengajar/app/director/contracts.py) and [`SemanticMaterialBlueprint`](file:///home/si/Codingan/Mencari%20nafkah/Mengajar/app/blueprints/contracts.py) to assess cognitive scaffolding.

### 2. Evaluated Pedagogical Invariants
1. **Worked-Example Placement**: Worked examples (`LearningStageType.WORKED_EXAMPLE`) must not precede concept formalization (`LearningStageType.CONCEPT_FORMALIZATION`). Doing so causes cognitive dissonance and triggers `QualitySeverity.ERROR`.
2. **Cognitive Hook Initiation**: For introductory or multi-stage educational materials, journeys should initiate with an engaging hook or prior-knowledge activation (`LearningStageType.HOOK`, `SURFACE_INTUITION`, `ACTIVATE_PRIOR_KNOWLEDGE`). Abrupt conceptual formalization without context triggers `QualitySeverity.WARNING`.
3. **Scaffolding Continuity**: Verifies that stages increase gradually in cognitive demand rather than jumping abruptly from recognition to complex evaluation.
