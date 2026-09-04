# REFINEMENT CONTRACTS & TYPED DATA MODELS
## BATCH 17 — ITERATIVE REFINEMENT & CLOSED-LOOP MATERIAL IMPROVEMENT

### 1. Refinement Enums (`app/refinement/contracts.py`)
- `RefinementStage`: `ANALYSIS`, `PLANNING`, `PATCH_GENERATION`, `CANDIDATE_EVALUATION`, `COMPARISON`, `DECISION`, `CONVERGENCE_CHECK`, `COMPLETE`, `STOPPED`.
- `RefinementTargetLayer`: `BLUEPRINT`, `DIRECTOR`, `CAPABILITY_SELECTION`, `COMPOSITION`, `CONTENT`, `DENSITY`, `VISUAL_STRUCTURE`, `FORMAT_METADATA`.
- `RefinementScope`: `TOKEN`, `BLOCK`, `REGION`, `PAGE`, `SECTION`, `DOCUMENT`.
- `RefinementIntent`: `REORDER`, `CLARIFY`, `SIMPLIFY`, `EXPAND`, `CONDENSE`, `REPLACE_CAPABILITY`, `REMOVE_REDUNDANCY`, `ADD_SCAFFOLDING`, `REBALANCE_DENSITY`, `IMPROVE_TRANSITION`, `STRENGTHEN_EVIDENCE`, `FIX_STRUCTURE`.
- `ImprovementDecision`: `ACCEPT`, `REJECT`, `RETRY`, `STOP_CONVERGED`, `STOP_MAX_ITERATIONS`, `STOP_OSCILLATION`, `STOP_RISK`, `STOP_NO_IMPROVEMENT`.
- `InvariantCategory`: `SEMANTIC_INVARIANT`, `PEDAGOGICAL_INVARIANT`, `STRUCTURAL_INVARIANT`, `FORMAT_INVARIANT`, `CONTENT_PRESERVATION_INVARIANT`, `TRACE_INVARIANT`.

---

### 2. Core Models
- `RefinementAction`: Encapsulates `action_id`, `source_finding_ids`, `target_layer`, `target_scope`, `target_identifier`, `intent`, `rationale`, `expected_benefit`, `estimated_risk`, `constraints`, and `preservation_requirements`.
- `RefinementPlan`: Encapsulates `plan_id`, `source_artifact_id`, `iteration`, `actions`, `invariants`, `expected_improvement`, `risk_summary`, and `trace`.
- `RefinementPatch`: Encapsulates localized modification before/after states.
- `RefinedArtifactBundle`: Bundles multi-layer representations (`blueprint`, `composition`, `journey`, `target_format`).
- `ImprovementComparison`: Compares before-and-after scores, resolved findings, persisting findings, new regressions, and invariant violations.
