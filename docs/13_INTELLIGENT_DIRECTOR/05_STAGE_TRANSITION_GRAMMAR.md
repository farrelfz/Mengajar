# 05 — Stage Transition Grammar

## Validation Rules & Prohibitions

The `StageTransitionPolicy` enforces pedagogical syntax rules:

1. **Adjacent Redundancy**: Identical consecutive stages (e.g. `HOOK -> HOOK`) are flagged and pruned.
2. **Universal Incoherent Transitions**:
   - `SUMMARY -> HOOK`
   - `CALL_TO_ACTION -> INITIAL_INTRODUCTION`
   - `INDEPENDENT_PRACTICE -> BASIC_DEFINITION`
3. **Strategy-Specific Constraint Checking**:
   - In `MISCONCEPTION_CORRECTION`: `CONCEPT_FORMALIZATION` must not precede `MISCONCEPTION`.
   - In `WORKED_EXAMPLE_PROGRESSIVE`: `INDEPENDENT_PRACTICE` must not precede `WORKED_EXAMPLE`.
