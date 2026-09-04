# CRITIC CONTRACTS & DATA MODELS
## BATCH 16 — GENERATIVE CRITIC & EXPLAINABLE MATERIAL CRITIQUE

### 1. Enumerations
- `CritiquePerspective`: `STRUCTURAL`, `SEMANTIC`, `PEDAGOGICAL`, `COGNITIVE_LOAD`, `NARRATIVE`, `VISUAL_COMMUNICATION`, `SCIENTIFIC_RIGOR`, `AUDIENCE`, `REDUNDANCY`, `CAPABILITY_SELECTION`.
- `CritiqueSeverity`: `LOW`, `MEDIUM`, `HIGH`, `CRITICAL`.
- `CritiqueConfidence`: `LOW`, `MEDIUM`, `HIGH`, `CERTAIN`.
- `CritiquePriority`: `BLOCKER`, `CRITICAL`, `HIGH`, `MEDIUM`, `LOW`.
- `ImplementationScope`: `BLOCK`, `REGION`, `PAGE`, `SECTION`, `DOCUMENT`, `GLOBAL_PATTERN`.

---

### 2. Core Models (`app/critic/contracts.py`)
- **`CritiqueEvidence`**: Captures `source`, `location`, `observation`, `supporting_data`, and `confidence`.
- **`CritiqueFinding`**: Captures `id`, `perspective`, `title`, `observation`, `diagnosis`, `why_it_matters`, `evidence`, `severity`, `confidence`, `affected_locations`, and `improvement_direction`.
- **`CritiqueRecommendation`**: Captures `id`, `finding_ids`, `recommendation`, `rationale`, `expected_impact`, `implementation_scope`, and `priority`.
- **`CritiqueConflict`**: Surfaces design trade-offs between competing perspectives (`perspectives`, `competing_findings`, `synthesis_question`).
- **`CritiqueAgreement`**: Captures multi-perspective consensus on shared issues (`finding_ids`, `perspectives`, `shared_conclusion`, `agreement_strength`).
- **`CritiqueReport`**: Encapsulates `overall_assessment`, `findings`, `recommendations`, `conflicts`, `agreements`, `priority_queue`, and `trace`.
